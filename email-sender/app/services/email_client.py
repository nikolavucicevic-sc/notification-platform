import httpx
from app.config import settings


async def send_email(customer_id: str, subject: str, body: str) -> dict:
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
