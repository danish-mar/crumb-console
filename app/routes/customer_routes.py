from flask import Blueprint, request, jsonify, render_template

from app.routes.routes import login_required
from app.customer_management.customer_manager import CustomerManager
from app.auth.sidebar import get_sidebar_items

# Initialize the Blueprint
customer_routes = Blueprint('customer_routes', __name__)

# Initialize the CustomerManager instance
customer_manager = None


def init_customer_manager(db_connection):
    """Initialize the Customer Manager singleton."""
    global customer_manager
    print("Customer Manager : Initializing Routes ")
    if not customer_manager:
        customer_manager = CustomerManager(db_connection)


# Route to create a new customer
@customer_routes.route('/api/customer/manage', methods=['POST'])
@login_required()
def create_customer():
    data = request.get_json()

    # Extract required fields from request data
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')
    default_location = data.get('default_location')
    role = data.get('role', 'customer')  # Default to 'customer'
    status = data.get('status', 'active')  # Default to 'active'
    auth_provider = data.get('auth_provider', 'manual')  # Default to 'manual'
    profile_pic_url = data.get('profile_pic_url', 'none')  # Default to 'none'
    address_lat = data.get('address_lat')
    address_lon = data.get('address_lon')

    # Validate the required fields
    if not all([first_name, last_name, email, phone, password, default_location]):
        return jsonify({'error': 'Missing required fields'}), 400

    # Create the customer
    customer_id = customer_manager.create_customer(
        first_name, last_name, email, phone, password, default_location,
        role, status, auth_provider, profile_pic_url, address_lat, address_lon
    )

    if customer_id:
        return jsonify({'message': 'Customer created successfully', 'customer_id': customer_id}), 201
    else:
        return jsonify({'error': 'Failed to create customer'}), 500


# Route to get a customer by ID
@customer_routes.route('/api/customer/<int:customer_id>', methods=['GET'])
@login_required()
def get_customer_by_id(customer_id):
    customer = customer_manager.get_customer_by_id(customer_id)
    if customer:
        return jsonify({'customer': customer}), 200
    else:
        return jsonify({'error': 'Customer not found'}), 404


# Route to update a customer
@customer_routes.route('/api/customer/manage/<int:customer_id>', methods=['PUT'])
@login_required()
def update_customer(customer_id):
    data = request.get_json()

    # Validate the data to update
    if not data:
        return jsonify({'error': 'No data provided to update'}), 400

    updated_rows = customer_manager.update_customer(customer_id, **data)

    if updated_rows > 0:
        return jsonify({'message': 'Customer updated successfully'}), 200
    else:
        return jsonify({'error': 'Failed to update customer or no changes detected'}), 400


# Route to delete a customer
@customer_routes.route('/api/customer/<int:customer_id>', methods=['DELETE'])
@login_required()
def delete_customer(customer_id):
    deleted_rows = customer_manager.delete_customer(customer_id)
    if deleted_rows > 0:
        return jsonify({'message': 'Customer deleted successfully'}), 200
    else:
        return jsonify({'error': 'Failed to delete customer or customer not found'}), 400


# Route to get all customers
@customer_routes.route('/api/customer/all', methods=['GET'])
@login_required()
def get_all_customers():
    customers = customer_manager.get_all_customers()
    if customers:
        return jsonify({'customers': customers}), 200
    else:
        return jsonify({'error': 'No customers found'}), 404

@customer_routes.route('/customers')
@login_required()
def customer_management():
    sidebar = get_sidebar_items("admin")
    return render_template('users/customer.html',sidebar_items=sidebar)