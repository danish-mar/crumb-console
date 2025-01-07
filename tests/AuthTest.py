import pytest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from flask import Flask, jsonify, request
from werkzeug.test import Client
from functools import wraps

# Import your actual decorator

from functools import wraps
from flask import request, jsonify, current_app
from app.db import get_mongo_db
from pymongo import MongoClient
from bson import ObjectId


def session_authenticated(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Retrieve session ID from the cookies
        session_id = request.cookies.get('X-Auth-Token')
        if not session_id:
            return jsonify({"error": "Unauthorized access, session ID missing"}), 401

        db = get_mongo_db()
        try:
            # Validate session ID in the web_sessions collection
            session_data = db.web_sessions.find_one({"_id": ObjectId(session_id)})

            if not session_data:
                return jsonify({"error": "Invalid session ID, please log in again"}), 401

            # Store the user ID in the request context for use in the route
            request.user_id = session_data['user_id']

        except Exception as e:
            return jsonify({"error": "Database error", "details": str(e)}), 500

        # Proceed to the actual route function
        return func(*args, **kwargs)

    return wrapper


# Create Flask test app
@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/alpha'

    # Test route using the decorator
    @app.route('/protected')
    @session_authenticated
    def protected_route():
        return jsonify({"message": "Success", "user_id": str(request.user_id)})

    return app

@pytest.fixture
def client(app):
    return app.test_client()

# Mock database for testing
@pytest.fixture
def mock_db():
    with patch('your_module.get_mongo_db') as mock:
        db = MagicMock()
        mock.return_value = db
        yield db

def test_missing_session_token(client):
    """Test when no session token is provided"""
    response = client.get('/protected')
    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized access, session ID missing"}

def test_invalid_session_token(client, mock_db):
    """Test when an invalid session token is provided"""
    session_id = str(ObjectId())
    mock_db.web_sessions.find_one.return_value = None

    response = client.get('/protected', headers={
        'Cookie': f'X-Auth-Token={session_id}'
    })

    assert response.status_code == 401
    assert response.json == {"error": "Invalid session ID, please log in again"}
    mock_db.web_sessions.find_one.assert_called_once_with({"_id": ObjectId(session_id)})

def test_valid_session_token(client, mock_db):
    """Test when a valid session token is provided"""
    session_id = str(ObjectId())
    user_id = str(ObjectId())

    mock_db.web_sessions.find_one.return_value = {
        "_id": ObjectId(session_id),
        "user_id": user_id
    }

    response = client.get('/protected', headers={
        'Cookie': f'X-Auth-Token={session_id}'
    })

    assert response.status_code == 200
    assert response.json == {"message": "Success", "user_id": user_id}
    mock_db.web_sessions.find_one.assert_called_once_with({"_id": ObjectId(session_id)})

def test_database_error(client, mock_db):
    """Test when database operation raises an exception"""
    session_id = str(ObjectId())
    mock_db.web_sessions.find_one.side_effect = Exception("Database connection failed")

    response = client.get('/protected', headers={
        'Cookie': f'X-Auth-Token={session_id}'
    })

    assert response.status_code == 500
    assert response.json["error"] == "Database error"
    assert "Database connection failed" in response.json["details"]

def test_invalid_object_id(client, mock_db):
    """Test when session token is not a valid ObjectId"""
    response = client.get('/protected', headers={
        'Cookie': 'X-Auth-Token=invalid_object_id'
    })

    assert response.status_code == 500
    assert response.json["error"] == "Database error"
    assert "invalid_object_id" in response.json["details"].lower()

def test_request_user_id_set(client, mock_db):
    """Test that user_id is properly set in request context"""
    session_id = str(ObjectId())
    user_id = str(ObjectId())

    mock_db.web_sessions.find_one.return_value = {
        "_id": ObjectId(session_id),
        "user_id": user_id
    }

    with client as c:
        response = c.get('/protected', headers={
            'Cookie': f'X-Auth-Token={session_id}'
        })
        assert response.status_code == 200
        with client.application.request_context():
            assert request.user_id == user_id