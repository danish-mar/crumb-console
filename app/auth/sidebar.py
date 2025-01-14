# sidebar.py

def get_sidebar_items(user_role):
    # Centralized definition of sidebar items with role-based conditions
    sidebar_items = [
        {'name': 'Dashboard', 'url': '/dashboard', 'icon': 'fas fa-tachometer-alt', 'active': ''},
        {'name': 'Orders', 'url': '/orders', 'icon': 'fas fa-shopping-cart', 'active': ''},
        {'name': 'Products', 'url': '/products', 'icon': 'fas fa-box', 'active': '', 'submenu': [
            {'name': 'Category', 'url': '/categories/manage', 'icon': 'fas fa-plus', 'active': ''},
            {'name': 'Manage Products', 'url': '/products/manage', 'icon': 'fas fa-edit', 'active': ''},
            {'name': 'Product Reviews', 'url': '/products/review', 'icon': 'fas fa-star', 'active': ''},
        ]},
        {'name': 'Customers', 'url': '/customers', 'icon': 'fas fa-users', 'active': ''},
        {'name': 'Statistics', 'url': '/statistics', 'icon': 'fas fa-chart-bar', 'active': ''},
        {'name': 'Reports', 'url': '/reports', 'icon': 'fas fa-file-alt', 'active': ''},
    ]

    # Modify sidebar items based on user role
    if user_role != 'admin':  # Example role-based condition
        sidebar_items = [item for item in sidebar_items if item['name'] != 'Reports']  # Hide Reports for non-admins

    return sidebar_items
