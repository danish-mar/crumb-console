import logging
import threading
import time

import mysql.connector
import mysql.connector.pooling
from flask import current_app
from flask_pymongo import PyMongo

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Thread-local storage for database connections
_thread_local = threading.local()
mysql_pool = None


def init_mysql_pool(app):
    """Initialize MySQL connection pool when the application starts."""
    global mysql_pool

    db_config = {
        "pool_name": "mypool",
        "pool_size": 5,
        "host": app.config['SERVER'],
        "port": app.config['PORT'],
        "database": app.config['DATABASE'],
        "user": app.config['USERNAME'],
        "password": app.config['PASSWORD'],
        "pool_reset_session": True,
        "connect_timeout": 30,
        "autocommit": True  # Enable autocommit mode
    }

    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            mysql_pool = mysql.connector.pooling.MySQLConnectionPool(**db_config)
            logger.info("MySQL connection pool initialized successfully")
            return
        except mysql.connector.Error as err:
            if attempt == max_retries - 1:
                logger.error(f"Failed to create connection pool after {max_retries} attempts: {err}")
                raise
            logger.warning(f"Attempt {attempt + 1} failed, retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)


def get_db():
    global mysql_pool
    print("getting new connection")

    if mysql_pool is None:
        logger.error("MySQL connection pool is not initialized.")
        init_mysql_pool(current_app)
        if mysql_pool is None:
            raise Exception("Failed to initialize MySQL pool")

    if not hasattr(_thread_local, 'db'):
        try:
            conn = mysql_pool.get_connection()
            if conn is None:
                raise Exception("Failed to get connection from pool")

            _thread_local.db = conn
            logger.debug("Retrieved new connection from pool.")

            # Test the connection
            try:
                conn.ping(reconnect=True)
                logger.debug("Connection is alive.")
            except mysql.connector.Error:
                logger.warning("Connection ping failed; retrieving a new connection.")
                conn = mysql_pool.get_connection()
                if conn is None:
                    raise Exception("Failed to get new connection after ping failure")
                _thread_local.db = conn
        except mysql.connector.Error as err:
            logger.error(f"Error getting database connection: {err}")
            raise

    return _thread_local.db




def close_db(e=None):
    """Close MySQL connection and return it to the pool."""
    db = getattr(_thread_local, 'db', None)
    if db is not None:
        try:
            db.close()
            delattr(_thread_local, 'db')
            logger.debug("MySQL connection returned to pool")
        except mysql.connector.Error as err:
            logger.error(f"Error closing MySQL connection: {err}")


def get_mongo_db():
    """Get MongoDB connection."""
    if not hasattr(_thread_local, 'mongo_db'):
        try:
            mongo = PyMongo(app=current_app, uri=current_app.config['MONGO_URI'])
            _thread_local.mongo_db = mongo.db
            logger.debug("MongoDB connection established")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            raise
    return _thread_local.mongo_db


def close_mongo_db(e=None):
    """Close MongoDB connection."""
    if hasattr(_thread_local, 'mongo_db'):
        delattr(_thread_local, 'mongo_db')
        logger.info("Closing MongoDB connection")


def init_app(app):
    """Initialize the database connections with the Flask app."""
    try:
        init_mysql_pool(app)

        # Register connection closing with the application
        app.teardown_appcontext(close_db)
        app.teardown_appcontext(close_mongo_db)

        # Register before_request handler to ensure connection is valid
        @app.before_request
        def ensure_db_connection():
            db = get_db()
            try:
                db.ping(reconnect=True)
            except:
                close_db()
                _ = get_db()  # Get a fresh connection

        logger.info("Database connections initialized with application")
    except Exception as e:
        logger.error(f"Error initializing database connections: {e}")
        raise
