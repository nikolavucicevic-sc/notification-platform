"""
SMS client for sending SMS messages via external SMS API.
Uses WireMock to mock the SMS gateway in development.
"""
import requests
from app.config import settings


async def send_sms(customer_id: str, body: str) -> dict:
    """
    Send an SMS to a customer via external SMS API.

    Args:
        customer_id: UUID of the customer
        body: SMS message text

    Returns:
        dict with status information

    Raises:
        Exception: If customer not found or SMS sending fails
    """
    # Step 1: Get customer details from customer-service
    customer_url = f"{settings.customer_service_url}/customers/{customer_id}"

    try:
        customer_response = requests.get(customer_url, timeout=5)
        customer_response.raise_for_status()
        customer = customer_response.json()
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to fetch customer {customer_id}: {e}")
        raise Exception(f"Customer not found: {customer_id}")

    # Validate phone number exists
    phone_number = customer.get("phone_number")
    if not phone_number:
        print(f"✗ Customer {customer_id} has no phone number")
        raise Exception(f"Customer {customer_id} has no phone number")

    # Step 2: Send SMS via external SMS API (mocked with WireMock)
    sms_payload = {
        "to": phone_number,
        "message": body,
        "customer_id": customer_id
    }

    try:
        sms_response = requests.post(
            settings.sms_api_url,
            json=sms_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        sms_response.raise_for_status()

        print(f"✓ SMS sent to {phone_number} for customer {customer_id}")

        return {
            "status": "sent",
            "customer_id": customer_id,
            "phone_number": phone_number,
            "message": body[:50] + "..." if len(body) > 50 else body
        }

    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to send SMS to {phone_number}: {e}")
        raise Exception(f"SMS sending failed: {str(e)}")
