from flask_login import current_user
from FlaredUI.Modules.DB.ApiKeys import get_api_key_by_value

from .. import logger
from .UserPass import User
from ..DB import db


def load_user_from_api_key(request):
    """Loads the user based on the API key from the request header."""
    api_key_value = request.headers.get('X-API-Key')

    if api_key_value:
        # Sanitize the API key value (e.g., remove potentially harmful characters)
        api_key_value = api_key_value.strip()  # Remove leading/trailing whitespace

        api_key = get_api_key_by_value(api_key_value)
        if api_key:
            user = api_key.user
            if user and user.is_active:
                # Log successful login to main_file
                logger.info(f"{user.username} logged in using API key.")
                return user
    # Authentication failed, log to auth_file (propagate=False prevents logging to main_file)
    logger.warning(f"API Key authentication failed for key: {api_key_value if api_key_value else 'None'}")
    return None  # Return None if authentication fails
