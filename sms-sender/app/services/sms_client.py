"""
SMS client for sending SMS messages via external SMS API.
Supports WireMock (mock) and Twilio (real) providers, controlled by SMS_PROVIDER env var.
"""
import requests
from app.config import settings


async def send_sms(customer_id: str, body: str) -> dict:
    if settings.sms_provider == "twilio":
        return await _send_via_twilio(customer_id, body)
    return await _send_via_wiremock(customer_id, body)


def _fetch_customer(customer_id: str) -> dict:
    """Fetch customer details from customer-service."""
    customer_url = f"{settings.customer_service_url}/customers/{customer_id}"
    customer_response = requests.get(customer_url, timeout=5)
    customer_response.raise_for_status()
    return customer_response.json()


async def _send_via_wiremock(customer_id: str, body: str) -> dict:
    # Step 1: Get customer details from customer-service
    try:
        customer = _fetch_customer(customer_id)
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to fetch customer {customer_id}: {e}")
        raise Exception(f"Customer not found: {customer_id}")

    phone_number = customer.get("phone_number")
    if not phone_number:
        print(f"✗ Customer {customer_id} has no phone number")
        raise Exception(f"Customer {customer_id} has no phone number")

    # Step 2: Send SMS via WireMock
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


async def _send_via_twilio(customer_id: str, body: str) -> dict:
    """
    Send SMS via Twilio REST API.
    Requires TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_FROM_NUMBER to be set.
    """
    # Step 1: Get customer details from customer-service
    try:
        customer = _fetch_customer(customer_id)
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to fetch customer {customer_id}: {e}")
        raise Exception(f"Customer not found: {customer_id}")

    phone_number = customer.get("phone_number")
    if not phone_number:
        print(f"✗ Customer {customer_id} has no phone number")
        raise Exception(f"Customer {customer_id} has no phone number")

    # Step 2: Send SMS via Twilio
    twilio_url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_account_sid}/Messages.json"

    try:
        sms_response = requests.post(
            twilio_url,
            auth=(settings.twilio_account_sid, settings.twilio_auth_token),
            data={
                "From": settings.twilio_from_number,
                "To": phone_number,
                "Body": body
            },
            timeout=10
        )
        sms_response.raise_for_status()

        result = sms_response.json()
        print(f"✓ Twilio SMS sent to {phone_number} for customer {customer_id}, SID: {result.get('sid')}")

        return {
            "status": "sent",
            "customer_id": customer_id,
            "phone_number": phone_number,
            "message": body[:50] + "..." if len(body) > 50 else body,
            "twilio_sid": result.get("sid")
        }

    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to send Twilio SMS to {phone_number}: {e}")
        raise Exception(f"SMS sending failed: {str(e)}")
