from flask_login import UserMixin, current_user
from cachetools import cached, TTLCache
from FlaredUI.Modules.DB.Models import User as UserModel, OAuth as OAuthModel
from FlaredUI.Modules.DB import db
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from FlaredUI.Modules.DB.Schemas import UserSchema
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from FlaredUI.Modules.Errors import UserNotFoundError
from FlaredUI.Logging import get_logger


logger = get_logger(__name__)


class User(UserMixin):
    """Represents a user in the application (adapted for Flask-Login)."""

    def __init__(self, user_model):
        self.id = user_model.id
        self.username = user_model.username
        self.email = user_model.email
        self.password_hash = user_model.password_hash

    @cached(cache=TTLCache(maxsize=1024, ttl=300))
    def get_by_username(username):
        """Retrieves a user by their username."""

        try:
            return UserModel.query.filter_by(username=username).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            raise Exception("Database error")

    def create_user(data):
        """Create a user in the database"""

        try:
            # Validate input data
            UserSchema().load(data)

            hashed_password = generate_password_hash(data['password'])  # Hash the password
            new_user = UserModel(
                username=data['username'],
                email=data['email'],
                password_hash=hashed_password
            )
            db.session.add(new_user)
            db.session.commit()
            return new_user
        except ValidationError as err:
            logger.error(f"Validation error creating user: {err.messages}")
            raise ValueError(err.messages)  # You can raise a more specific error if needed
        except IntegrityError:  # Handle unique constraint violations
            db.session.rollback()
            raise ValueError("Username or email already exists.")
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Database error: {e}")

    @cached(cache=TTLCache(maxsize=1024, ttl=300))
    def get_user_by_id(user_id):
        """Retrieves a user by their ID."""

        try:
            user = UserModel.query.get(user_id)
            if not user:
                raise UserNotFoundError(f"User with ID {user_id} not found")
            return user
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            raise Exception("Database error")

    @cached(cache=TTLCache(maxsize=1024, ttl=300))
    def get_user_by_email(email):
        """Retrieves a user by their email."""

        try:
            return UserModel.query.filter_by(email=email).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            raise Exception("Database error")

    # Flask-Login required methods:
    def is_authenticated(self):
        return True

    def is_active(self):
        return True  # You can add custom logic here to check for account activation, etc.

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def check_password(self, password):
        """Check if the provided password matches the hashed password."""
        return check_password_hash(self.password_hash, password)


# --- Helper function to get or create an OAuth user ---
def get_or_create_oauth_user(user_data):
    """Gets or creates a user based on OAuth data."""
    if current_user.is_authenticated and current_user.oauth:
        return current_user

    oauth = OAuthModel.query.filter_by(  # Corrected to OAuthModel
        provider_id=user_data['provider_id'],
        oauth_id=user_data['oauth_id']
    ).first()

    if oauth:
        return oauth.user  # User already exists, return it

    try:
        new_user = UserModel(
            username=user_data['username'],
            email=user_data['email']  # Email from OAuth provider (ensure it's unique)
        )

        new_oauth = OAuthModel(
            provider_id=user_data['provider_id'],
            oauth_id=user_data['oauth_id']
        )
        new_user.oauth = new_oauth

        db.session.add(new_user)
        db.session.add(new_oauth)
        db.session.commit()
        return new_user
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Failed to create OAuth user. Ensure email is unique.")
    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception(f"Database error: {e}")
