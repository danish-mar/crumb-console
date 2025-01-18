from flask import Blueprint

from app import get_db

test_route = Blueprint('test_route', __name__)

@test_route.route('/test-db')
def test_db():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT 1;")  # Test query to check connection
        return "Database connection is working!"
    except Exception as e:
        return f"Error: {e}"
