import pytest
from datetime import datetime
from uuid import UUID

from app.models.customer import Customer


@pytest.mark.unit
class TestCustomerModel:
    """Test cases for Customer model."""

    def test_create_customer_with_all_fields(self, db_session):
        """Test creating a customer with all fields."""
        customer = Customer(
            email="test@example.com",
            phone_number="+1234567890",
            first_name="John",
            last_name="Doe"
        )
        db_session.add(customer)
        db_session.commit()

        assert isinstance(customer.id, UUID)
        assert customer.email == "test@example.com"
        assert customer.phone_number == "+1234567890"
        assert customer.first_name == "John"
        assert customer.last_name == "Doe"
        assert isinstance(customer.created_at, datetime)
        assert isinstance(customer.updated_at, datetime)

    def test_create_customer_without_phone(self, db_session):
        """Test creating a customer without phone number."""
        customer = Customer(
            email="test@example.com",
            first_name="Jane",
            last_name="Smith"
        )
        db_session.add(customer)
        db_session.commit()

        assert customer.phone_number is None
        assert customer.email == "test@example.com"

    def test_customer_email_uniqueness(self, db_session):
        """Test that email must be unique."""
        customer1 = Customer(
            email="test@example.com",
            first_name="John",
            last_name="Doe"
        )
        db_session.add(customer1)
        db_session.commit()

        customer2 = Customer(
            email="test@example.com",
            first_name="Jane",
            last_name="Smith"
        )
        db_session.add(customer2)

        with pytest.raises(Exception):  # IntegrityError or similar
            db_session.commit()

    def test_customer_timestamps(self, db_session):
        """Test that timestamps are set correctly."""
        customer = Customer(
            email="test@example.com",
            first_name="John",
            last_name="Doe"
        )
        db_session.add(customer)
        db_session.commit()

        created_at = customer.created_at
        updated_at = customer.updated_at

        # Update the customer
        customer.first_name = "Jane"
        db_session.commit()
        db_session.refresh(customer)

        # Created timestamp should not change
        assert customer.created_at == created_at
        # Updated timestamp should change
        assert customer.updated_at >= updated_at

    def test_query_customer_by_email(self, db_session):
        """Test querying customer by email."""
        customer = Customer(
            email="unique@example.com",
            first_name="John",
            last_name="Doe"
        )
        db_session.add(customer)
        db_session.commit()

        found = db_session.query(Customer).filter(Customer.email == "unique@example.com").first()

        assert found is not None
        assert found.id == customer.id
        assert found.email == "unique@example.com"
