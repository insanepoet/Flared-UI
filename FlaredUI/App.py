import os
from flask import Flask, jsonify, request
from flask_login import LoginManager, current_user
from flasgger import Swagger, LazyString, LazyJSONEncoder
from FlaredUI.Config import config, DatabaseURI
from FlaredUI.Modules.DB import init_db, Settings, get_api_key_by_value, User, db
from FlaredUI.Modules.Auth.OAuth import init_oauth
from FlaredUI.Logging.Init_Logging import initialize_logging
from FlaredUI.Routes import api_bp


# Create the Flask app
app = Flask(__name__)


# Initialize Logging
logger = initialize_logging()


# Load configuration
app.config.from_object(config.get(os.environ.get("FLASK_ENV") or "default"))
app.json_encoder = LazyJSONEncoder

# Initialize Database
init_db(app)


# Database setup
if not app.config['SQLALCHEMY_DATABASE_URI']:
    app.config['SQLALCHEMY_DATABASE_URI'] = DatabaseURI().build_uri()
db.init_app(app)


# Initialize OAuth after the database is initialized
init_oauth(app)


# Swagger configuration
app.config["SWAGGER"] = {
    "title": "Flared-UI API",
    "uiversion": 3,
}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/apispec_1.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/Docs/",
}
template = dict(
    swaggerUiPrefix=LazyString(lambda: request.environ.get("HTTP_X_SCRIPT_NAME", ""))
)

# Initialize Flasgger Swagger
swagger = Swagger(app, config=swagger_config, template=template)

# Register the main api_bp blueprint
app.register_blueprint(api_bp, url_prefix="/api")


@login_manager.user_loader
def load_user(user_id):
    return User.get_user_by_id(int(user_id))


# Example route for the main page
@app.route('/')
def index():
    """Route for the index page. Requires authentication or returns a message."""
    if not current_user.is_authenticated:
        return jsonify({"message": "Please log in to access the Flared-UI Backend."}), 401
    else:
        return jsonify({"message": "Welcome to the Flared-UI Backend, there isn't much to see here."}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)