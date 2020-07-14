from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


# Instantiate Flask extensions
db = SQLAlchemy()
migrate = Migrate()


# Initialize Flask Application
def create_app(extra_config_settings=None):
    """Create a Flask application.
    """
    extra_config_settings = extra_config_settings or {}

    # Instantiate Flask
    app = Flask(__name__)

    # Load common settings
    app.config.from_object('app.settings')
    # Load environment specific settings
    app.config.from_object('app.local_settings')
    # Load extra settings from extra_config_settings param
    app.config.update(extra_config_settings)

    # Setup Flask-SQLAlchemy
    db.init_app(app)

    # Setup Flask-Migrate
    migrate.init_app(app, db)

    # Register blueprints
    from .endpoints import register_blueprints
    register_blueprints(app)

    return app
