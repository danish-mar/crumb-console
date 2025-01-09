import os
from flask import Flask, g
from .config import config
from .db import close_db, close_mongo_db, get_db  # Ensure `get_db` is defined properly
from .routes.product_routes import init_product_manager


def create_app(config_name='alpha'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Register blueprints
    from .routes.order_routes import order_blueprint, init_order_manager
    app.register_blueprint(order_blueprint)

    from .routes.routes import app as app_blueprint
    app.register_blueprint(app_blueprint)

    from .routes.report import receipts_bp
    app.register_blueprint(receipts_bp)

    from .routes.product_routes import product_blueprint
    app.register_blueprint(product_blueprint)

    # Initialize database connections after app context is available
    with app.app_context():
        # This ensures the database connection is created after the app is initialized
        db_connection = get_db()
        init_product_manager(db_connection) #  Initializes Product Manager
        init_order_manager(db_connection)  # Initialize OrderManager

    # Add teardown hooks
    app.teardown_appcontext(close_mongo_db)
    app.teardown_appcontext(close_db)

    return app
