from FlaredUI.Modules.Errors.GeneralErrors import CustomFlaskError


class CloudflareError(CustomFlaskError):
    """Base class for all errors related to Cloudflare."""
    pass


# --- Cloudflare API Errors ---
class CloudflareAPIError(CloudflareError):
    """Base class for errors specifically related to the Cloudflare API."""
    pass


class CloudflareBadRequestError(CloudflareAPIError):
    """Raised when a Cloudflare API request is invalid (HTTP 400)."""

    def __init__(self, message="Bad request to Cloudflare API.", status_code=400, payload=None):
        super().__init__(message, status_code, payload)


class CloudflareUnauthorizedError(CloudflareAPIError):
    """Raised when the Cloudflare API credentials are invalid (HTTP 401)."""

    def __init__(self, message="Unauthorized access to Cloudflare API.", status_code=401, payload=None):
        super().__init__(message, status_code, payload)


class CloudflareForbiddenError(CloudflareAPIError):
    """Raised when the API key does not have permissions for the requested operation (HTTP 403)."""

    def __init__(self, message="Forbidden access to Cloudflare API.", status_code=403, payload=None):
        super().__init__(message, status_code, payload)


class CloudflareNotFoundError(CloudflareAPIError):
    """Raised when the requested Cloudflare resource is not found (HTTP 404)."""

    def __init__(self, message="Resource not found on Cloudflare.", status_code=404, payload=None):
        super().__init__(message, status_code, payload)


class CloudflareRateLimitError(CloudflareAPIError):
    """Raised when the Cloudflare API rate limit is exceeded (HTTP 429)."""

    def __init__(self, message="Cloudflare API rate limit exceeded.", status_code=429, payload=None):
        super().__init__(message, status_code, payload)


# --- Cloudflare Tunnel Errors --- (Cloudflared)
class CloudflaredError(CloudflareError):
    """Base class for errors related to Cloudflared."""
    pass

class CloudflareTunnelError(CloudflaredError):
    """Base class for errors related to Cloudflare Tunnels."""
    pass


class CloudflareTunnelNameError(CloudflareTunnelError):
    """Raised when a tunnel name is invalid."""
    def __init__(self, message="Tunnel name is invalid.", status_code=400, payload=None):
        super().__init__(message, status_code, payload)


class CloudflareTunnelCredentialsError(CloudflareTunnelError):
    """Raised when cloudflared credentials are invalid or not found."""

    def __init__(self, message="Invalid or missing Cloudflare credentials.", status_code=401, payload=None):
        super().__init__(message, status_code, payload)


class CloudflareTunnelConnectionError(CloudflareTunnelError):
    """Raised when a connection to the cloudflared daemon cannot be established."""

    def __init__(self, message="Could not connect to cloudflared.", status_code=503, payload=None):  # 503 Service Unavailable
        super().__init__(message, status_code, payload)


# --- Cloudflare General Errors ---
class CloudflareServiceError(CloudflareError):
    """Raised when there's a general error communicating with Cloudflare's services."""

    def __init__(self, message="Error communicating with Cloudflare.", status_code=500, payload=None):
        super().__init__(message, status_code, payload)
