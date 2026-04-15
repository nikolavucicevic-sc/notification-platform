import httpx
from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)


async def send_email(customer_id: str, subject: str, body: str, tenant_config: dict | None = None) -> dict:
    if settings.email_provider == "brevo":
        return await _send_via_brevo(customer_id, subject, body, tenant_config or {})
    return await _send_via_wiremock(customer_id, subject, body)


async def _send_via_wiremock(customer_id: str, subject: str, body: str) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.wiremock_url}/send-email",
                json={"customer_id": customer_id, "subject": subject, "body": body}
            )
            success = response.status_code == 200
            logger.info(
                "wiremock_email_sent",
                customer_id=customer_id,
                success=success,
                status_code=response.status_code
            )
            return {"customer_id": customer_id, "success": success, "status_code": response.status_code}
        except Exception as e:
            logger.error("wiremock_email_failed", customer_id=customer_id, error=str(e))
            return {"customer_id": customer_id, "success": False, "error": str(e)}


async def _send_via_brevo(customer_id: str, subject: str, body: str, tenant_config: dict) -> dict:
    """
    Send email via Brevo (formerly Sendinblue) API.
    Requires BREVO_API_KEY and BREVO_FROM_EMAIL to be set.
    The recipient email is fetched from the customer-service.
    tenant_config may contain display_name and reply_to_email for per-tenant branding.
    """
    async with httpx.AsyncClient() as client:
        # Fetch customer email from customer-service
        try:
            customer_response = await client.get(
                f"{settings.customer_service_url}/customers/{customer_id}",
                timeout=5
            )
            customer_response.raise_for_status()
            customer = customer_response.json()
        except Exception as e:
            logger.error("customer_fetch_failed", customer_id=customer_id, error=str(e))
            return {"customer_id": customer_id, "success": False, "error": str(e)}

        to_email = customer.get("email")
        if not to_email:
            logger.warning("customer_no_email", customer_id=customer_id)
            return {"customer_id": customer_id, "success": False, "error": "Customer has no email address"}

        sender = {"email": settings.brevo_from_email}
        if tenant_config.get("display_name"):
            sender["name"] = tenant_config["display_name"]

        payload = {
            "sender": sender,
            "to": [{"email": to_email}],
            "subject": subject,
            "textContent": body,
        }
        if tenant_config.get("reply_to_email"):
            payload["replyTo"] = {"email": tenant_config["reply_to_email"]}

        try:
            response = await client.post(
                "https://api.brevo.com/v3/smtp/email",
                headers={
                    "api-key": settings.brevo_api_key,
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=10
            )
            # Brevo returns 201 Created on success
            success = response.status_code == 201
            logger.info(
                "brevo_email_sent",
                customer_id=customer_id,
                to_email=to_email,
                success=success,
                status_code=response.status_code
            )
            return {"customer_id": customer_id, "success": success, "status_code": response.status_code}
        except Exception as e:
            logger.error("brevo_email_failed", customer_id=customer_id, to_email=to_email, error=str(e))
            return {"customer_id": customer_id, "success": False, "error": str(e)}
