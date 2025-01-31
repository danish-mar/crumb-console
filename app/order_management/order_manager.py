from datetime import datetime

import mysql.connector

from app import get_db


class OrderManager:
    def __init__(self, db_connection):
        """Initialize OrderManager with a database connection."""
        self.db = db_connection

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

    def get_order(self, order_id):
        """Get complete order details, including customer and product information."""

        cursor = None
        try:
            cursor = self.get_cursor()

            # Query to get order, customer, and product details
            query = """
            SELECT 
                o.id AS order_id,
                o.user_id,
                o.payment_method,
                o.order_place_date,
                o.expected_delivery_date,
                o.actual_delivery_date,
                o.is_completed,
                o.total,
                o.shipping_address,
                o.status,
                o.delivery_charges,
                od.id AS order_detail_id,
                od.product_id,
                od.quantity,
                od.price,
                od.subtotal,
                p.name AS product_name,
                p.category AS product_category,
                p.weight AS product_weight,
                p.image_url AS product_image_url,
                u.first_name AS customer_first_name,
                u.last_name AS customer_last_name,
                u.phone AS customer_phone,
                u.default_location AS customer_address
            FROM orders o
            LEFT JOIN order_details od ON o.id = od.order_id
            LEFT JOIN products p ON od.product_id = p.id
            LEFT JOIN users u ON o.user_id = u.id
            WHERE o.id = %s
            """

            # Execute query
            cursor.execute(query, (order_id,))

            # Fetch order and product details
            order = cursor.fetchone()

            if order:
                # Build order details
                order_data = {
                    'id': order['order_id'],
                    'user_id': order['user_id'],
                    'payment_method': order['payment_method'],
                    'order_place_date': order['order_place_date'],
                    'expected_delivery_date': order['expected_delivery_date'],
                    'actual_delivery_date': order['actual_delivery_date'],
                    'is_completed': order['is_completed'],
                    'total': order['total'],
                    'shipping_address': order['shipping_address'],
                    'status': order['status'],
                    'delivery_charges': order['delivery_charges'],
                    'customer': {
                        'first_name': order['customer_first_name'],
                        'last_name': order['customer_last_name'],
                        'phone': order['customer_phone'],
                        'address': order['customer_address']
                    },
                    'order_details': []
                }

                # List of products related to the order
                while order:
                    order_data['order_details'].append({
                        'order_detail_id': order['order_detail_id'],
                        'product_id': order['product_id'],
                        'quantity': order['quantity'],
                        'price': order['price'],
                        'subtotal': order['subtotal'],
                        'product': {
                            'name': order['product_name'],
                            'category': order['product_category'],
                            'weight': order['product_weight'],
                            'image_url': order['product_image_url']
                        }
                    })
                    # Fetch next product in the order (if exists)
                    order = cursor.fetchone()

                return order_data

        except Exception as e:
            raise Exception(f"Error getting order: {e}")
        finally:
            if cursor:
                cursor.close()

    from decimal import Decimal
    from datetime import datetime

    def get_all_orders(self):
        """Get all orders along with customer details."""
        cursor = None
        try:
            cursor = self.get_cursor()
            # # Diagnostic queries
            # cursor.execute("SELECT @@session.transaction_isolation")
            # isolation = cursor.fetchone()
            # print(f"Transaction isolation level: {isolation}")
            # Set isolation level to READ COMMITTED for this session
            cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

            cursor.execute("SELECT COUNT(*) as count FROM orders")
            count = cursor.fetchone()
            print(f"Total orders in database: {count['count']}")

            query = """
                SELECT 
                    o.id AS order_id,
                    o.order_place_date,
                    o.total,
                    o.status,
                    o.shipping_address,
                    o.delivery_charges,
                    o.expected_delivery_date,
                    o.actual_delivery_date,
                    o.is_completed,
                    o.payment_method,
                    u.first_name,
                    u.last_name,
                    u.email,
                    u.phone,
                    p.method_name AS payment_method_name
                FROM orders o
                JOIN users u ON o.user_id = u.id
                JOIN payment_methods p ON o.payment_method = p.id;
            """

            # Clear any existing cursor state
            cursor.execute("SELECT 1")  # Dummy query to clear any existing state
            cursor.fetchall()

            # Execute main query
            cursor.execute(query)
            orders = cursor.fetchall()
            print(f"Number of orders fetched: {len(orders)}")

            print(orders)

            def format_datetime(dt):
                return dt.isoformat() if dt else None

            def format_decimal(dec):
                return float(dec) if dec else 0.0

            # Convert orders data into a list of dictionaries
            order_list = []
            for order in orders:
                order_dict = {
                    "order_id": order['order_id'],
                    "order_place_date": format_datetime(order['order_place_date']),
                    "total": format_decimal(order['total']),
                    "status": order['status'] or "pending",
                    "shipping_address": order['shipping_address'],
                    "delivery_charges": format_decimal(order['delivery_charges']),
                    "expected_delivery_date": format_datetime(order['expected_delivery_date']),
                    "actual_delivery_date": format_datetime(order['actual_delivery_date']),
                    "is_completed": bool(order['is_completed']),
                    "payment_method": order['payment_method_name'],  # Using the correct field
                    "customer": {
                        "first_name": order['first_name'],
                        "last_name": order['last_name'],
                        "email": order['email'],
                        "phone": order['phone']
                    }
                }
                order_list.append(order_dict)

            return order_list

        except Exception as e:
            # Log the actual error for debugging
            print(f"Database error: {str(e)}")
            import traceback
            print(traceback.format_exc())  # This will print the full stack trace
            raise Exception(f"Error getting orders: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def create_order(self, user_id, payment_method, shipping_address, delivery_charges, order_details):
        """
        Create a new order and its details.
        :param user_id: User ID placing the order
        :param payment_method: Payment method ID
        :param shipping_address: Shipping address
        :param delivery_charges: Delivery charges
        :param order_details: List of product details (product_id, quantity, price)
        """
        cursor = None
        try:
            cursor = self.get_cursor()
            self.db.start_transaction()

            # Insert into orders table
            query = """
            INSERT INTO orders (user_id, payment_method, shipping_address, delivery_charges, total)
            VALUES (%s, %s, %s, %s, %s)
            """
            total = sum(detail['quantity'] * detail['price'] for detail in order_details)
            cursor.execute(query, (user_id, payment_method, shipping_address, delivery_charges, total))
            order_id = cursor.lastrowid

            # Insert into order_details table
            query_details = """
            INSERT INTO order_details (order_id, product_id, quantity, price, subtotal)
            VALUES (%s, %s, %s, %s, %s)
            """
            for detail in order_details:
                subtotal = detail['quantity'] * detail['price']
                cursor.execute(query_details,
                               (order_id, detail['product_id'], detail['quantity'], detail['price'], subtotal))

            self.db.commit()
            return order_id
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error creating order: {e}")
        finally:
            if cursor:
                cursor.close()

    def delete_order(self, order_id):
        """Delete an order and its associated details."""
        cursor = None
        try:
            cursor = self.get_cursor()
            self.db.start_transaction()

            # Delete from order_details table
            query_details = "DELETE FROM order_details WHERE order_id = %s"
            cursor.execute(query_details, (order_id,))

            # Delete from orders table
            query = "DELETE FROM orders WHERE id = %s"
            cursor.execute(query, (order_id,))

            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error deleting order: {e}")
        finally:
            if cursor:
                cursor.close()

    def dispatch_order(self, order_id):
        """Dispatch an order by updating the status to 'Dispatched'."""
        cursor = None

        try:
            cursor = self.get_cursor()
            # Check if the order exists and is eligible for dispatch
            cursor.execute("""
                SELECT status FROM orders WHERE id = %s
            """, (order_id,))
            result = cursor.fetchone()

            if not result:
                return {"success": False, "message": "Order not found."}

            if result['status'] in ['dispatched', 'completed']:
                return {"success": False, "message": "Order already dispatched or completed."}

            # Update the order status and expected_delivery_date
            current_date = datetime.now()
            cursor.execute("""
                UPDATE orders
                SET status = %s, expected_delivery_date = %s
                WHERE id = %s
            """, ('dispatched', current_date, order_id))
            self.db.commit()

            return {"success": True, "message": f"Order {order_id} dispatched successfully."}
        except Exception as e:
            self.db.rollback()  # Rollback in case of an error
            return {"success": False, "message": f"Error dispatching order: {str(e)}"}
        finally:
            cursor.close()  # Close the cursor

    def update_order_status(self, order_id, status):
        """Update the status of an order."""
        cursor = None
        valid_statuses = {"dispatched", "pending", "cancelled", "completed"}
        if status not in valid_statuses:
            return "Invalid order status"

        try:
            cursor = self.get_cursor()
            query = "UPDATE orders SET status = %s WHERE id = %s"
            cursor.execute(query, (status, order_id))
            self.db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error updating order status: {e}")
        finally:
            if cursor:
                cursor.close()


