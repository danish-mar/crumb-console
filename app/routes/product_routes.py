from flask import Blueprint, request, jsonify, current_app, render_template, send_from_directory
from werkzeug.utils import secure_filename
import os

from app.auth.sidebar import get_sidebar_items
from app.routes.routes import login_required

from app.product_management.product_manager import ProductManager

# Create the blueprint
product_blueprint = Blueprint('product_blueprint', __name__)

# Singleton instance for ProductManager
product_manager = None


def init_product_manager(db_connection):
    """Initialize the ProductManager singleton."""
    global product_manager
    print("Product Manager : Initializing Routes ")
    if not product_manager:
        print(db_connection)
        product_manager = ProductManager(db_connection)


# Helper to get the absolute path for saving images
def save_image(image):
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    filename = secure_filename(image.filename)
    filepath = os.path.join(upload_folder, filename)
    image.save(filepath)
    return f"/static/images/products/{filename}"


# Routes

@product_blueprint.route('/api/products/all', methods=['POST', 'GET'])
@login_required()
def fetch_all_products():
    try:

        products = product_manager.fetch_all_products()

        for product in products:
            print(product["image_url"])
        #     product["image_url"] = f"{request.host_url}{product['image']}"  # Construct image URL
        return jsonify({"products": products}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@product_blueprint.route('/api/products/create', methods=['POST'])
@login_required()
def create_product():
    try:
        #   def add_product(self, name, category_id, price, stock, description, weight_in_g, tags, image_url="Wil.jpg"):

        data = request.form
        print(data)
        image = request.files.get('image')

        if not image:
            return jsonify({"error": "Image is required"}), 400

        image_path = save_image(image)
        print(image_path)

        print()

        print("Creating product with data:", data)

        product_id = product_manager.add_product(
            name=data['name'],
            category_id=data['category'],
            price=float(data['price']),
            stock=int(data['stock']),
            description=data['description'],
            is_available=data['is_available'],
            weight_in_g=int(data['weight']),
            tags=data['tags'],
            image_url=image_path
        )

        # Update the product with the image path
        # product_manager.update_product(product_id, image_url=image_path)

        return jsonify({"message": "Product created successfully", "product_id": product_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@product_blueprint.route('/api/products/update/<int:product_id>', methods=['PUT'])
@login_required()
def update_product(product_id):
    try:
        # Get form data
        data = request.form
        image = request.files.get('image')

        print("Update requested")
        print(data)

        # Handle image file
        if image:
            image_url = save_image(image)
        else:
            image_url = data.get('image_url')
            print("No image provided, using existing image:", image_url)

        # Prepare the update data
        update_data = {
            "name": data.get('name'),
            "category": data.get('category'),
            "price": float(data.get('price')) if data.get('price') else None,
            "stock_quantity": int(data.get('stock')) if data.get('stock') else None,
            "description": data.get('description'),
            "is_available": data.get('is_available'),
            "weight": float(data.get('weight')) if data.get('weight') else None,  # Add weight
            "tags": data.get('tags'),  # Add tags (comma-separated string)
            "image_url": image_url
        }

        print("\n")
        print("Update Data : ")
        print(f"Updating product {product_id} with data: {update_data}")
        print(update_data)

        # Call the product manager to update the product
        success = product_manager.update_product(product_id, **update_data)
        if not success:
            return jsonify({"error": "Product not found"}), 404

        return jsonify({"message": "Product updated successfully"}), 200

    except Exception as e:
        print(f"Error updating product {product_id}: {e}")
        return jsonify({"error": str(e)}), 500


@product_blueprint.route('/api/products/delete/<int:product_id>', methods=['DELETE'])
@login_required()
def delete_product(product_id):
    try:
        print(f"deleting product_id {product_id}")
        success = product_manager.delete_product(product_id)
        print(success)
        if not success:
            return jsonify({"error": "Product not found"}), 404
        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@product_blueprint.route('/products/manage', methods=['POST', 'GET'])
@login_required(redirect_url="/products/manage")
def manage_product_page():
    try:
        sidebar_items = get_sidebar_items('admin')

        return render_template('product/manage_products.html', sidebar_items=sidebar_items)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@product_blueprint.route('/api/categories', methods=['GET'])
@login_required()
def get_categories():
    """Get all categories with their ID and name."""
    try:
        categories = product_manager.get_all_categories()
        return jsonify({"categories": categories}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


## category maanagement routes :
@product_blueprint.route('/api/categories/add', methods=['POST'])
@login_required()
def add_category():
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')

        if not name:
            return jsonify({"error": "Category name is required"}), 400

        category_id = product_manager.add_category(name, description)
        return jsonify({"message": "Category added successfully", "category_id": category_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@product_blueprint.route('/api/categories/delete/<int:category_id>', methods=['DELETE'])
@login_required()
def remove_category(category_id):
    try:
        success = product_manager.remove_category(category_id)
        if not success:
            return jsonify({"error": "Category not found"}), 404
        return jsonify({"message": "Category removed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@product_blueprint.route('/api/categories/<int:category_id>', methods=['GET'])
@login_required()
def get_category(category_id):
    try:
        category = product_manager.get_category(category_id)
        if not category:
            return jsonify({"error": "Category not found"}), 404
        return jsonify({"category": category}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@product_blueprint.route('/api/categories/update/<int:category_id>', methods=['PUT'])
@login_required()
def update_category(category_id):
    try:
        # Get form data
        data = request.form

        print("Update category requested")
        print(data)

        # Prepare the update data
        update_data = {
            "name": data.get('name'),
            "description": data.get('description'),
        }

        # Filter out None values (optional: if the update_category method already does this)
        update_data = {k: v for k, v in update_data.items() if v is not None}

        print("\n")
        print("Update Data:")
        print(f"Updating category {category_id} with data: {update_data}")

        # Call the category manager to update the category
        success = product_manager.update_category(category_id, **update_data)
        if not success:
            return jsonify({"error": "Category not found or no changes made"}), 404

        return jsonify({"message": "Category updated successfully"}), 200

    except Exception as e:
        print(f"Error updating category {category_id}: {e}")
        return jsonify({"error": str(e)}), 500


@product_blueprint.route('/categories/manage', methods=['GET'])
@login_required(redirect_url="/categories/manage")
def manage_catetgory_template():
    try:
        sidebar_items = get_sidebar_items('admin')

        return render_template('product/manage_categories.html',sidebar_items=sidebar_items)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

