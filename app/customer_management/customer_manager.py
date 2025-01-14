import mysql.connector

from app.utils.hash_utils import hash_password, calculate_hash


class CustomerManager:
    def __init__(self, db_connection):
        self.db = db_connection
        self.cursor = self.db.cursor()

    # Create a new customer
    def create_customer(self, first_name, last_name, email, phone, password, default_location, role='customer',
                        status='active', auth_provider='manual', profile_pic_url='none', address_lat=None,
                        address_lon=None):
        hashed_password = hash_password(password)

        query = """
            INSERT INTO users (first_name, last_name, email, phone, password, default_location, role, status, auth_provider, profile_pic_url, address_lat, address_lon)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (first_name, last_name, email, phone, hashed_password, default_location, role, status, auth_provider,
                  profile_pic_url, address_lat, address_lon)
        try:
            self.cursor.execute(query, values)
            self.db.commit()
            return self.cursor.lastrowid  # Return the ID of the newly created customer
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None

    # Get customer by ID
    def get_customer_by_id(self, customer_id):
        query = "SELECT * FROM users WHERE id = %s"
        self.cursor.execute(query, (customer_id,))
        result = self.cursor.fetchone()
        if result:
            return result  # Return customer details as a tuple
        return None

    # Get customer by email
    def get_customer_by_email(self, email):
        query = "SELECT * FROM users WHERE email = %s"
        self.cursor.execute(query, (email,))
        result = self.cursor.fetchone()
        if result:
            return result  # Return customer details as a tuple
        return None

    def update_customer(self, customer_id, **kwargs):
        set_clauses = []
        update_values = []

        # Check if password is provided and hash it
        if 'password' in kwargs:
            kwargs['password'] = hash_password(kwargs['password'])

        # Loop through the kwargs dictionary and create SET clauses
        for field, value in kwargs.items():
            set_clauses.append(f"{field} = %s")
            update_values.append(value)

        if set_clauses:
            set_clause = ", ".join(set_clauses)
            update_values.append(customer_id)

            query = f"UPDATE users SET {set_clause} WHERE id = %s"
            try:
                self.cursor.execute(query, tuple(update_values))
                self.db.commit()
                return self.cursor.rowcount  # Return the number of rows updated
            except mysql.connector.Error as err:
                print(f"Error: {err}")
                return 0
        else:
            print("No fields provided to update.")
            return 0

    # Delete customer
    def delete_customer(self, customer_id):
        query = "DELETE FROM users WHERE id = %s"
        try:
            self.cursor.execute(query, (customer_id,))
            self.db.commit()
            return self.cursor.rowcount  # Return the number of rows deleted
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return 0

    # Get all customers
    def get_all_customers(self):
        query = "SELECT * FROM users"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result  # Return a list of all customers

