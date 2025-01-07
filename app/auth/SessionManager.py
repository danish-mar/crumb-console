import uuid
from datetime import datetime, timedelta, UTC

import pytz
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from flask import current_app


class SessionManager:
    def __init__(self, db_uri, db_name):
        """Initialize the SessionManager with a MongoDB connection."""
        self.client = MongoClient(db_uri)
        self.db = self.client[db_name]
        self.sessions = self.db.sessions

    def create_session(self, user_id, expires_in_hours=24):
        """Creates a new session for a user."""
        try:
            session_id = str(uuid.uuid4())
            expires_at = datetime.now(UTC) + timedelta(hours=expires_in_hours)
            session = {
                "session_id": session_id,
                "user_id": user_id,
                "expires_at": expires_at
            }
            self.sessions.insert_one(session)

            return session_id  # Return the new session's ID
        except PyMongoError as e:
            print(f"Error creating session: {e}")
            return None

    def get_session(self, session_id):
        """Fetches a session by its session ID."""
        try:
            session = self.sessions.find_one({"session_id": session_id})
            return session
        except PyMongoError as e:
            print(f"Error fetching session: {e}")
            return None

    def delete_session(self, session_id):
        """Deletes a session by its session ID."""
        try:
            result = self.sessions.delete_one({"session_id": session_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            print(f"Error deleting session: {e}")
            return False

    def delete_expired_sessions(self):
        """Deletes all expired sessions."""
        try:
            result = self.sessions.delete_many({"expires_at": {"$lt": datetime.now(UTC)}})
            return result.deleted_count > 0
        except PyMongoError as e:
            print(f"Error deleting expired sessions: {e}")
            return False

    def get_user_sessions(self, user_id):
        """Fetches all sessions for a specific user."""
        try:
            sessions = list(self.sessions.find({"user_id": user_id}))
            return sessions
        except PyMongoError as e:
            print(f"Error fetching user sessions: {e}")
            return None

    def validate_session(self, session_id):
        """Validates if a session is active."""
        session = self.get_session(session_id)
        print(session)
        if not session:
            return False
        expires_at = session["expires_at"]

        # Convert datetime.now(UTC) to naive datetime
        current_time = datetime.now(pytz.UTC).replace(tzinfo=None)

        print(expires_at)
        return current_time < expires_at
