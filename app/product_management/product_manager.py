# product_manager.py
import mysql
import mysql.connector


class ProductManager:
    def __init__(self, db_connection):
        """Initialize ProductManager with a database connection."""
        print("Initializing Product Manager")
        self.db = db_connection

    def get_cursor(self):
        """Get a new cursor, ping the connection first to ensure it's alive."""
        self.db.ping(reconnect=True)
        return self.db.cursor(dictionary=True)

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
            cursor = self.get_cursor()
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