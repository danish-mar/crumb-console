import unittest
from unittest.mock import patch, MagicMock
from app.auth.SessionManager import SessionManager
from pymongo.errors import PyMongoError
from datetime import datetime, timedelta, UTC
from flask import Flask

class TestSessionManager(unittest.TestCase):

    @patch('app.auth.SessionManager.MongoClient')
    def setUp(self, mock_mongo_client):
        self.app = Flask(__name__)
        self.app.config['MONGO_URI'] = 'mongodb://localhost:27017'
        self.app.config['MONGO_DATABASE'] = 'test_db'
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.session_manager = SessionManager()

    def tearDown(self):
        self.app_context.pop()

    @patch('app.auth.SessionManager.MongoClient')
    def create_session_creates_new_session(self, mock_mongo_client):
        mock_mongo_client().sessions.insert_one.return_value.inserted_id = 'session_id'
        result = self.session_manager.create_session('user_id', 'session_id')
        self.assertEqual(result, 'session_id')

    @patch('app.auth.SessionManager.MongoClient')
    def create_session_handles_exception(self, mock_mongo_client):
        mock_mongo_client().sessions.insert_one.side_effect = PyMongoError("Insert error")
        result = self.session_manager.create_session('user_id', 'session_id')
        self.assertIsNone(result)

    @patch('app.auth.SessionManager.MongoClient')
    def get_session_returns_session(self, mock_mongo_client):
        mock_mongo_client().sessions.find_one.return_value = {'session_id': 'session_id', 'user_id': 'user_id'}
        result = self.session_manager.get_session('session_id')
        self.assertEqual(result, {'session_id': 'session_id', 'user_id': 'user_id'})

    @patch('app.auth.SessionManager.MongoClient')
    def get_session_handles_exception(self, mock_mongo_client):
        mock_mongo_client().sessions.find_one.side_effect = PyMongoError("Find error")
        result = self.session_manager.get_session('session_id')
        self.assertIsNone(result)

    @patch('app.auth.SessionManager.MongoClient')
    def delete_session_deletes_session(self, mock_mongo_client):
        mock_mongo_client().sessions.delete_one.return_value.deleted_count = 1
        result = self.session_manager.delete_session('session_id')
        self.assertTrue(result)

    @patch('app.auth.SessionManager.MongoClient')
    def delete_session_handles_exception(self, mock_mongo_client):
        mock_mongo_client().sessions.delete_one.side_effect = PyMongoError("Delete error")
        result = self.session_manager.delete_session('session_id')
        self.assertFalse(result)

    @patch('app.auth.SessionManager.MongoClient')
    def delete_expired_sessions_deletes_expired_sessions(self, mock_mongo_client):
        mock_mongo_client().sessions.delete_many.return_value.deleted_count = 1
        result = self.session_manager.delete_expired_sessions()
        self.assertTrue(result)

    @patch('app.auth.SessionManager.MongoClient')
    def delete_expired_sessions_handles_exception(self, mock_mongo_client):
        mock_mongo_client().sessions.delete_many.side_effect = PyMongoError("Delete error")
        result = self.session_manager.delete_expired_sessions()
        self.assertFalse(result)

    @patch('app.auth.SessionManager.MongoClient')
    def get_user_sessions_returns_sessions(self, mock_mongo_client):
        mock_mongo_client().sessions.find.return_value = [{'session_id': 'session_id', 'user_id': 'user_id'}]
        result = self.session_manager.get_user_sessions('user_id')
        self.assertEqual(result, [{'session_id': 'session_id', 'user_id': 'user_id'}])

    @patch('app.auth.SessionManager.MongoClient')
    def get_user_sessions_handles_exception(self, mock_mongo_client):
        mock_mongo_client().sessions.find.side_effect = PyMongoError("Find error")
        result = self.session_manager.get_user_sessions('user_id')
        self.assertIsNone(result)

    @patch('app.auth.SessionManager.MongoClient')
    def validate_session_returns_true_for_valid_session(self, mock_mongo_client):
        mock_mongo_client().sessions.find_one.return_value = {'session_id': 'session_id',
                                                              'expires_at': datetime.now(UTC) + timedelta(hours=1)}
        result = self.session_manager.validate_session('session_id')
        self.assertTrue(result)

    @patch('app.auth.SessionManager.MongoClient')
    def validate_session_returns_false_for_invalid_session(self, mock_mongo_client):
        mock_mongo_client().sessions.find_one.return_value = {'session_id': 'session_id',
                                                              'expires_at': datetime.now(UTC) - timedelta(hours=1)}
        result = self.session_manager.validate_session('session_id')
        self.assertFalse(result)

    @patch('app.auth.SessionManager.MongoClient')
    def validate_session_handles_exception(self, mock_mongo_client):
        mock_mongo_client().sessions.find_one.side_effect = PyMongoError("Find error")
        result = self.session_manager.validate_session('session_id')
        self.assertFalse(result)

    @patch('app.auth.SessionManager.MongoClient')
    def close_closes_mongo_client(self, mock_mongo_client):
        self.session_manager.close()
        mock_mongo_client().close.assert_called_once()


if __name__ == '__main__':
    unittest.main()