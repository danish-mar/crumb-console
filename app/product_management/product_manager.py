# product_manager.py
import mysql
import mysql.connector

from app import get_db


class ProductManager:
    def __init__(self, db_connection):
        """Initialize ProductManager with a database connection."""
        if not db_connection:
            raise ValueError("Database connection cannot be None")

        self.db = db_connection
        print(f"Initializing Product Manager with: {self.db}")

    def ensure_connection(self):
        """Ensure the database connection is valid and active."""
        if not self.db:
            raise ValueError("Database connection is not initialized")

        try:
            self.db.ping(reconnect=True)
        except Exception as e:
            print(f"Connection error: {e}")
            # Try to get a new connection from the pool

            self.db = get_db()
            if not self.db:
                raise ValueError("Could not establish database connection")

    def get_cursor(self):
        """Get a new cursor, ensuring the connection is alive first."""
        print(f"Product manager getting cursor from: {self.db}")

        self.ensure_connection()

        try:
            cursor = self.db.cursor(dictionary=True)
            if not cursor:
                raise ValueError("Failed to create cursor")
            return cursor
        except Exception as e:
            print(f"Error creating cursor: {e}")
            raise

    def add_product(self, name, category_id, price, stock, description, is_available, weight_in_g, tags, image_url="Wil.jpg"):
        """Add a new product to the database."""
        cursor = None
        try:
            cursor = self.get_cursor()
            query = """
            INSERT INTO products (name, category, price, stock_quantity, description, created_at, is_available, weight, image_url, tags)
            VALUES (%s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s)
            """
            cursor.execute(query, (name, category_id, price, stock, description, is_available, weight_in_g, image_url, tags))
            self.db.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            self.db.rollback()
            raise Exception(f"MySQL error: {err}")
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error adding product: {e}")
        finally:
            if cursor:
                cursor.close()

    def update_product(self, product_id, **kwargs):
        """Update product attributes."""
        cursor = None
        try:
            cursor = self.get_cursor()
            # Filter out None values
            kwargs = {k: v for k, v in kwargs.items() if v is not None}
            if not kwargs:
                return

            set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
            query = f"UPDATE products SET {set_clause} WHERE id = %s"
            values = (*kwargs.values(), product_id)
            cursor.execute(query, values)
            self.db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error updating product: {e}")
        finally:
            if cursor:
                cursor.close()

    def delete_product(self, product_id):
        """Delete a product by ID."""
        cursor = None
        try:
            cursor = self.get_cursor()

            # Check if the product exists in order_details or review table
            check_query = """
            SELECT EXISTS(SELECT 1 FROM order_details WHERE product_id = %s) AS in_orders,
                   EXISTS(SELECT 1 FROM review WHERE product = %s) AS in_reviews
            """
            cursor.execute(check_query, (product_id, product_id))
            result = cursor.fetchone()

            # If the product exists in either order_details or review, raise an exception
            if result['in_orders'] or result['in_reviews']:
                print("Cannot delete product as it exists in order details or reviews.")
                raise Exception("Cannot delete product as it exists in order details or reviews.")

            # Attempt to delete the product from the products table
            query = "DELETE FROM products WHERE id = %s"
            cursor.execute(query, (product_id,))
            self.db.commit()

            # Return True if the deletion was successful, otherwise False
            return cursor.rowcount > 0
        except Exception as e:
            # Rollback the transaction in case of any errors
            self.db.rollback()
            raise Exception(f"{e}")
        finally:
            # Ensure the cursor is always closed
            if cursor:
                cursor.close()


    def get_product(self, product_id):
        """Get a product by ID."""
        cursor = None
        try:
            cursor = self.get_cursor()
            query = "SELECT * FROM products WHERE id = %s"
            cursor.execute(query, (product_id,))
            return cursor.fetchone()
        finally:
            if cursor:
                cursor.close()

    def add_category(self, name, description):
        """Add a new category to the database."""
        cursor = None
        try:
            cursor = self.get_cursor()
            query = "INSERT INTO product_category (name, description) VALUES (%s, %s)"
            cursor.execute(query, (name, description))
            self.db.commit()
            return cursor.lastrowid
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error adding category: {e}")
        finally:
            if cursor:
                cursor.close()

    def remove_category(self, category_id):
        """Remove a category by ID."""
        cursor = None
        try:
            cursor = self.get_cursor()
            query = "DELETE FROM product_category WHERE id = %s"
            cursor.execute(query, (category_id,))
            self.db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error removing category: {e}")
        finally:
            if cursor:
                cursor.close()

    def get_category(self, category_id):
        """Get a category by ID."""
        cursor = None
        try:
            cursor = self.get_cursor()
            query = "SELECT * FROM product_category WHERE id = %s"
            cursor.execute(query, (category_id,))
            return cursor.fetchone()
        finally:
            if cursor:
                cursor.close()

    def get_all_categories(self):
        """Get all categories."""
        cursor = None
        try:
            cursor = get_db().cursor(dictionary=True)
            query = "SELECT * FROM product_category"
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()

    def update_category(self, category_id, **kwargs):
        """Update category attributes."""
        cursor = None
        try:
            cursor = self.get_cursor()
            # Filter out None values
            kwargs = {k: v for k, v in kwargs.items() if v is not None}
            if not kwargs:
                return False

            set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
            query = f"UPDATE product_category SET {set_clause} WHERE id = %s"
            values = (*kwargs.values(), category_id)
            cursor.execute(query, values)
            self.db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error updating category: {e}")
        finally:
            if cursor:
                cursor.close()

    def fetch_all_products(self):
        """
        Fetches all products from the database, including their categories.

        Returns:
            A list of dictionaries, where each dictionary represents a product
            with its associated category name.
        """
        try:
            print(f"Fetching all products.")
            cursor = get_db().cursor(dictionary=True)
            print(cursor)

            # Execute the query to fetch all products with their categories
            query = """
                SELECT p.*, c.name as category_name
                FROM products p
                RIGHT JOIN product_category c ON p.category = c.id
                WHERE p.id IS NOT NULL AND p.name IS NOT NULL
            """
            cursor.execute(query)
            products = cursor.fetchall()

            return products
        except mysql.connector.Error as e:
            print(f"Error fetching products: {e}")
            raise Exception(f"Error fetching products: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise