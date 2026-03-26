"""
Script to create the initial admin user.
Run this once after deployment to create your first admin account.

Usage:
    python create_admin.py
"""
from app.database import SessionLocal
from app.models import User, UserRole
from app.auth import get_password_hash
import sys


def create_admin_user():
    """Create the default admin user."""
    db = SessionLocal()

    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("❌ Admin user already exists!")
            print(f"   Username: {existing_admin.username}")
            print(f"   Email: {existing_admin.email}")
            return

        # Create admin user
        password = "admin123"
        hashed_password = get_password_hash(password)

        admin = User(
            email="admin@notification-platform.com",
            username="admin",
            hashed_password=hashed_password,
            full_name="System Administrator",
            role=UserRole.ADMIN,
            is_active=True
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("✅ Admin user created successfully!")
        print()
        print("📧 Email:    admin@notification-platform.com")
        print("👤 Username: admin")
        print("🔑 Password: admin123")
        print()
        print("⚠️  IMPORTANT: Change this password immediately after first login!")
        print()
        print("To login, send a POST request to /auth/login with:")
        print('  {"username": "admin", "password": "admin123"}')

    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()
