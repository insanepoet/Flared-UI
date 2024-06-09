import os
import yaml
from pathlib import Path
from cryptography.fernet import Fernet
import base64


class Config:

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    _SECRET_KEY_ENV_VAR = 'APP_SECRET_KEY'
    _ENCRYPTION_KEY_ENV_VAR = 'APP_ENCRYPTION_KEY'

    if _SECRET_KEY_ENV_VAR not in os.environ:
        secret_key = os.urandom(32)
        os.environ[_SECRET_KEY_ENV_VAR] = base64.b64encode(secret_key).decode('utf-8')
        print("NEW Secret Key Generated")
    SECRET_KEY = base64.b64decode(os.environ.get(_SECRET_KEY_ENV_VAR))

    if _ENCRYPTION_KEY_ENV_VAR not in os.environ:
        encryption_key = Fernet.generate_key()
        os.environ[_ENCRYPTION_KEY_ENV_VAR] = base64.b64encode(encryption_key).decode('utf-8')
        print("NEW Encryption Key Generated")
    encryption_key = base64.b64decode(os.environ.get(_ENCRYPTION_KEY_ENV_VAR))

    def __init__(self, config_path):
        self._config_path = config_path
        self._data = self._load_config()

    def _load_config(self):
        """Loads configuration from the YAML file."""
        with open(self._config_path, 'r') as f:
            return yaml.safe_load(f)

    def get(self, key, default=None):
        """Retrieves a configuration value by key."""
        return self._data.get(key, default)

    def set(self, key, value):
        """Sets a configuration value."""
        self._data[key] = value

    def save(self):
        """Saves the modified configuration back to the YAML file."""
        with open(self._config_path, 'w') as f:
            yaml.dump(self._data, f)


class DatabaseURI:
    """Builds a database URI string from environment variables."""
    def __init__(self):
        self.dialect = os.environ.get('DATABASE_DIALECT')
        self.driver = os.environ.get('DATABASE_DRIVER', '')
        self.username = os.environ.get('DATABASE_USER')
        self.password = os.environ.get('DATABASE_PASSWORD')
        self.host = os.environ.get('DATABASE_HOST')
        self.port = os.environ.get('DATABASE_PORT')
        self.database = os.environ.get('DATABASE_NAME')

        # If required env vars are not set, create them for the default SQLite database
        if not all([self.dialect, self.username, self.password, self.host, self.database]):
            self._set_sqlite_defaults()
            # reload variables
            self.dialect = os.environ.get('DATABASE_DIALECT')
            self.database = os.environ.get('DATABASE_NAME')

    def _set_sqlite_defaults(self):
        """Sets default values for SQLite if environment variables are not set."""
        base_dir = Path(__file__).resolve().parent.parent
        os.environ['DATABASE_DIALECT'] = 'sqlite'
        os.environ['DATABASE_NAME'] = str(base_dir / 'Data' / 'FlaredDB.db')

    def build_uri(self):
        """Constructs and returns the database URI string."""
        if self.dialect == 'sqlite':
            return f"sqlite:///{self.database}"  # SQLite doesn't need credentials
        else:
            return f"{self.dialect}+{self.driver}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class DevelopmentConfig(Config):
    DEBUG = True
    BASE_DIR = Path(__file__).resolve().parent.parent
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(BASE_DIR / 'Data' / 'FlaredDB.db')
    # Uncomment and fill in if you want to test with another database type in development
    # SQLALCHEMY_DATABASE_URI = DatabaseURI().build_uri()


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = DatabaseURI().build_uri()  # Always build URI from env vars in production


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
