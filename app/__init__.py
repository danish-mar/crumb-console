from flask import Flask
from .config import config
from .db import init_app as init_db_app, get_db
from .utils.DatabaseWrapper import DatabaseWrapper
from .routes.customer_routes import init_customer_manager
from .routes.dashboard_routes import init_dashboard_controller
from .routes.order_routes import init_order_manager
from .routes.product_routes import init_product_manager


def validate_db_connection(connection):
    """
    Validate the database connection by attempting a simple operation.
    """
    try:
        connection.ping(reconnect=True)  # Ensure the connection is active

    except Exception as e:
        raise Exception(f"Database connection validation failed: {e}")


def create_app(config_name='prod'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize the database connections
    init_db_app(app)

    # Register blueprints
    from .routes.order_routes import order_blueprint
    app.register_blueprint(order_blueprint)

    from .routes.routes import app as app_blueprint
    app.register_blueprint(app_blueprint)

    from .routes.dashboard_routes import dash_routes
    app.register_blueprint(dash_routes)

    from .routes.product_routes import product_blueprint
    app.register_blueprint(product_blueprint)

    from .routes.customer_routes import customer_routes
    app.register_blueprint(customer_routes)

    from .routes.report import receipts_bp
    app.register_blueprint(receipts_bp)

    with app.app_context():
        try:

            # Initialize managers with the pool instead of a single connection
            init_product_manager(get_db())
            init_order_manager(get_db())
            init_dashboard_controller(get_db())
            init_customer_manager(get_db())

        except Exception as e:
            app.logger.error(f"Error initializing services: {e}")
            raise

    return app

