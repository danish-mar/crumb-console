from flask import Blueprint, request, jsonify, current_app, render_template
from app.order_management.order_manager import OrderManager
from app.routes.routes import login_required
from app.auth.sidebar import get_sidebar_items

# Create the blueprint
order_blueprint = Blueprint('order_blueprint', __name__)

# Singleton instance for OrderManager
order_manager = None


def init_order_manager(db_connection):
    """Initialize the OrderManager singleton."""
    global order_manager
    if not order_manager:
        order_manager = OrderManager(db_connection)


@order_blueprint.route('/api/orders/<int:order_id>', methods=['POST'])
@login_required()
def get_order(order_id):
    """Get details of a specific order."""
    try:
        if not order_manager:
            return jsonify({"error": "OrderManager not initialized"}), 500
        order = order_manager.get_order(order_id)
        if order:
            return jsonify(order), 200
        return jsonify({"message": "Order not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@order_blueprint.route('/api/orders', methods=['POST'])
@login_required()
def create_order():
    """Create a new order."""
    try:
        if not order_manager:
            return jsonify({"error": "OrderManager not initialized"}), 500

        data = request.json
        user_id = data.get('user_id')
        payment_method = data.get('payment_method')
        shipping_address = data.get('shipping_address')
        delivery_charges = data.get('delivery_charges')
        order_details = data.get('order_details')

        if not all([user_id, payment_method, shipping_address, delivery_charges, order_details]):
            return jsonify({"error": "Missing required fields"}), 400

        order_id = order_manager.create_order(
            user_id, payment_method, shipping_address, delivery_charges, order_details)
        return jsonify({"order_id": order_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@order_blueprint.route('/api/orders/<int:order_id>', methods=['PUT'])
@login_required()
def update_order_status(order_id):
    """Update the status of an order."""
    try:
        if not order_manager:
            return jsonify({"error": "OrderManager not initialized"}), 500

        data = request.json
        status = data.get('status')

        if not status:
            return jsonify({"error": "Missing 'status' field"}), 400

        order_manager.update_order_status(order_id, status)
        return jsonify({"message": "Order status updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@order_blueprint.route('/api/orders/<int:order_id>', methods=['DELETE'])
@login_required()
def delete_order(order_id):
    """Delete an order."""
    print("Deleting order ??")
    try:
        if not order_manager:
            return jsonify({"error": "OrderManager not initialized"}), 500

        order_manager.delete_order(order_id)
        return jsonify({"message": "Order deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@order_blueprint.route('/api/orders/all', methods=['POST'])
@login_required()
def get_all_orders():
    try:
        orders = order_manager.get_all_orders()
        return jsonify({"orders": orders}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@order_blueprint.route('/api/orders/dispatch/<int:order_id>', methods=['POST'])
@login_required()
def dispatch_order_api(order_id):

    # Call the dispatch order method
    result = order_manager.dispatch_order(order_id)

    if result['success']:
        return jsonify({"success": True, "message": result['message']}), 200
    else:
        return jsonify({"success": False, "message": result['message']}), 400

@order_blueprint.route('/api/orders/<int:order_id>/status', methods=['PUT'])
@login_required()
def update_order_status_route(order_id):
    """API route to update the status of an order."""
    try:
        # Parse JSON data from the request body
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({"error": "Status is required"}), 400

        status = data['status'].lower()
        # Assuming `db_instance` is the instance of the class containing update_order_status
        success = order_manager.update_order_status(order_id, status)

        if success:
            return jsonify({"message": f"Order {order_id} status updated to {status}"}), 200
        else:
            return jsonify({"error": "Order not found or status unchanged"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to update status: {str(e)}"}), 500



@order_blueprint.route('/orders/<int:order_id>', methods=['GET'])
@login_required(redirect_url='/order')
def view_order(order_id):
    sidebar_items = get_sidebar_items('admin')
    return render_template('order/view_order.html', sidebar_items=sidebar_items, order_id=order_id)
