import httpx
from app.config import settings


async def send_email(customer_id: str, subject: str, body: str) -> dict:
    if settings.email_provider == "sendgrid":
        return await _send_via_sendgrid(customer_id, subject, body)
    return await _send_via_wiremock(customer_id, subject, body)


async def _send_via_wiremock(customer_id: str, subject: str, body: str) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.wiremock_url}/send-email",
                json={
                    "customer_id": customer_id,
                    "subject": subject,
                    "body": body
                }
            )
            success = response.status_code == 200
            return {
                "customer_id": customer_id,
                "success": success,
                "status_code": response.status_code
            }
        except Exception as e:
            print(f"Failed to send email to customer {customer_id}: {e}")
            return {
                "customer_id": customer_id,
                "success": False,
                "error": str(e)
            }


async def _send_via_sendgrid(customer_id: str, subject: str, body: str) -> dict:
    """
    Send email via SendGrid API.
    Requires SENDGRID_API_KEY and SENDGRID_FROM_EMAIL to be set.
    The recipient email is fetched from the customer-service.
    """
    # Fetch customer email from customer-service
    async with httpx.AsyncClient() as client:
        try:
            customer_response = await client.get(
                f"{settings.customer_service_url}/customers/{customer_id}",
                timeout=5
            )
            customer_response.raise_for_status()
            customer = customer_response.json()
        except Exception as e:
            print(f"Failed to fetch customer {customer_id}: {e}")
            return {"customer_id": customer_id, "success": False, "error": str(e)}

        to_email = customer.get("email")
        if not to_email:
            return {"customer_id": customer_id, "success": False, "error": "Customer has no email address"}

        try:
            response = await client.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {settings.sendgrid_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "personalizations": [{"to": [{"email": to_email}]}],
                    "from": {"email": settings.sendgrid_from_email},
                    "subject": subject,
                    "content": [{"type": "text/plain", "value": body}]
                },
                timeout=10
            )
            # SendGrid returns 202 Accepted on success
            success = response.status_code == 202
            print(f"{'✓' if success else '✗'} SendGrid email to {to_email} (customer {customer_id}): {response.status_code}")
            return {
                "customer_id": customer_id,
                "success": success,
                "status_code": response.status_code
            }
        except Exception as e:
            print(f"Failed to send SendGrid email to customer {customer_id}: {e}")
            return {"customer_id": customer_id, "success": False, "error": str(e)}
