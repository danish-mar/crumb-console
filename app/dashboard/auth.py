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
