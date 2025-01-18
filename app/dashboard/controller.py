from flask import Blueprint, request, jsonify, render_template
from datetime import datetime, timedelta

from app import get_db
from app.routes.routes import login_required


class DashboardController:
    def __init__(self, db_connection):
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

    def get_dashboard_overview(self):
        cursor = self.get_cursor()

        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        # Revenue Data (same as before)
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN DATE(order_place_date) = %s THEN total ELSE 0 END) as today_revenue,
                SUM(CASE WHEN DATE(order_place_date) = %s THEN total ELSE 0 END) as yesterday_revenue
            FROM orders
            WHERE DATE(order_place_date) >= %s
        """, (today, yesterday, yesterday))

        revenue_data = cursor.fetchone()

        # Pending Orders Data (same as before)
        cursor.execute("""
            SELECT COUNT(*) as pending_count
            FROM orders
            WHERE status = 'pending'
        """)
        pending_orders = cursor.fetchone()['pending_count']

        # Stock Data (same as before)
        cursor.execute("""
            SELECT 
                COUNT(*) as out_of_stock,
                SUM(CASE WHEN stock_quantity <= 5 THEN 1 ELSE 0 END) as low_stock
            FROM products
            WHERE stock_quantity <= 0
        """)
        stock_data = cursor.fetchone()

        # Review Data (same as before)
        cursor.execute("""
            SELECT 
                COUNT(*) as total_reviews,
                AVG(rating) as avg_rating,
                COUNT(CASE WHEN rating >= 4 THEN 1 END) as positive_reviews
            FROM product_reviews
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        """)
        review_data = cursor.fetchone()

        satisfaction_percentage = 0
        if review_data['total_reviews'] > 0:
            satisfaction_percentage = (review_data['positive_reviews'] / review_data['total_reviews']) * 100

        # New and Old Customers Data
        cursor.execute("""
            SELECT COUNT(*) as total_customers
            FROM users
            WHERE status = 'active'
        """)
        total_customers = cursor.fetchone()['total_customers']

        cursor.execute("""
            SELECT COUNT(*) as new_customers
            FROM users
            WHERE DATE(joined_at) = %s
        """, (today,))
        new_customers = cursor.fetchone()['new_customers']

        cursor.execute("""
            SELECT COUNT(*) as old_customers
            FROM users
            WHERE DATE(joined_at) < %s AND status = 'active'
        """, (today,))
        old_customers = cursor.fetchone()['old_customers']

        # Customers who spent the most
        cursor.execute("""
            SELECT u.id, u.first_name, u.last_name, SUM(o.total) as total_spent
            FROM users u
            JOIN orders o ON u.id = o.user_id
            WHERE o.status = 'completed'
            GROUP BY u.id
            ORDER BY total_spent DESC
            LIMIT 5
        """)
        top_spending_customers = cursor.fetchall()

        cursor.close()

        return {
            'revenue': {
                'today': float(revenue_data['today_revenue'] or 0),
                'yesterday': float(revenue_data['yesterday_revenue'] or 0),
                'change': float((revenue_data['today_revenue'] or 0) - (revenue_data['yesterday_revenue'] or 0))
            },
            'pending_orders': pending_orders,
            'stock': {
                'out_of_stock': stock_data['out_of_stock'],
                'low_stock': stock_data['low_stock']
            },
            'customer_satisfaction': {
                'percentage': round(satisfaction_percentage, 1),
                'total_reviews': review_data['total_reviews']
            },
            'customers': {
                'total_customers': total_customers,
                'new_customers': new_customers,
                'old_customers': old_customers,
                'top_spending_customers': top_spending_customers
            }
        }

    def get_recent_orders(self, limit=5):
        cursor = self.get_cursor()

        cursor.execute("""
            SELECT 
                o.id,
                CONCAT(u.first_name, ' ', COALESCE(u.last_name, '')) as customer_name,
                o.status,
                o.total,
                o.order_place_date
            FROM orders o
            JOIN users u ON o.user_id = u.id
            ORDER BY o.order_place_date DESC
            LIMIT %s
        """, (limit,))

        orders = cursor.fetchall()

        cursor.close()

        return [{
            'order_id': order['id'],
            'customer': order['customer_name'],
            'status': order['status'],
            'amount': float(order['total']),
            'date': order['order_place_date'].strftime('%Y-%m-%d %H:%M')
        } for order in orders]
