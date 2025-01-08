# receipts.py

from flask import Blueprint, jsonify, send_file

from app import get_db
from app.receipt_generator.ThermalReceipt import ThermalReceiptGenerator  # import your class here
from app.routes.routes import login_required
from flask import current_app
# Create the blueprint
receipts_bp = Blueprint('receipts', __name__)


# Define the route for generating receipts
@receipts_bp.route('/generate-receipt/<int:order_id>', methods=['GET'])
@login_required()
def generate_receipt(order_id):
    try:
        # Initialize the receipt generator
        receipt_generator = ThermalReceiptGenerator()

        # Generate the receipt
        pdf_path = receipt_generator.generate_thermal_receipt(order_id, current_app.config['RECEIPT_PATH'])

        print(current_app.config['RECEIPT_PATH'] + pdf_path)

        # Send the PDF as a downloadable file
        return send_file(pdf_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 400
