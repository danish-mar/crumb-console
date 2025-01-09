from flask import Blueprint, request, jsonify, current_app, render_template, send_from_directory
from werkzeug.utils import secure_filename
import os

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

@product_blueprint.route('/api/products/all', methods=['POST','GET'])
def fetch_all_products():
    try:
        cursor = product_manager.get_cursor()
        query = """
            SELECT p.*, c.name as category_name
            FROM products p
            RIGHT JOIN product_category c ON p.category = c.id
        """
        cursor.execute(query)
        products = cursor.fetchall()

        for product in products:
            print(product["image_url"])
        #     product["image_url"] = f"{request.host_url}{product['image']}"  # Construct image URL
        return jsonify({"products": products}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@product_blueprint.route('/api/products/create', methods=['POST'])
def create_product():
    try:
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
            image_url=image_path
        )


        # Update the product with the image path
        # product_manager.update_product(product_id, image_url=image_path)

        return jsonify({"message": "Product created successfully", "product_id": product_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@product_blueprint.route('/api/products/update/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        data = request.form
        image = request.files.get('image')


        print("Update requested")
        print(data)

        update_data = {
            "name": data.get('name'),
            "category": data.get('category'),
            "price": float(data.get('price')) if data.get('price') else None,
            "stock_quantity": int(data.get('stock_quantity')) if data.get('stock_quantity') else None,
            "description": data.get('description'),
            "is_available": data.get('is_available')
        }

        print("\n")
        print("Update Data : ")
        print(update_data)

        if image:
            update_data['image_url'] = save_image(image)
        else:
            update_data['image_url'] = "product_image.png"

        print(f"Updating product {product_id} with data: {update_data}")

        success = product_manager.update_product(product_id, **update_data)
        if not success:
            return jsonify({"error": "Product not found"}), 404

        return jsonify({"message": "Product updated successfully"}), 200
    except Exception as e:
        print(f"Error updating product {product_id}: {e}")
        return jsonify({"error": str(e)}), 500

@product_blueprint.route('/api/products/delete/<int:product_id>', methods=['DELETE'])
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


@product_blueprint.route('/products/manage', methods=['POST','GET'])
def manage_product_page():
    try:
        return render_template('product/manage_products.html')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@product_blueprint.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all categories with their ID and name."""
    try:
        categories = product_manager.get_all_categories()
        return jsonify({"categories": categories}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

4