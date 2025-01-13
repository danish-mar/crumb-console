from flask import Blueprint, render_template, jsonify, request
from app.auth.SessionManager import SessionManager
from app.routes.routes import login_required
from app.dashboard.controller import DashboardController

dash_routes = Blueprint('dash_routes', __name__)

dashboard_controller = None


def init_dashboard_controller(db_connection):
    """Initialize the OrderManager singleton."""
    global dashboard_controller
    if not dashboard_controller:
        dashboard_controller = DashboardController(db_connection)

@dash_routes.route('/dashboard')
@login_required()
def dashboard():
    overview_data = dashboard_controller.get_dashboard_overview()
    recent_orders = dashboard_controller.get_recent_orders()

    # List of sidebar items
    sidebar_items = [
        {'name': 'Dashboard', 'url': '/dashboard', 'icon': 'fas fa-tachometer-alt', 'active': 'active'},
        {'name': 'Orders', 'url': '/orders', 'icon': 'fas fa-shopping-cart', 'active': ''},
        {'name': 'Products', 'url': '/products', 'icon': 'fas fa-box', 'active': '', 'submenu': [
            {'name': 'Category', 'url': '/categories/manage', 'icon': 'fas fa-plus', 'active': ''},
            {'name': 'Manage Products', 'url': '/products/manage', 'icon': 'fas fa-edit', 'active': ''},
        ]},
        {'name': 'Customers', 'url': '/customers', 'icon': 'fas fa-users', 'active': ''},
        {'name': 'Statistics', 'url': '/statistics', 'icon': 'fas fa-chart-bar', 'active': ''},
        {'name': 'Reports', 'url': '/reports', 'icon': 'fas fa-file-alt', 'active': ''}
    ]

    return render_template('dashboard.html',
                           overview=overview_data,
                           recent_orders=recent_orders, sidebar_items=sidebar_items)


@dash_routes.route('/api/dashboard/overview', methods=['GET'])
@login_required()
def dashboard_overview():
    try:
        data = dashboard_controller.get_dashboard_overview()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dash_routes.route('/api/dashboard/recent-orders', methods=['GET'])
@login_required()
def recent_orders_api():
    try:
        limit = request.args.get('limit', default=5, type=int)
        orders = dashboard_controller.get_recent_orders(limit)
        return jsonify(orders), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500