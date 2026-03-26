# Installation Guide

## For Customers: How to Install and Use the SDK

### Option 1: Install Directly from GitHub (Recommended for Now)

Since the SDK is not yet published to PyPI, you can install it directly from GitHub:

```bash
pip install git+https://github.com/nikolavucicevic-sc/notification-platform.git#subdirectory=notification-platform-sdk
```

This will install the SDK from the main branch of the repository.

### Option 2: Install from Local Copy

If you've downloaded or cloned the repository:

```bash
# Clone the repository
git clone https://github.com/nikolavucicevic-sc/notification-platform.git

# Navigate to the SDK directory
cd notification-platform/notification-platform-sdk

# Install in development mode
pip install -e .

# Or install normally
pip install .
```

### Option 3: Install from PyPI (Coming Soon)

Once published to PyPI, installation will be as simple as:

```bash
pip install notification-platform-sdk
```

## Quick Start After Installation

### Step 1: Get Your API Key

1. Log in to your Notification Platform account at: `http://18.156.176.60:3000`
2. Navigate to **Admin** → **API Keys** tab
3. Click **Create API Key**
4. Give it a name (e.g., "Production API Key")
5. Copy the key (it's only shown once!)

### Step 2: Create Your First Script

Create a file called `test_notifications.py`:

```python
from notification_platform_sdk import NotificationPlatformClient

# Initialize the client
client = NotificationPlatformClient(
    base_url="http://18.156.176.60:3000",  # Your instance URL
    api_key="np_your_api_key_here"         # Replace with your actual API key
)

# Create a customer
print("Creating customer...")
customer = client.customers.create(
    email="test@example.com",
    first_name="Test",
    last_name="User",
    phone="+1234567890"
)
print(f"✓ Customer created: {customer['id']}")

# Send an email notification
print("\nSending notification...")
notification = client.notifications.send(
    customer_id=customer["id"],
    channel="email",
    subject="Test Notification",
    body="This is a test notification from the SDK!"
)
print(f"✓ Notification sent: {notification['id']}")
print(f"✓ Status: {notification['status']}")

# List all customers
print("\nListing customers...")
customers = client.customers.list(limit=5)
print(f"✓ Found {len(customers)} customers")

client.close()
print("\n✓ All operations completed successfully!")
```

### Step 3: Run Your Script

```bash
python test_notifications.py
```

## Verification

To verify the SDK is installed correctly, run:

```bash
python -c "from notification_platform_sdk import NotificationPlatformClient; print('SDK installed successfully!')"
```

## Troubleshooting

### Issue: Module not found

**Problem**: `ModuleNotFoundError: No module named 'notification_platform_sdk'`

**Solution**: Make sure you've installed the SDK:
```bash
pip install git+https://github.com/nikolavucicevic-sc/notification-platform.git#subdirectory=notification-platform-sdk
```

### Issue: Authentication error

**Problem**: `AuthenticationError: Invalid or missing authentication token`

**Solutions**:
1. Check that your API key is correct
2. Ensure the API key hasn't expired or been revoked
3. Make sure you're passing the key correctly:
   ```python
   client = NotificationPlatformClient(
       base_url="http://18.156.176.60:3000",
       api_key="np_your_actual_key_here"  # Replace this!
   )
   ```

### Issue: Connection error

**Problem**: `ConnectionError` or `timeout`

**Solutions**:
1. Verify the base URL is correct
2. Check that the server is running
3. Ensure you have internet connectivity
4. Try increasing the timeout:
   ```python
   client = NotificationPlatformClient(
       base_url="http://18.156.176.60:3000",
       api_key="np_your_key",
       timeout=60  # Increase timeout to 60 seconds
   )
   ```

### Issue: Import error

**Problem**: `ImportError: cannot import name 'NotificationPlatformClient'`

**Solution**: Reinstall the SDK:
```bash
pip uninstall notification-platform-sdk
pip install git+https://github.com/nikolavucicevic-sc/notification-platform.git#subdirectory=notification-platform-sdk
```

## Python Version

The SDK requires Python 3.8 or higher. Check your Python version:

```bash
python --version
```

If you need to upgrade Python:
- **macOS/Linux**: Use `pyenv` or download from python.org
- **Windows**: Download from python.org

## Dependencies

The SDK only requires one dependency:
- `requests>=2.25.0`

This will be installed automatically when you install the SDK.

## Virtual Environment (Recommended)

It's recommended to use a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install SDK
pip install git+https://github.com/nikolavucicevic-sc/notification-platform.git#subdirectory=notification-platform-sdk

# Verify
python -c "from notification_platform_sdk import NotificationPlatformClient; print('Success!')"
```

## Next Steps

After successful installation:

1. Check out the [README.md](README.md) for comprehensive usage examples
2. Explore the [examples/](examples/) directory for sample scripts
3. Read the API documentation for your specific use case

## Support

If you encounter issues:
- Check the [README.md](README.md) for detailed documentation
- Review the [examples/](examples/) for working code samples
- Contact support at your Notification Platform instance

## Uninstalling

To uninstall the SDK:

```bash
pip uninstall notification-platform-sdk
```
