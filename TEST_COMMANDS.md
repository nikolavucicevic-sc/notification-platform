# Quick Test Commands Cheat Sheet

## The Problem
When running pytest from the **project root**, you'll get `ImportPathMismatchError` because pytest tries to collect tests from all services at once, and each service has its own `conftest.py` file.

## The Solution
Always run tests **from within each service directory**, or use the convenience script.

---

## ✅ Recommended: Use the Test Script

```bash
# From anywhere in the project
./run-tests.sh
```

This script automatically runs tests for all three services in sequence.

---

## 📁 Run Tests Per Service

### Customer Service
```bash
cd customer-service

# All tests
pytest -v

# With coverage
pytest -v --cov=app --cov-report=term-missing

# Only API tests
pytest -m api -v

# Only unit tests
pytest -m unit -v

# Specific test file
pytest tests/test_api.py -v

# Specific test class
pytest tests/test_api.py::TestCreateCustomer -v

# Specific test method
pytest tests/test_api.py::TestCreateCustomer::test_create_customer_success -v
```

### Notification Service
```bash
cd notification-service

# All tests
pytest -v

# Only messaging tests
pytest -m messaging -v

# Only API tests
pytest -m api -v

# Only unit tests
pytest -m unit -v
```

### Email Sender
```bash
cd email-sender

# All tests
pytest -v

# Only messaging tests
pytest -m messaging -v

# Only unit tests
pytest -m unit -v
```

---

## 🚫 Don't Do This (from project root)

```bash
# ❌ This will cause ImportPathMismatchError
cd /Users/nikola.vucicevic/PycharmProjects/notification-platform
pytest -m unit -v

# ❌ This will also fail
pytest customer-service/tests/ -v
```

---

## ✅ Do This Instead

```bash
# Option 1: Use the script
./run-tests.sh

# Option 2: CD into service first
cd customer-service && pytest -v

# Option 3: One-liner for all services
cd customer-service && pytest -v && cd ../notification-service && pytest -v && cd ../email-sender && pytest -v && cd ..
```

---

## 📊 Useful Test Commands

### View HTML Coverage Report
```bash
cd customer-service
pytest --cov=app --cov-report=html
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

### Run Tests and Stop on First Failure
```bash
cd customer-service
pytest -v -x
```

### Run Tests with Extra Verbosity
```bash
cd customer-service
pytest -vv
```

### Run Tests in Parallel (faster)
```bash
cd customer-service
pip install pytest-xdist
pytest -n auto
```

### Show Test Output (print statements)
```bash
cd customer-service
pytest -v -s
```

### List All Tests Without Running
```bash
cd customer-service
pytest --collect-only
```

---

## 🎯 Common Test Markers

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.messaging` - Message queue tests

---

## 🐛 Troubleshooting

### Issue: "ImportPathMismatchError"
**Cause:** Running pytest from project root
**Fix:** CD into service directory first

### Issue: "pytest: command not found"
**Cause:** pytest not installed
**Fix:** `pip install -r requirements.txt`

### Issue: "No module named 'app'"
**Cause:** Running from wrong directory
**Fix:** CD into service directory (customer-service, notification-service, or email-sender)

### Issue: "Unknown pytest.mark.api"
**Cause:** Just a warning, tests still run fine
**Fix:** Already configured in pytest.ini, you can ignore this warning

---

## 📝 Test File Locations

```
customer-service/tests/
  ├── test_api.py       # 15 API tests
  └── test_models.py    # 5 model tests

notification-service/tests/
  ├── test_api.py       # API tests
  ├── test_models.py    # Model tests
  └── test_messaging.py # Messaging tests

email-sender/tests/
  ├── test_email_client.py  # Email client tests
  ├── test_consumer.py      # Consumer tests
  └── test_dlq_handler.py   # DLQ handler tests
```

---

## 🚀 Quick Start

**First time setup:**
```bash
cd customer-service && pip install -r requirements.txt && cd ..
cd notification-service && pip install -r requirements.txt && cd ..
cd email-sender && pip install -r requirements.txt && cd ..
```

**Run all tests:**
```bash
./run-tests.sh
```

**Run tests for one service:**
```bash
cd customer-service && pytest -v
```

That's it! 🎉