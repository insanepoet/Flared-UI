from FlaredUI.Modules.Errors import CustomFlaskError


# --- Cloudflare API Errors ---
class CloudflareError(CustomFlaskError):
    """Base class for Cloudflare errors."""
    pass


class CloudflareBadRequestError(CloudflareError):
    """Raised when a Cloudflare API request is invalid."""
    status_code = 400


class CloudflareUnauthorizedError(CloudflareError):
    """Raised when the Cloudflare API credentials are invalid."""
    status_code = 401


class CloudflareForbiddenError(CloudflareError):
    """Raised when the API key does not have permissions for the requested operation."""
    status_code = 403


class CloudflareNotFoundError(CloudflareError):
    """Raised when the requested Cloudflare resource is not found."""
    status_code = 404


class CloudflareRateLimitError(CloudflareError):
    """Raised when the Cloudflare API rate limit is exceeded."""
    status_code = 429


class CloudflareClientError(CloudflareError):
    """Base class for Cloudflare client errors (4xx status codes)."""
    status_code = 400


class CloudflareServerError(CloudflareError):
    """Base class for Cloudflare server errors (5xx status codes)."""
    status_code = 500

# --- Cloudflare tunnel Errors
class CloudflareTunnelError(CustomFlaskError):
    """Base class for errors related to Cloudflare Tunnels."""
    pass


class CloudflareTunnelNameError(CloudflareTunnelError):
    """Raised when a tunnel name is invalid."""
    pass

class CloudflareTunnelCredentialsError(CloudflareTunnelError):
    """Raised when cloudflared credentials are invalid or not found."""
    pass


class CloudflareTunnelConnectionError(CloudflareTunnelError):
    """Raised when a connection to the cloudflared daemon cannot be established."""
    pass