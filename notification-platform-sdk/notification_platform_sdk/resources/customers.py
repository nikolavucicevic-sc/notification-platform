"""
Customers API resource.
"""

from typing import List, Optional, Dict, Any


class CustomersResource:
    """Handles customer-related API operations."""

    def __init__(self, client):
        """
        Initialize the customers resource.

        Args:
            client: BaseClient instance
        """
        self._client = client

    def create(
        self,
        email: str,
        phone: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new customer.

        Args:
            email: Customer's email address (required)
            phone: Customer's phone number in E.164 format (optional)
            first_name: Customer's first name (optional)
            last_name: Customer's last name (optional)
            preferences: Notification preferences (optional)
            metadata: Additional metadata (optional)

        Returns:
            Created customer object

        Example:
            >>> customer = client.customers.create(
            ...     email="john@example.com",
            ...     phone="+1234567890",
            ...     first_name="John",
            ...     last_name="Doe",
            ...     preferences={"email": True, "sms": True},
            ...     metadata={"plan": "premium"}
            ... )
        """
        data = {"email": email}
        if phone is not None:
            data["phone"] = phone
        if first_name is not None:
            data["first_name"] = first_name
        if last_name is not None:
            data["last_name"] = last_name
        if preferences is not None:
            data["preferences"] = preferences
        if metadata is not None:
            data["metadata"] = metadata

        return self._client.post("/api/customers/", json=data)

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        List customers with pagination.

        Args:
            skip: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 100)

        Returns:
            List of customer objects

        Example:
            >>> customers = client.customers.list(skip=0, limit=50)
            >>> for customer in customers:
            ...     print(customer["email"])
        """
        params = {"skip": skip, "limit": limit}
        return self._client.get("/api/customers/", params=params)

    def get(self, customer_id: str) -> Dict[str, Any]:
        """
        Get a specific customer by ID.

        Args:
            customer_id: The customer's unique identifier

        Returns:
            Customer object

        Example:
            >>> customer = client.customers.get("123e4567-e89b-12d3-a456-426614174000")
            >>> print(customer["email"])
        """
        return self._client.get(f"/api/customers/{customer_id}")

    def update(
        self,
        customer_id: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update a customer's information.

        Args:
            customer_id: The customer's unique identifier
            email: Customer's email address (optional)
            phone: Customer's phone number in E.164 format (optional)
            first_name: Customer's first name (optional)
            last_name: Customer's last name (optional)
            preferences: Notification preferences (optional)
            metadata: Additional metadata (optional)

        Returns:
            Updated customer object

        Example:
            >>> customer = client.customers.update(
            ...     "123e4567-e89b-12d3-a456-426614174000",
            ...     first_name="Jane",
            ...     preferences={"email": True, "sms": False}
            ... )
        """
        data = {}
        if email is not None:
            data["email"] = email
        if phone is not None:
            data["phone"] = phone
        if first_name is not None:
            data["first_name"] = first_name
        if last_name is not None:
            data["last_name"] = last_name
        if preferences is not None:
            data["preferences"] = preferences
        if metadata is not None:
            data["metadata"] = metadata

        return self._client.put(f"/api/customers/{customer_id}", json=data)

    def delete(self, customer_id: str) -> None:
        """
        Delete a customer.

        Args:
            customer_id: The customer's unique identifier

        Returns:
            None

        Example:
            >>> client.customers.delete("123e4567-e89b-12d3-a456-426614174000")
        """
        return self._client.delete(f"/api/customers/{customer_id}")

    def get_by_email(self, email: str) -> Dict[str, Any]:
        """
        Get a customer by email address.

        Args:
            email: The customer's email address

        Returns:
            Customer object

        Example:
            >>> customer = client.customers.get_by_email("john@example.com")
            >>> print(customer["id"])
        """
        return self._client.get(f"/api/customers/email/{email}")
