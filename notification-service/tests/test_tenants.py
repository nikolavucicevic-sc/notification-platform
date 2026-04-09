import pytest
from uuid import uuid4
from unittest.mock import MagicMock

from app.models.user import User, UserRole
from app.auth import get_current_user, require_super_admin
from app.database import get_db
from app.main import app
import app.main as app_main
from app.database import Base
from tests.conftest import engine, TestingSessionLocal


def make_super_admin():
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.username = "super_admin"
    user.email = "super@bemby.app"
    user.role = UserRole.SUPER_ADMIN
    user.is_active = True
    user.tenant_id = None
    return user


@pytest.fixture()
def super_admin_client():
    import asyncio
    from fastapi.testclient import TestClient

    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    super_admin = make_super_admin()

    def override_get_db():
        try:
            yield session
        finally:
            pass

    def override_get_current_user():
        return super_admin

    def override_require_super_admin():
        return super_admin

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[require_super_admin] = override_require_super_admin

    app_main.shutdown_event = asyncio.Event()
    app_main.shutdown_event.set()

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
    session.close()
    Base.metadata.drop_all(bind=engine)


class TestTenantCreation:

    def test_create_tenant_success(self, super_admin_client):
        """POST /tenants creates a new tenant and returns 201."""
        unique = str(uuid4())[:8]
        payload = {
            "name": f"Test Corp {unique}",
            "email_limit": 1000,
            "sms_limit": 500,
            "admin_username": f"admin_{unique}",
            "admin_email": f"admin_{unique}@testcorp.com",
            "admin_password": "SecurePass1!",
            "admin_full_name": "Test Admin"
        }

        response = super_admin_client.post("/tenants", json=payload)

        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["email_limit"] == 1000
        assert data["sms_limit"] == 500
        assert data["is_active"] is True
        assert "id" in data
        assert data["user_count"] == 1

    def test_create_tenant_no_trailing_slash(self, super_admin_client):
        """POST /tenants (no trailing slash) must NOT redirect to GET — returns 201 directly."""
        unique = str(uuid4())[:8]
        payload = {
            "name": f"NoSlash Corp {unique}",
            "email_limit": None,
            "sms_limit": None,
            "admin_username": f"noslash_{unique}",
            "admin_email": f"noslash_{unique}@corp.com",
            "admin_password": "SecurePass1!",
        }

        # allow_redirects=False to catch any accidental redirect
        response = super_admin_client.post("/tenants", json=payload, allow_redirects=False)

        assert response.status_code == 201, (
            f"Expected 201, got {response.status_code} — "
            f"redirect_slashes may still be enabled: {response.text}"
        )

    def test_create_tenant_duplicate_name(self, super_admin_client):
        """Creating two tenants with the same name returns 400."""
        unique = str(uuid4())[:8]
        payload = {
            "name": f"Dup Corp {unique}",
            "admin_username": f"dup1_{unique}",
            "admin_email": f"dup1_{unique}@corp.com",
            "admin_password": "SecurePass1!",
        }
        super_admin_client.post("/tenants", json=payload)

        payload2 = {**payload, "admin_username": f"dup2_{unique}", "admin_email": f"dup2_{unique}@corp.com"}
        response = super_admin_client.post("/tenants", json=payload2)

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_tenant_duplicate_username(self, super_admin_client):
        """Creating two tenants with the same admin username returns 400."""
        unique = str(uuid4())[:8]
        base_payload = {
            "admin_username": f"shared_{unique}",
            "admin_password": "SecurePass1!",
        }
        super_admin_client.post("/tenants", json={
            **base_payload,
            "name": f"Corp A {unique}",
            "admin_email": f"a_{unique}@corp.com",
        })

        response = super_admin_client.post("/tenants", json={
            **base_payload,
            "name": f"Corp B {unique}",
            "admin_email": f"b_{unique}@corp.com",
        })

        assert response.status_code == 400
        assert "Username already taken" in response.json()["detail"]

    def test_list_tenants(self, super_admin_client):
        """GET /tenants returns a list."""
        response = super_admin_client.get("/tenants")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_tenant_missing_required_fields(self, super_admin_client):
        """Missing required fields returns 422."""
        response = super_admin_client.post("/tenants", json={"name": "Incomplete"})
        assert response.status_code == 422
