import pytest
from uuid import uuid4


@pytest.mark.api
class TestCreateCustomer:
    """Test cases for creating customers."""

    def test_create_customer_success(self, client, sample_customer_data):
        """Test successful customer creation."""
        response = client.post("/customers/", json=sample_customer_data)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == sample_customer_data["email"]
        assert data["first_name"] == sample_customer_data["first_name"]
        assert data["last_name"] == sample_customer_data["last_name"]
        assert data["phone_number"] == sample_customer_data["phone_number"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_customer_without_phone(self, client, sample_customer_data_no_phone):
        """Test customer creation without phone number."""
        response = client.post("/customers/", json=sample_customer_data_no_phone)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == sample_customer_data_no_phone["email"]
        assert data["phone_number"] is None

    def test_create_customer_duplicate_email(self, client, sample_customer_data):
        """Test that duplicate email addresses are rejected."""
        # Create first customer
        client.post("/customers/", json=sample_customer_data)

        # Try to create second customer with same email
        response = client.post("/customers/", json=sample_customer_data)

        assert response.status_code == 400
        assert "Email already exists" in response.json()["detail"]

    def test_create_customer_missing_required_fields(self, client):
        """Test that missing required fields return validation error."""
        incomplete_data = {"email": "test@example.com"}
        response = client.post("/customers/", json=incomplete_data)

        assert response.status_code == 422


@pytest.mark.api
class TestGetCustomers:
    """Test cases for retrieving customers."""

    def test_get_customers_empty(self, client):
        """Test getting customers when none exist."""
        response = client.get("/customers/")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_customers_multiple(self, client, sample_customer_data, sample_customer_data_no_phone):
        """Test getting multiple customers."""
        # Create two customers
        client.post("/customers/", json=sample_customer_data)
        client.post("/customers/", json=sample_customer_data_no_phone)

        response = client.get("/customers/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


@pytest.mark.api
class TestGetCustomer:
    """Test cases for retrieving a single customer."""

    def test_get_customer_success(self, client, sample_customer_data):
        """Test successfully retrieving a customer by ID."""
        # Create a customer
        create_response = client.post("/customers/", json=sample_customer_data)
        customer_id = create_response.json()["id"]

        # Retrieve the customer
        response = client.get(f"/customers/{customer_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == customer_id
        assert data["email"] == sample_customer_data["email"]

    def test_get_customer_not_found(self, client):
        """Test retrieving a non-existent customer."""
        fake_id = str(uuid4())
        response = client.get(f"/customers/{fake_id}")

        assert response.status_code == 404
        assert "Customer not found" in response.json()["detail"]

    def test_get_customer_invalid_uuid(self, client):
        """Test with invalid UUID format."""
        response = client.get("/customers/invalid-uuid")

        assert response.status_code == 422


@pytest.mark.api
class TestUpdateCustomer:
    """Test cases for updating customers."""

    def test_update_customer_all_fields(self, client, sample_customer_data):
        """Test updating all customer fields."""
        # Create a customer
        create_response = client.post("/customers/", json=sample_customer_data)
        customer_id = create_response.json()["id"]

        # Update all fields
        update_data = {
            "email": "updated@example.com",
            "phone_number": "+9876543210",
            "first_name": "UpdatedFirst",
            "last_name": "UpdatedLast"
        }
        response = client.put(f"/customers/{customer_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == update_data["email"]
        assert data["phone_number"] == update_data["phone_number"]
        assert data["first_name"] == update_data["first_name"]
        assert data["last_name"] == update_data["last_name"]

    def test_update_customer_partial(self, client, sample_customer_data):
        """Test partial update of customer."""
        # Create a customer
        create_response = client.post("/customers/", json=sample_customer_data)
        customer_id = create_response.json()["id"]
        original_email = create_response.json()["email"]

        # Update only first name
        update_data = {"first_name": "NewFirstName"}
        response = client.put(f"/customers/{customer_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "NewFirstName"
        assert data["email"] == original_email  # Should remain unchanged

    def test_update_customer_not_found(self, client):
        """Test updating a non-existent customer."""
        fake_id = str(uuid4())
        update_data = {"first_name": "Test"}
        response = client.put(f"/customers/{fake_id}", json=update_data)

        assert response.status_code == 404
        assert "Customer not found" in response.json()["detail"]


@pytest.mark.api
class TestDeleteCustomer:
    """Test cases for deleting customers."""

    def test_delete_customer_success(self, client, sample_customer_data):
        """Test successfully deleting a customer."""
        # Create a customer
        create_response = client.post("/customers/", json=sample_customer_data)
        customer_id = create_response.json()["id"]

        # Delete the customer
        response = client.delete(f"/customers/{customer_id}")

        assert response.status_code == 204

        # Verify customer is deleted
        get_response = client.get(f"/customers/{customer_id}")
        assert get_response.status_code == 404

    def test_delete_customer_not_found(self, client):
        """Test deleting a non-existent customer."""
        fake_id = str(uuid4())
        response = client.delete(f"/customers/{fake_id}")

        assert response.status_code == 404
        assert "Customer not found" in response.json()["detail"]


@pytest.mark.api
class TestHealthCheck:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint returns OK."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
