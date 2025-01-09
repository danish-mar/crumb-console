from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, current_app
from functools import wraps
import mysql.connector

from app.auth.SessionManager import SessionManager
from app.customer_management.customer_manager import UserManager
from app.db import get_mongo_db

app = Blueprint('app', __name__)


def login_required(redirect_url='/dashboard',order_id=""):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print("Checking for session")

            # Access the session manager with the app's config
            session_manager = SessionManager(
                db_uri=current_app.config['MONGO_URI'],
                db_name=current_app.config['MONGO_DATABASE']
            )

            # Retrieve the session ID from cookies
            session_id = request.cookies.get('session_id')
            print(session_id)

            # If no session ID or session is invalid
            if not session_id or not session_manager.validate_session(session_id):
                print("Session Rejected")
                # Handle GET requests with a redirect to login
                if request.method == 'GET':
                    if order_id:
                        return redirect(url_for('app.login', isLoggedIn="false", redirect=f"/orders/{order_id}"))
                    return redirect(url_for('app.login', isLoggedIn="false", redirect=redirect_url))
                # Handle non-GET requests with an error response
                return jsonify({"error": "Unauthorized access"}), 401

            # If session is valid, allow access to the route
            print("Session Accepted")
            return f(*args, **kwargs)

        return decorated_function

    return decorator


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user_manager = UserManager(get_mongo_db())
        user = user_manager.get_user_by_email(email)

        print(user)

        if user is not None and user['password'] == password:
            session_manager = SessionManager(db_uri=current_app.config['MONGO_URI'],
                                             db_name=current_app.config['MONGO_DATABASE'])
            session_id = session_manager.create_session(user['_id'], expires_in_hours=24)
            if session_id is not None:
                response = redirect(url_for('app.dashboard'))
                response.set_cookie('session_id', session_id)
                return response
            else:
                flash('Error creating session', 'error')
        else:
            flash('Invalid email or password', 'error')

    return render_template('login.html')


@app.route('/dashboard', methods=['GET'])
@login_required(redirect_url='/dashboard')
def dashboard():
    # List of sidebar items
    sidebar_items = [
        {'name': 'Dashboard', 'url': '/dashboard', 'icon': 'fas fa-tachometer-alt', 'active': 'active'},
        {'name': 'Orders', 'url': '/orders', 'icon': 'fas fa-shopping-cart', 'active': ''},
        {'name': 'Products', 'url': '/products', 'icon': 'fas fa-box', 'active': '', 'submenu': [
            {'name': 'Category', 'url': '/products/add', 'icon': 'fas fa-plus', 'active': ''},
            {'name': 'Manage Products', 'url': '/products/manage', 'icon': 'fas fa-edit', 'active': ''},
        ]},
        {'name': 'Customers', 'url': '/customers', 'icon': 'fas fa-users', 'active': ''},
        {'name': 'Statistics', 'url': '/statistics', 'icon': 'fas fa-chart-bar', 'active': ''},
        {'name': 'Reports', 'url': '/reports', 'icon': 'fas fa-file-alt', 'active': ''}
    ]

    return render_template('dashboard.html', sidebar_items=sidebar_items)


@app.route('/orders', methods=['GET'])
@login_required(redirect_url='/orders')
def orders():
    # List of sidebar items
    sidebar_items = [
        {'name': 'Dashboard', 'url': '/dashboard', 'icon': 'fas fa-tachometer-alt', 'active': ''},
        {'name': 'Orders', 'url': '/orders', 'icon': 'fas fa-shopping-cart', 'active': 'active'},
        {'name': 'Products', 'url': '/products', 'icon': 'fas fa-box', 'active': '', 'submenu': [
            {'name': 'Category', 'url': '/products/add', 'icon': 'fas fa-plus', 'active': ''},
            {'name': 'Manage Products', 'url': '/products/manage', 'icon': 'fas fa-edit', 'active': ''},
        ]},
        {'name': 'Customers', 'url': '/customers', 'icon': 'fas fa-users', 'active': ''},
        {'name': 'Statistics', 'url': '/statistics', 'icon': 'fas fa-chart-bar', 'active': ''},
        {'name': 'Reports', 'url': '/reports', 'icon': 'fas fa-file-alt', 'active': ''}
    ]

    return render_template('order/orders.html', sidebar_items=sidebar_items)
