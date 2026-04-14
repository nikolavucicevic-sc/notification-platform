"""
Basic usage examples for the Notification Platform SDK.
"""

from notification_platform_sdk import NotificationPlatformClient

# Initialize the client
client = NotificationPlatformClient(
    base_url="https://notifications.example.com",
    api_key="np_your_api_key_here"
)

# Example 1: Create a customer
print("Example 1: Creating a customer...")
customer = client.customers.create(
    email="john@example.com",
    first_name="John",
    last_name="Doe",
    phone="+1234567890",
    preferences={
        "email": True,
        "sms": True,
        "push": False
    }
)
print(f"✓ Customer created with ID: {customer['id']}")

# Example 2: Send a simple email
print("\nExample 2: Sending an email notification...")
notification = client.notifications.send(
    customer_id=customer["id"],
    channel="email",
    subject="Welcome to our platform!",
    body="Hi John, thanks for signing up!",
    priority="high"
)
print(f"✓ Notification sent with ID: {notification['id']}")

# Example 3: List all customers
print("\nExample 3: Listing customers...")
customers = client.customers.list(limit=10)
print(f"✓ Found {len(customers)} customers")
for c in customers[:3]:  # Show first 3
    print(f"  - {c['email']}")

# Example 4: Get notification status
print(f"\nExample 4: Checking notification status...")
notification_detail = client.notifications.get(notification["id"])
print(f"✓ Notification status: {notification_detail['status']}")

print("\n✓ All examples completed successfully!")

# Clean up
client.close()
