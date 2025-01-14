from flask import Blueprint, render_template, jsonify, request
from app.auth.SessionManager import SessionManager
from app.auth.sidebar import get_sidebar_items
from app.routes.routes import login_required
from app.dashboard.controller import DashboardController

dash_routes = Blueprint('dash_routes', __name__)

dashboard_controller = None


def init_dashboard_controller(db_connection):
    """Initialize the dashboard controller singleton."""
    global dashboard_controller
    print("Dashboard : Initializing Routes ")
    if not dashboard_controller:
        dashboard_controller = DashboardController(db_connection)


@dash_routes.route('/dashboard')
@login_required()
def dashboard():
    overview_data = dashboard_controller.get_dashboard_overview()
    print(overview_data)
    recent_orders = dashboard_controller.get_recent_orders()

    sidebar_items = get_sidebar_items('admin')

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
