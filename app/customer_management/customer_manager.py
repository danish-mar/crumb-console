from pymongo import MongoClient
from bson.objectid import ObjectId
from app.utils.hash_utils import hash_password


class UserManager:
    def __init__(self, db_connection):
        """
        Initialize UserManager with a MongoDB connection.
        :param db_connection: A MongoDB client connection.
        """
        self.db = db_connection
        self.collection = self.db['users']  # Replace 'users' with your MongoDB collection name

    def create_user(self, first_name, last_name, email, phone, password, default_location, role="customer", auth_provider="manual"):
        """
        Create a new user.
        """
        try:
            hashed_password = hash_password(password)  # Hash the password
            user = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "password": hashed_password,
                "default_location": default_location,
                "role": role,
                "auth_provider": auth_provider
            }
            result = self.collection.insert_one(user)
            return str(result.inserted_id)
        except Exception as e:
            raise Exception(f"Error creating user: {e}")

    def get_user_by_id(self, user_id):
        """
        Retrieve user information by user ID.
        """
        try:
            user = self.collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user["_id"] = str(user["_id"])  # Convert ObjectId to string
            return user
        except Exception as e:
            raise Exception(f"Error fetching user by ID: {e}")

    def get_user_by_email(self, email):
        """
        Retrieve user information by email.
        """
        try:
            user = self.collection.find_one({"email": email})
            if user:
                user["_id"] = str(user["_id"])  # Convert ObjectId to string
            return user
        except Exception as e:
            raise Exception(f"Error fetching user by email: {e}")

    def update_user(self, user_id, **kwargs):
        """
        Update user details.
        """
        try:
            if 'password' in kwargs:
                kwargs['password'] = hash_password(kwargs['password'])  # Hash the password if it's being updated
            update_query = {"$set": kwargs}
            result = self.collection.update_one({"_id": ObjectId(user_id)}, update_query)
            if result.matched_count == 0:
                raise Exception("No user found to update.")
            return result.modified_count
        except Exception as e:
            raise Exception(f"Error updating user: {e}")

    def delete_user(self, user_id):
        """
        Delete a user.
        """
        try:
            result = self.collection.delete_one({"_id": ObjectId(user_id)})
            if result.deleted_count == 0:
                raise Exception("No user found to delete.")
            return result.deleted_count
        except Exception as e:
            raise Exception(f"Error deleting user: {e}")
