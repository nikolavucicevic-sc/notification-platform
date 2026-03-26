"""
Base HTTP client for making API requests.
"""

import requests
from typing import Optional, Dict, Any
from urllib.parse import urljoin

from .exceptions import (
    NotificationPlatformError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ForbiddenError,
    ServerError,
)


class BaseClient:
    """Base HTTP client with authentication and error handling."""

    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        """
        Initialize the base client.

        Args:
            base_url: The base URL of the API (e.g., "https://api.example.com")
            api_key: API key for authentication
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        return urljoin(self.base_url + "/", endpoint.lstrip("/"))

    def _handle_response(self, response: requests.Response) -> Any:
        """
        Handle HTTP response and raise appropriate exceptions.

        Args:
            response: The HTTP response object

        Returns:
            Parsed JSON response or None for 204 No Content

        Raises:
            NotificationPlatformError: For various HTTP error codes
        """
        # Success responses
        if response.status_code == 204:
            return None

        if 200 <= response.status_code < 300:
            try:
                return response.json()
            except ValueError:
                return response.text

        # Error responses
        try:
            error_data = response.json()
            error_message = error_data.get("detail", response.text)
        except ValueError:
            error_message = response.text or f"HTTP {response.status_code}"

        # Map status codes to exceptions
        if response.status_code == 401:
            raise AuthenticationError(
                error_message,
                status_code=response.status_code,
                response=error_data if 'error_data' in locals() else None
            )
        elif response.status_code == 403:
            raise ForbiddenError(
                error_message,
                status_code=response.status_code,
                response=error_data if 'error_data' in locals() else None
            )
        elif response.status_code == 404:
            raise NotFoundError(
                error_message,
                status_code=response.status_code,
                response=error_data if 'error_data' in locals() else None
            )
        elif response.status_code in (400, 422):
            raise ValidationError(
                error_message,
                status_code=response.status_code,
                response=error_data if 'error_data' in locals() else None
            )
        elif response.status_code == 429:
            raise RateLimitError(
                error_message,
                status_code=response.status_code,
                response=error_data if 'error_data' in locals() else None
            )
        elif response.status_code >= 500:
            raise ServerError(
                error_message,
                status_code=response.status_code,
                response=error_data if 'error_data' in locals() else None
            )
        else:
            raise NotificationPlatformError(
                error_message,
                status_code=response.status_code,
                response=error_data if 'error_data' in locals() else None
            )

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make a GET request."""
        url = self._build_url(endpoint)
        response = self.session.get(url, params=params, timeout=self.timeout)
        return self._handle_response(response)

    def post(self, endpoint: str, json: Optional[Dict[str, Any]] = None) -> Any:
        """Make a POST request."""
        url = self._build_url(endpoint)
        response = self.session.post(url, json=json, timeout=self.timeout)
        return self._handle_response(response)

    def put(self, endpoint: str, json: Optional[Dict[str, Any]] = None) -> Any:
        """Make a PUT request."""
        url = self._build_url(endpoint)
        response = self.session.put(url, json=json, timeout=self.timeout)
        return self._handle_response(response)

    def patch(self, endpoint: str, json: Optional[Dict[str, Any]] = None) -> Any:
        """Make a PATCH request."""
        url = self._build_url(endpoint)
        response = self.session.patch(url, json=json, timeout=self.timeout)
        return self._handle_response(response)

    def delete(self, endpoint: str) -> Any:
        """Make a DELETE request."""
        url = self._build_url(endpoint)
        response = self.session.delete(url, timeout=self.timeout)
        return self._handle_response(response)

    def close(self):
        """Close the session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
