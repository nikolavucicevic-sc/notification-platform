# Notification Platform SDK

Official Python SDK for the Notification Platform API.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Features

- **Easy to use**: Simple, intuitive API
- **Type hints**: Full type annotation support
- **Comprehensive**: Covers all API endpoints
- **Well documented**: Extensive docstrings and examples
- **Error handling**: Custom exceptions for different error types
- **Context manager**: Automatic resource cleanup
- **Production ready**: Battle-tested and reliable

## Installation

```bash
pip install notification-platform-sdk
```

## Quick Start

```python
from notification_platform_sdk import NotificationPlatformClient

# Initialize the client
client = NotificationPlatformClient(
    base_url="https://notifications.example.com",
    api_key="np_your_api_key_here"
)

# Create a customer
customer = client.customers.create(
    email="john@example.com",
    first_name="John",
    last_name="Doe",
    phone="+1234567890"
)

# Send an email notification
notification = client.notifications.send(
    customer_id=customer["id"],
    channel="email",
    subject="Welcome to our platform!",
    body="Hi John, thanks for signing up!"
)

print(f"Notification sent with ID: {notification['id']}")
```

## Authentication

You need an API key to use the SDK. To get an API key:

1. Log in to your Notification Platform account
2. Navigate to **Settings** → **API Keys**
3. Click **Create API Key**
4. Copy the key (it's only shown once!)

```python
client = NotificationPlatformClient(
    base_url="https://your-instance.com",
    api_key="np_1234567890abcdef"
)
```

## Usage Examples

### Customers

#### Create a customer

```python
customer = client.customers.create(
    email="alice@example.com",
    phone="+1234567890",
    first_name="Alice",
    last_name="Smith",
    preferences={
        "email": True,
        "sms": True,
        "push": False
    },
    metadata={
        "plan": "premium",
        "signup_date": "2024-01-15"
    }
)
```

#### List customers

```python
# Get first 50 customers
customers = client.customers.list(limit=50)

# Pagination
customers_page_2 = client.customers.list(skip=50, limit=50)
```

#### Get a customer

```python
customer = client.customers.get("customer-id-here")
print(customer["email"])
```

#### Update a customer

```python
customer = client.customers.update(
    "customer-id-here",
    first_name="Alicia",
    preferences={"email": True, "sms": False}
)
```

#### Delete a customer

```python
client.customers.delete("customer-id-here")
```

#### Get customer by email

```python
customer = client.customers.get_by_email("alice@example.com")
```

### Notifications

#### Send a simple notification

```python
notification = client.notifications.send(
    customer_id="customer-id-here",
    channel="email",
    subject="Welcome!",
    body="Welcome to our platform!",
    priority="high"
)
```

#### Send SMS notification

```python
notification = client.notifications.send(
    customer_id="customer-id-here",
    channel="sms",
    body="Your verification code is 123456"
)
```

#### Send with template

```python
notification = client.notifications.send(
    customer_id="customer-id-here",
    channel="email",
    template_id="welcome_email",
    template_data={
        "name": "Alice",
        "company": "Acme Corp"
    }
)
```

#### Schedule a notification

```python
notification = client.notifications.send(
    customer_id="customer-id-here",
    channel="email",
    subject="Reminder",
    body="Don't forget your appointment tomorrow!",
    scheduled_at="2024-12-25T10:00:00Z"
)
```

#### List notifications

```python
# All notifications
notifications = client.notifications.list()

# Filter by customer
notifications = client.notifications.list(customer_id="customer-id-here")

# Filter by status
failed_notifications = client.notifications.list(status="failed")

# Filter by channel
email_notifications = client.notifications.list(channel="email")
```

#### Get notification

```python
notification = client.notifications.get("notification-id-here")
print(notification["status"])
```

#### Update notification status

```python
notification = client.notifications.update_status(
    "notification-id-here",
    status="delivered"
)

# Mark as failed with error
notification = client.notifications.update_status(
    "notification-id-here",
    status="failed",
    error_message="Recipient email bounced"
)
```

#### Retry a failed notification

```python
notification = client.notifications.retry("notification-id-here")
```

#### Cancel a scheduled notification

```python
notification = client.notifications.cancel("notification-id-here")
```

#### Get statistics

```python
stats = client.notifications.get_stats(
    start_date="2024-01-01T00:00:00Z",
    end_date="2024-12-31T23:59:59Z"
)
print(stats)
```

### Templates

#### Create a template

```python
# Email template
template = client.templates.create(
    name="welcome_email",
    channel="email",
    subject="Welcome {{name}}!",
    body_template="Hi {{name}}, welcome to {{company}}!",
    variables=["name", "company"],
    metadata={"category": "onboarding"}
)

# SMS template
template = client.templates.create(
    name="otp_sms",
    channel="sms",
    body_template="Your OTP is {{code}}. Valid for {{minutes}} minutes.",
    variables=["code", "minutes"]
)
```

#### List templates

```python
# All templates
templates = client.templates.list()

# Filter by channel
email_templates = client.templates.list(channel="email")
```

#### Get a template

```python
template = client.templates.get("welcome_email")
print(template["body_template"])
```

#### Update a template

```python
template = client.templates.update(
    "welcome_email",
    subject="Welcome {{name}} to {{company}}!",
    body_template="Hi {{name}}, thanks for joining {{company}}!"
)
```

#### Delete a template

```python
client.templates.delete("old_template")
```

#### Render a template (preview)

```python
rendered = client.templates.render(
    "welcome_email",
    data={"name": "Alice", "company": "Acme Corp"}
)
print(rendered["subject"])  # "Welcome Alice!"
print(rendered["body"])     # "Hi Alice, welcome to Acme Corp!"
```

### Schedules

#### Create a recurring schedule

```python
# Daily reminder at 9 AM
schedule = client.schedules.create(
    name="Daily reminder",
    customer_id="customer-id-here",
    channel="email",
    cron_expression="0 9 * * *",
    subject="Daily Reminder",
    body="Don't forget to check your tasks!",
    timezone="America/New_York"
)

# Weekly report on Mondays at 10 AM
schedule = client.schedules.create(
    name="Weekly report",
    customer_id="customer-id-here",
    channel="email",
    cron_expression="0 10 * * MON",
    template_id="weekly_report",
    template_data={"report_type": "sales"}
)
```

#### List schedules

```python
# All schedules
schedules = client.schedules.list()

# Filter by customer
schedules = client.schedules.list(customer_id="customer-id-here")

# Only active schedules
active_schedules = client.schedules.list(enabled=True)
```

#### Get a schedule

```python
schedule = client.schedules.get("schedule-id-here")
print(schedule["cron_expression"])
```

#### Update a schedule

```python
# Change time
schedule = client.schedules.update(
    "schedule-id-here",
    cron_expression="0 10 * * *"  # Change to 10 AM
)

# Disable
schedule = client.schedules.update(
    "schedule-id-here",
    enabled=False
)
```

#### Delete a schedule

```python
client.schedules.delete("schedule-id-here")
```

#### Enable/disable shortcuts

```python
# Enable
schedule = client.schedules.enable("schedule-id-here")

# Disable
schedule = client.schedules.disable("schedule-id-here")
```

#### Get next run time

```python
next_run = client.schedules.get_next_run("schedule-id-here")
print(next_run["next_run"])  # "2024-12-25T10:00:00Z"
```

## Error Handling

The SDK provides custom exceptions for different error scenarios:

```python
from notification_platform_sdk import (
    NotificationPlatformClient,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
)

client = NotificationPlatformClient(base_url="...", api_key="...")

try:
    customer = client.customers.get("invalid-id")
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    print(f"Status code: {e.status_code}")
except NotFoundError as e:
    print(f"Customer not found: {e.message}")
except ValidationError as e:
    print(f"Validation error: {e.message}")
    print(f"Details: {e.response}")
except RateLimitError as e:
    print(f"Rate limit exceeded: {e.message}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Context Manager

Use the client as a context manager for automatic cleanup:

```python
with NotificationPlatformClient(base_url="...", api_key="...") as client:
    customers = client.customers.list()
    for customer in customers:
        print(customer["email"])
# Connection automatically closed
```

## Advanced Usage

### Custom timeout

```python
# Set custom timeout (default is 30 seconds)
client = NotificationPlatformClient(
    base_url="https://notifications.example.com",
    api_key="np_your_api_key",
    timeout=60  # 60 seconds
)
```

### Pagination helper

```python
def get_all_customers(client):
    """Get all customers with automatic pagination."""
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

customers = get_all_customers(client)
```

### Bulk operations

```python
# Create multiple customers
customers_data = [
    {"email": "user1@example.com", "first_name": "User1"},
    {"email": "user2@example.com", "first_name": "User2"},
    {"email": "user3@example.com", "first_name": "User3"},
]

created_customers = []
for data in customers_data:
    customer = client.customers.create(**data)
    created_customers.append(customer)

# Send bulk notifications
for customer in created_customers:
    client.notifications.send(
        customer_id=customer["id"],
        channel="email",
        subject="Welcome!",
        body="Thanks for joining!"
    )
```

## Cron Expression Guide

For schedules, use standard cron expressions:

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday=0)
│ │ │ │ │
│ │ │ │ │
* * * * *
```

Examples:
- `0 9 * * *` - Daily at 9:00 AM
- `0 */6 * * *` - Every 6 hours
- `0 9 * * MON` - Every Monday at 9:00 AM
- `0 9 1 * *` - First day of month at 9:00 AM
- `*/15 * * * *` - Every 15 minutes

## Requirements

- Python 3.8+
- requests

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Support

- **Documentation**: [https://docs.notification-platform.com](https://docs.notification-platform.com)
- **Issues**: [GitHub Issues](https://github.com/your-org/notification-platform-sdk/issues)
- **Email**: support@notification-platform.com

## Changelog

### 1.0.0 (2024-01-15)
- Initial release
- Full API coverage
- Comprehensive documentation
- Error handling
- Context manager support
