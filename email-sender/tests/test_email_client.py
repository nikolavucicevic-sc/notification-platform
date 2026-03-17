import pytest
from unittest.mock import AsyncMock, patch
import httpx

from app.services.email_client import send_email


@pytest.mark.unit
class TestEmailClient:
    """Test cases for email client."""

    @pytest.mark.asyncio
    @patch("app.services.email_client.httpx.AsyncClient")
    async def test_send_email_success(self, mock_client_class):
        """Test successful email sending."""
        # Setup mock
        mock_response = AsyncMock()
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        mock_client_class.return_value = mock_client

        # Execute
        result = await send_email("customer-123", "Test Subject", "Test Body")

        # Verify
        assert result["customer_id"] == "customer-123"
        assert result["success"] is True
        assert result["status_code"] == 200

        # Verify API was called with correct parameters
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert "/send-email" in call_args[0][0]
        assert call_args[1]["json"]["customer_id"] == "customer-123"
        assert call_args[1]["json"]["subject"] == "Test Subject"
        assert call_args[1]["json"]["body"] == "Test Body"

    @pytest.mark.asyncio
    @patch("app.services.email_client.httpx.AsyncClient")
    async def test_send_email_failure_status_code(self, mock_client_class):
        """Test email sending with non-200 status code."""
        # Setup mock
        mock_response = AsyncMock()
        mock_response.status_code = 500

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        mock_client_class.return_value = mock_client

        # Execute
        result = await send_email("customer-123", "Test Subject", "Test Body")

        # Verify
        assert result["customer_id"] == "customer-123"
        assert result["success"] is False
        assert result["status_code"] == 500

    @pytest.mark.asyncio
    @patch("app.services.email_client.httpx.AsyncClient")
    async def test_send_email_exception(self, mock_client_class):
        """Test email sending with exception."""
        # Setup mock
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=httpx.ConnectError("Connection failed"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        mock_client_class.return_value = mock_client

        # Execute
        result = await send_email("customer-123", "Test Subject", "Test Body")

        # Verify
        assert result["customer_id"] == "customer-123"
        assert result["success"] is False
        assert "error" in result
        assert "Connection failed" in result["error"]

    @pytest.mark.asyncio
    @patch("app.services.email_client.httpx.AsyncClient")
    async def test_send_email_timeout(self, mock_client_class):
        """Test email sending with timeout."""
        # Setup mock
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        mock_client_class.return_value = mock_client

        # Execute
        result = await send_email("customer-123", "Test Subject", "Test Body")

        # Verify
        assert result["success"] is False
        assert "error" in result
