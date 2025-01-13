from flask import Blueprint, request, jsonify, render_template
from datetime import datetime, timedelta
from app.routes.routes import login_required


class DashboardController:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_dashboard_overview(self):
        cursor = self.db.cursor(dictionary=True)

        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        cursor.execute("""
            SELECT 
                SUM(CASE WHEN DATE(order_place_date) = %s THEN total ELSE 0 END) as today_revenue,
                SUM(CASE WHEN DATE(order_place_date) = %s THEN total ELSE 0 END) as yesterday_revenue
            FROM orders
            WHERE DATE(order_place_date) >= %s
        """, (today, yesterday, yesterday))

        revenue_data = cursor.fetchone()

        cursor.execute("""
            SELECT COUNT(*) as pending_count
            FROM orders
            WHERE status = 'pending'
        """)
        pending_orders = cursor.fetchone()['pending_count']

        cursor.execute("""
            SELECT 
                COUNT(*) as out_of_stock,
                SUM(CASE WHEN stock_quantity <= 5 THEN 1 ELSE 0 END) as low_stock
            FROM products
            WHERE stock_quantity <= 0
        """)
        stock_data = cursor.fetchone()

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
            }
        }

    def get_recent_orders(self, limit=5):
        cursor = self.db.cursor(dictionary=True)

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
