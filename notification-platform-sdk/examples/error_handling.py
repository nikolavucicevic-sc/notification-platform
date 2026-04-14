"""
Error handling examples for the Notification Platform SDK.
"""

from notification_platform_sdk import (
    NotificationPlatformClient,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    NotificationPlatformError,
)

# Initialize the client
client = NotificationPlatformClient(
    base_url="https://notifications.example.com",
    api_key="np_your_api_key_here"
)

# Example 1: Handle authentication errors
print("Example 1: Handling authentication errors...")
try:
    bad_client = NotificationPlatformClient(
        base_url="https://notifications.example.com",
        api_key="invalid_key"
    )
    customers = bad_client.customers.list()
except AuthenticationError as e:
    print(f"✓ Caught authentication error: {e.message}")
    print(f"  Status code: {e.status_code}")

# Example 2: Handle not found errors
print("\nExample 2: Handling not found errors...")
try:
    customer = client.customers.get("non-existent-id-12345")
except NotFoundError as e:
    print(f"✓ Caught not found error: {e.message}")
    print(f"  Status code: {e.status_code}")

# Example 3: Handle validation errors
print("\nExample 3: Handling validation errors...")
try:
    # Try to create customer with invalid email
    customer = client.customers.create(
        email="invalid-email",  # Invalid email format
        first_name="Test"
    )
except ValidationError as e:
    print(f"✓ Caught validation error: {e.message}")
    print(f"  Status code: {e.status_code}")
    if e.response:
        print(f"  Details: {e.response}")

# Example 4: Retry logic for rate limits
print("\nExample 4: Handling rate limit with retry...")
import time

def send_with_retry(client, customer_id, max_retries=3):
    """Send notification with automatic retry on rate limit."""
    for attempt in range(max_retries):
        try:
            return client.notifications.send(
                customer_id=customer_id,
                channel="email",
                subject="Test",
                body="Test notification"
            )
        except RateLimitError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"  Rate limited, waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                print(f"✗ Failed after {max_retries} attempts")
                raise

# Example 5: Generic error handling
print("\nExample 5: Generic error handling...")
try:
    # Try some operation that might fail
    notification = client.notifications.get("some-id")
except NotFoundError:
    print("✓ Resource not found, creating new one...")
    # Handle not found by creating new resource
except ValidationError as e:
    print(f"✓ Validation failed: {e.message}")
    # Handle validation errors
except NotificationPlatformError as e:
    print(f"✓ General error occurred: {e.message}")
    # Handle any other API errors
except Exception as e:
    print(f"✓ Unexpected error: {e}")
    # Handle unexpected errors

# Example 6: Context manager with error handling
print("\nExample 6: Using context manager with error handling...")
try:
    with NotificationPlatformClient(
        base_url="https://notifications.example.com",
        api_key="np_your_api_key_here"
    ) as client:
        customers = client.customers.list(limit=5)
        print(f"✓ Retrieved {len(customers)} customers")
except NotificationPlatformError as e:
    print(f"✗ API error: {e.message}")
except Exception as e:
    print(f"✗ Unexpected error: {e}")
# Connection automatically closed even if error occurs

# Example 7: Graceful degradation
print("\nExample 7: Graceful degradation pattern...")

def get_customer_safe(client, customer_id):
    """Get customer with fallback to None on error."""
    try:
        return client.customers.get(customer_id)
    except NotFoundError:
        print(f"  Customer {customer_id} not found")
        return None
    except NotificationPlatformError as e:
        print(f"  API error: {e.message}")
        return None

customer = get_customer_safe(client, "some-id")
if customer:
    print(f"✓ Found customer: {customer['email']}")
else:
    print("✓ Customer not found, using default behavior")

print("\n✓ All error handling examples completed!")

# Clean up
client.close()
