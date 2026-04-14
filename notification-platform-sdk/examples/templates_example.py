"""
Template usage examples for the Notification Platform SDK.
"""

from notification_platform_sdk import NotificationPlatformClient

# Initialize the client
client = NotificationPlatformClient(
    base_url="https://notifications.example.com",
    api_key="np_your_api_key_here"
)

# Example 1: Create an email template
print("Example 1: Creating an email template...")
template = client.templates.create(
    name="welcome_email",
    channel="email",
    subject="Welcome {{name}} to {{company}}!",
    body_template="""
    Hi {{name}},

    Welcome to {{company}}! We're excited to have you on board.

    Your account has been successfully created with the email: {{email}}

    Best regards,
    The {{company}} Team
    """,
    variables=["name", "company", "email"]
)
print(f"✓ Template created: {template['name']}")

# Example 2: Preview the template
print("\nExample 2: Previewing the template...")
rendered = client.templates.render(
    "welcome_email",
    data={
        "name": "Alice",
        "company": "Acme Corp",
        "email": "alice@example.com"
    }
)
print(f"✓ Rendered subject: {rendered['subject']}")
print(f"✓ Rendered body preview: {rendered['body'][:100]}...")

# Example 3: Create a customer
print("\nExample 3: Creating a customer...")
customer = client.customers.create(
    email="alice@example.com",
    first_name="Alice",
    last_name="Smith"
)
print(f"✓ Customer created: {customer['email']}")

# Example 4: Send notification using template
print("\nExample 4: Sending notification with template...")
notification = client.notifications.send(
    customer_id=customer["id"],
    channel="email",
    template_id="welcome_email",
    template_data={
        "name": "Alice",
        "company": "Acme Corp",
        "email": customer["email"]
    }
)
print(f"✓ Notification sent with ID: {notification['id']}")

# Example 5: Create SMS template
print("\nExample 5: Creating an SMS template...")
sms_template = client.templates.create(
    name="otp_sms",
    channel="sms",
    body_template="Your verification code is {{code}}. Valid for {{minutes}} minutes.",
    variables=["code", "minutes"]
)
print(f"✓ SMS template created: {sms_template['name']}")

# Example 6: List all templates
print("\nExample 6: Listing all templates...")
templates = client.templates.list()
print(f"✓ Found {len(templates)} templates:")
for t in templates:
    print(f"  - {t['name']} ({t['channel']})")

print("\n✓ All template examples completed successfully!")

# Clean up
client.close()
