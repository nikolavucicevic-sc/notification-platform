# Quick Start Guide

Get started with the Notification Platform SDK in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A Notification Platform account with API access

## Step 1: Install the SDK (30 seconds)

```bash
pip install git+https://github.com/nikolavucicevic-sc/notification-platform.git#subdirectory=notification-platform-sdk
```

Verify installation:
```bash
python -c "from notification_platform_sdk import NotificationPlatformClient; print('✓ SDK installed!')"
```

## Step 2: Get Your API Key (2 minutes)

1. **Log in** to your Notification Platform: `http://18.156.176.60:3000`
2. **Navigate** to Admin → API Keys
3. **Create** a new API key
4. **Copy** the key (shown only once!)

## Step 3: Write Your First Code (2 minutes)

Create `my_first_notification.py`:

```python
from notification_platform_sdk import NotificationPlatformClient

# Initialize
client = NotificationPlatformClient(
    base_url="http://18.156.176.60:3000",
    api_key="paste_your_api_key_here"
)

# Create a customer
customer = client.customers.create(
    email="you@example.com",
    first_name="Your Name"
)

# Send notification
notification = client.notifications.send(
    customer_id=customer["id"],
    channel="email",
    subject="My First Notification!",
    body="Hello from the SDK!"
)

print(f"✓ Sent notification: {notification['id']}")
client.close()
```

## Step 4: Run It!

```bash
python my_first_notification.py
```

You should see:
```
✓ Sent notification: 123e4567-e89b-12d3-a456-426614174000
```

## What's Next?

### Send SMS Notifications

```python
notification = client.notifications.send(
    customer_id=customer["id"],
    channel="sms",
    body="Your verification code is 123456"
)
```

### Use Templates

```python
# Create template
template = client.templates.create(
    name="welcome",
    channel="email",
    subject="Welcome {{name}}!",
    body_template="Hi {{name}}, thanks for joining!"
)

# Use template
notification = client.notifications.send(
    customer_id=customer["id"],
    channel="email",
    template_id="welcome",
    template_data={"name": "Alice"}
)
```

### Schedule Recurring Notifications

```python
# Daily reminder at 9 AM
schedule = client.schedules.create(
    name="Daily reminder",
    customer_id=customer["id"],
    channel="email",
    cron_expression="0 9 * * *",
    subject="Daily Reminder",
    body="Don't forget your tasks!"
)
```

### Handle Errors

```python
from notification_platform_sdk import NotFoundError

try:
    customer = client.customers.get("some-id")
except NotFoundError:
    print("Customer not found!")
```

## Common Use Cases

### 1. Welcome Email on User Signup

```python
def send_welcome_email(user_email, user_name):
    # Create customer
    customer = client.customers.create(
        email=user_email,
        first_name=user_name
    )

    # Send welcome email
    client.notifications.send(
        customer_id=customer["id"],
        channel="email",
        template_id="welcome_email",
        template_data={"name": user_name}
    )
```

### 2. SMS Verification Code

```python
def send_verification_code(phone_number, code):
    # Get or create customer
    customer = client.customers.create(
        email=f"{phone_number}@temp.com",
        phone=phone_number
    )

    # Send SMS
    client.notifications.send(
        customer_id=customer["id"],
        channel="sms",
        body=f"Your verification code is {code}"
    )
```

### 3. Order Confirmation

```python
def send_order_confirmation(customer_email, order_id, total):
    customer = client.customers.get_by_email(customer_email)

    client.notifications.send(
        customer_id=customer["id"],
        channel="email",
        template_id="order_confirmation",
        template_data={
            "order_id": order_id,
            "total": total
        }
    )
```

### 4. Weekly Report Schedule

```python
def setup_weekly_report(customer_email):
    customer = client.customers.get_by_email(customer_email)

    # Every Monday at 8 AM
    schedule = client.schedules.create(
        name="Weekly report",
        customer_id=customer["id"],
        channel="email",
        cron_expression="0 8 * * MON",
        template_id="weekly_report",
        template_data={"name": customer["first_name"]}
    )
```

## Tips & Best Practices

### Use Context Manager
```python
with NotificationPlatformClient(base_url="...", api_key="...") as client:
    # Your code here
    pass
# Automatic cleanup
```

### Store API Key Securely
```python
import os

client = NotificationPlatformClient(
    base_url=os.environ.get("NOTIFICATION_API_URL"),
    api_key=os.environ.get("NOTIFICATION_API_KEY")
)
```

### Implement Retry Logic
```python
from notification_platform_sdk import RateLimitError
import time

def send_with_retry(client, **kwargs):
    for attempt in range(3):
        try:
            return client.notifications.send(**kwargs)
        except RateLimitError:
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                raise
```

### Pagination for Large Lists
```python
def get_all_customers(client):
    all_customers = []
    skip = 0
    limit = 100

    while True:
        batch = client.customers.list(skip=skip, limit=limit)
        if not batch:
            break
        all_customers.extend(batch)
        skip += limit

    return all_customers
```

## Need Help?

- **Full Documentation**: See [README.md](README.md)
- **Examples**: Check the [examples/](examples/) directory
- **Installation Issues**: See [INSTALLATION.md](INSTALLATION.md)

## Ready for Production?

When you're ready to go live:

1. **Use HTTPS**: Update to your production URL with SSL
2. **Secure API Keys**: Use environment variables or secret management
3. **Error Handling**: Implement comprehensive error handling
4. **Monitoring**: Track notification delivery rates
5. **Rate Limiting**: Implement retry logic with exponential backoff

## Complete Example: E-commerce Integration

```python
from notification_platform_sdk import NotificationPlatformClient
import os

class NotificationService:
    def __init__(self):
        self.client = NotificationPlatformClient(
            base_url=os.environ.get("NOTIFICATION_API_URL"),
            api_key=os.environ.get("NOTIFICATION_API_KEY")
        )

    def on_user_signup(self, email, name):
        """Send welcome email on user signup"""
        customer = self.client.customers.create(
            email=email,
            first_name=name
        )

        self.client.notifications.send(
            customer_id=customer["id"],
            channel="email",
            template_id="welcome_email",
            template_data={"name": name}
        )

    def on_order_placed(self, email, order_id, items, total):
        """Send order confirmation"""
        customer = self.client.customers.get_by_email(email)

        self.client.notifications.send(
            customer_id=customer["id"],
            channel="email",
            template_id="order_confirmation",
            template_data={
                "order_id": order_id,
                "items": items,
                "total": total
            }
        )

    def on_shipment(self, email, tracking_number):
        """Send shipment notification via email and SMS"""
        customer = self.client.customers.get_by_email(email)

        # Email
        self.client.notifications.send(
            customer_id=customer["id"],
            channel="email",
            template_id="shipment_notification",
            template_data={"tracking_number": tracking_number}
        )

        # SMS if phone available
        if customer.get("phone"):
            self.client.notifications.send(
                customer_id=customer["id"],
                channel="sms",
                body=f"Your order has shipped! Track it: {tracking_number}"
            )

# Usage
notifications = NotificationService()
notifications.on_user_signup("user@example.com", "John Doe")
```

---

**You're all set! Start sending notifications in production! 🚀**
