import requests

from FlaredUI.Modules.Errors import CloudflareBadRequestError, CloudflareUnauthorizedError, CloudflareForbiddenError, CloudflareNotFoundError, CloudflareRateLimitError, CloudflareClientError, CloudflareServerError


class CloudflareAPI:
    """A class to interact with the Cloudflare API."""

    def __init__(self, api_key):
        """
        Initializes the CloudflareAPI object.

        :param api_key: The Cloudflare API key.
        """
        self.api_key = api_key
        self.base_url = "https://api.cloudflare.com/client/v4"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def make_request(self, method, endpoint, params=None, data=None):
        """
        Makes a request to the Cloudflare API.

        :param method: The HTTP method (GET, POST, PUT, DELETE).
        :param endpoint: The API endpoint.
        :param params: Query parameters.
        :param data: Request payload (JSON).
        :return: The JSON response from the API, or raises an error if the request fails.
        """
        url = f"{self.base_url}/{endpoint}"
        response = requests.request(method, url, headers=self.headers, params=params, json=data)

        # Handle Errors
        if response.status_code == 400:  # Bad Request
            raise CloudflareBadRequestError(response.json().get("errors"))
        elif response.status_code == 401:  # Unauthorized
            raise CloudflareUnauthorizedError(response.json().get("errors"))
        elif response.status_code == 403:  # Forbidden
            raise CloudflareForbiddenError(response.json().get("errors"))
        elif response.status_code == 404:  # Not Found
            raise CloudflareNotFoundError(response.json().get("errors"))
        elif response.status_code == 429:  # Too Many Requests
            raise CloudflareRateLimitError(response.json().get("errors"))
        elif 400 <= response.status_code < 500:  # Other client errors
            raise CloudflareClientError(response.json().get("errors"))
        elif response.status_code >= 500:  # Server errors
            raise CloudflareServerError(response.json().get("errors"))

        # Try to return JSON, but if it fails (e.g., not a valid JSON response), return raw text
        try:
            return response.json()
        except ValueError:
            return response.text()