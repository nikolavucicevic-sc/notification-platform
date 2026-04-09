"""
SMS client for sending SMS messages via external SMS API.
Supports WireMock (mock) and Twilio (real) providers, controlled by SMS_PROVIDER env var.
"""
import requests
from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)


async def send_sms(customer_id: str, body: str) -> dict:
    if settings.sms_provider == "twilio":
        return await _send_via_twilio(customer_id, body)
    return await _send_via_wiremock(customer_id, body)


def _fetch_customer(customer_id: str) -> dict:
    customer_url = f"{settings.customer_service_url}/customers/{customer_id}"
    customer_response = requests.get(customer_url, timeout=5)
    customer_response.raise_for_status()
    return customer_response.json()


async def _send_via_wiremock(customer_id: str, body: str) -> dict:
    try:
        customer = _fetch_customer(customer_id)
    except requests.exceptions.RequestException as e:
        logger.error("customer_fetch_failed", customer_id=customer_id, error=str(e))
        raise Exception(f"Customer not found: {customer_id}")

    phone_number = customer.get("phone_number")
    if not phone_number:
        logger.warning("customer_no_phone", customer_id=customer_id)
        raise Exception(f"Customer {customer_id} has no phone number")

    try:
        sms_response = requests.post(
            settings.sms_api_url,
            json={"to": phone_number, "message": body, "customer_id": customer_id},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        sms_response.raise_for_status()
        logger.info("wiremock_sms_sent", customer_id=customer_id, phone_number=phone_number)
        return {
            "status": "sent",
            "customer_id": customer_id,
            "phone_number": phone_number,
            "message": body[:50] + "..." if len(body) > 50 else body
        }
    except requests.exceptions.RequestException as e:
        logger.error("wiremock_sms_failed", customer_id=customer_id, phone_number=phone_number, error=str(e))
        raise Exception(f"SMS sending failed: {str(e)}")


async def _send_via_twilio(customer_id: str, body: str) -> dict:
    try:
        customer = _fetch_customer(customer_id)
    except requests.exceptions.RequestException as e:
        logger.error("customer_fetch_failed", customer_id=customer_id, error=str(e))
        raise Exception(f"Customer not found: {customer_id}")

    phone_number = customer.get("phone_number")
    if not phone_number:
        logger.warning("customer_no_phone", customer_id=customer_id)
        raise Exception(f"Customer {customer_id} has no phone number")

    twilio_url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_account_sid}/Messages.json"

    try:
        sms_response = requests.post(
            twilio_url,
            auth=(settings.twilio_account_sid, settings.twilio_auth_token),
            data={"From": settings.twilio_from_number, "To": phone_number, "Body": body},
            timeout=10
        )
        sms_response.raise_for_status()
        result = sms_response.json()
        logger.info(
            "twilio_sms_sent",
            customer_id=customer_id,
            phone_number=phone_number,
            twilio_sid=result.get("sid")
        )
        return {
            "status": "sent",
            "customer_id": customer_id,
            "phone_number": phone_number,
            "message": body[:50] + "..." if len(body) > 50 else body,
            "twilio_sid": result.get("sid")
        }
    except requests.exceptions.RequestException as e:
        logger.error("twilio_sms_failed", customer_id=customer_id, phone_number=phone_number, error=str(e))
        raise Exception(f"SMS sending failed: {str(e)}")
