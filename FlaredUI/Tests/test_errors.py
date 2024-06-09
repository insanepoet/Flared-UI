# Tests/test_errors.py
import pytest
from FlaredUI.Modules.Errors import (
    CustomFlaskError, UnauthorizedError, NotImplementedError,
    TunnelNotFoundError, ContainerError, ContainerNotFoundOnServerError,
    ContainerNotFoundInDatabaseError, ContainerRetrievalError,
    ContainerUpdateError, ContainerManagerNotSupportedError,
    CloudflaredError, CloudflareAPIError, CloudflareBadRequestError,
    CloudflareUnauthorizedError, CloudflareForbiddenError,
    CloudflareNotFoundError, CloudflareRateLimitError, CloudflareTunnelError,
    CloudflareTunnelNameError, CloudflareTunnelCredentialsError,
    CloudflareTunnelConnectionError, CloudflareServiceError, VMError,
    VMRetrievalError, VMNotFound, VMManagerError, ESXiError,
    NutanixError, OpenstackError, ProxmoxError, TrueNASVMError,
    XCPNgError, XenError, PluginError, PluginRepositoryError,
    PluginNotFoundError, PluginInvalidOperationError,
    PluginRepositoryNotFoundError, PluginRepositoryInvalidOperationError,
    ServerError, ServerNotFoundError, ServerCreationError, ServerUpdateError,
    ServerDeletionError, ServerManagerNotSupportedError
)
from flask import jsonify


def test_custom_flask_error_to_dict():
    error = CustomFlaskError("Test error", 400, {'detail': 'Additional details'})
    error_dict = error.to_dict()
    assert error_dict["message"] == "Test error"
    assert error_dict["status_code"] == 400
    assert error_dict["detail"] == "Additional details"


# Test UnauthorizedError
def test_unauthorized_error():
    with pytest.raises(UnauthorizedError) as excinfo:
        raise UnauthorizedError()
    assert excinfo.value.status_code == 401
    assert "Unauthorized" in str(excinfo.value)


# Test NotImplementedError
def test_not_implemented_error():
    with pytest.raises(NotImplementedError) as excinfo:
        raise NotImplementedError()
    assert excinfo.value.status_code == 501
    assert "Not Implemented" in str(excinfo.value)


# Test TunnelNotFoundError
def test_tunnel_not_found_error():
    with pytest.raises(TunnelNotFoundError) as excinfo:
        raise TunnelNotFoundError()
    assert excinfo.value.status_code == 404
    assert "Tunnel not found" in str(excinfo.value)


# --- Container Errors ---
def test_container_not_found_on_server_error():
    with pytest.raises(ContainerNotFoundOnServerError) as excinfo:
        raise ContainerNotFoundOnServerError()
    assert excinfo.value.status_code == 404
    assert "Container not found on server" in str(excinfo.value)


def test_container_not_found_in_database_error():
    with pytest.raises(ContainerNotFoundInDatabaseError) as excinfo:
        raise ContainerNotFoundInDatabaseError()
    assert excinfo.value.status_code == 404
    assert "Container not found in database" in str(excinfo.value)


def test_container_retrieval_error():
    with pytest.raises(ContainerRetrievalError) as excinfo:
        raise ContainerRetrievalError()
    assert excinfo.value.status_code == 500
    assert "Error retrieving container" in str(excinfo.value)


def test_container_update_error():
    with pytest.raises(ContainerUpdateError) as excinfo:
        raise ContainerUpdateError()
    assert excinfo.value.status_code == 500
    assert "Error updating container" in str(excinfo.value)


def test_container_manager_not_supported_error():
    with pytest.raises(ContainerManagerNotSupportedError) as excinfo:
        raise ContainerManagerNotSupportedError()
    assert excinfo.value.status_code == 501
    assert "Container manager not supported" in str(excinfo.value)


# --- Cloudflare Errors ---
def test_cloudflare_api_error():
    error = CloudflareAPIError("Test Cloudflare API Error", 500)
    assert error.status_code == 500
    assert "Test Cloudflare API Error" in str(error)


def test_cloudflare_bad_request_error():
    error = CloudflareBadRequestError()
    assert error.status_code == 400
    assert "Bad request to Cloudflare API" in str(error)


def test_cloudflare_unauthorized_error():
    error = CloudflareUnauthorizedError()
    assert error.status_code == 401
    assert "Unauthorized access to Cloudflare API" in str(error)


def test_cloudflare_forbidden_error():
    error = CloudflareForbiddenError()
    assert error.status_code == 403
    assert "Forbidden access to Cloudflare API" in str(error)


def test_cloudflare_not_found_error():
    error = CloudflareNotFoundError()
    assert error.status_code == 404
    assert "Resource not found on Cloudflare" in str(error)


def test_cloudflare_rate_limit_error():
    error = CloudflareRateLimitError()
    assert error.status_code == 429
    assert "Cloudflare API rate limit exceeded" in str(error)


# --- Cloudflared Errors ---
def test_cloudflared_error():
    error = CloudflaredError("Test Cloudflared Error", 500)
    assert error.status_code == 500
    assert "Test Cloudflared Error" in str(error)


def test_cloudflare_tunnel_name_error():
    error = CloudflareTunnelNameError()
    assert error.status_code == 400
    assert "Tunnel name is invalid" in str(error)


def test_cloudflare_tunnel_credentials_error():
    error = CloudflareTunnelCredentialsError()
    assert error.status_code == 401
    assert "Invalid or missing Cloudflare credentials" in str(error)


def test_cloudflare_tunnel_connection_error():
    error = CloudflareTunnelConnectionError()
    assert error.status_code == 503
    assert "Could not connect to cloudflared" in str(error)


def test_cloudflare_service_error():
    error = CloudflareServiceError()
    assert error.status_code == 500
    assert "Error communicating with Cloudflare" in str(error)
