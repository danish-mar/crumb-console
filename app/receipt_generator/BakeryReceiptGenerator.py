import datetime
from typing import Dict, List
import mysql.connector
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
import os
from barcode import Code128
from barcode.writer import ImageWriter

class BakeryReceiptGenerator:
    def __init__(self, db_config: Dict):
        """
        Initialize the receipt generator with database configuration

        Args:
            db_config (dict): MySQL database configuration with host, user, password, database
        """
        self.db_config = db_config
        self.company_name = "Adarsh Bakery"
        self.company_address = "123 Baker Street"
        self.company_phone = "(555) 123-4567"
        self.company_email = "orders@sweetdelights.com"

    def _connect_db(self):
        """Create and return a database connection"""
        return mysql.connector.connect(**self.db_config)

    def _generate_barcode(self, order_id: int, output_path: str) -> str:
        """Generate a barcode image for the order"""
        # Ensure the output directory exists
        os.makedirs(output_path, exist_ok=True)

        # Generate barcode
        barcode_instance = Code128(str(order_id), writer=ImageWriter())
        barcode_path = f"{output_path}/barcode_{order_id}"
        barcode_filename = barcode_instance.save(barcode_path)

        return barcode_filename

    def _fetch_order_details(self, order_id: int) -> tuple:
        """Fetch all necessary order information from database"""
        conn = self._connect_db()
        cursor = conn.cursor(dictionary=True)

        order_query = """
        SELECT o.*, u.first_name, u.last_name, u.email, pm.method_name
        FROM orders o
        JOIN users u ON o.user_id = u.id
        JOIN payment_methods pm ON o.payment_method = pm.id
        WHERE o.id = %s
        """
        cursor.execute(order_query, (order_id,))
        order_info = cursor.fetchone()

        items_query = """
        SELECT od.*, p.name, p.price
        FROM order_details od
        JOIN products p ON od.product_id = p.id
        WHERE od.order_id = %s
        """
        cursor.execute(items_query, (order_id,))
        order_items = cursor.fetchall()

        cursor.close()
        conn.close()

        return order_info, order_items

    def generate_pdf_receipt(self, order_id: int, output_path: str = "./receipts") -> str:
        """
        Generate a PDF receipt for the given order ID

        Args:
            order_id (int): The order ID to generate receipt for
            output_path (str): Path to save the PDF and barcode

        Returns:
            str: Path to generated PDF file
        """
        order_info, order_items = self._fetch_order_details(order_id)

        if not order_info:
            raise ValueError(f"Order {order_id} not found")

        # Generate barcode
        barcode_path = self._generate_barcode(order_id, output_path)

        # Create PDF
        pdf_filename = f"{output_path}/receipt_{order_id}.pdf"
        c = canvas.Canvas(pdf_filename, pagesize=letter)
        width, height = letter

        # Add logo (assuming logo.png exists in the same directory)
        logo_path = "logo.png"
        if os.path.exists(logo_path):
            c.drawImage(logo_path, width/2 - 1*inch, height - 2*inch, width=2*inch, height=2*inch)

        # Header
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width/2, height - 2.5*inch, self.company_name)

        c.setFont("Helvetica", 10)
        c.drawCentredString(width/2, height - 2.7*inch, self.company_address)
        c.drawCentredString(width/2, height - 2.9*inch, f"Phone: {self.company_phone}")
        c.drawCentredString(width/2, height - 3.1*inch, self.company_email)

        # Order Information
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1*inch, height - 3.5*inch, f"Receipt")
        c.setFont("Helvetica", 10)
        c.drawString(1*inch, height - 3.8*inch, f"Order #: {order_id}")
        c.drawString(1*inch, height - 4.0*inch, f"Date: {order_info['order_place_date'].strftime('%Y-%m-%d %H:%M')}")
        c.drawString(1*inch, height - 4.2*inch, f"Customer: {order_info['first_name']} {order_info['last_name']}")
        c.drawString(1*inch, height - 4.4*inch, f"Payment Method: {order_info['method_name']}")

        # Items Table
        data = [['Item', 'Quantity', 'Price', 'Subtotal']]
        for item in order_items:
            subtotal = item['quantity'] * item['price']
            data.append([
                item['name'],
                str(item['quantity']),
                f"${item['price']:.2f}",
                f"${subtotal:.2f}"
            ])

        # Calculate totals
        subtotal = sum(item['price'] * item['quantity'] for item in order_items)
        delivery_charges = order_info['delivery_charges']
        total = order_info['total']

        # Add totals to table
        data.extend([
            ['', '', 'Subtotal:', f"${subtotal:.2f}"],
            ['', '', 'Delivery Charges:', f"${delivery_charges:.2f}"],
            ['', '', 'Total:', f"${total:.2f}"]
        ])

        table = Table(data, colWidths=[3*inch, 1*inch, 1.25*inch, 1.25*inch])
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -4), 1, colors.black),
            ('LINEBELOW', (2, -3), (-1, -1), 1, colors.black),
            ('FONTNAME', (2, -3), (-1, -1), 'Helvetica-Bold'),
        ]))

        table.wrapOn(c, width, height)
        table.drawOn(c, 1*inch, height - 7*inch)

        # Add barcode
        c.drawImage(barcode_path, 1*inch, 1*inch, width=2*inch, height=0.5*inch)

        # Footer
        c.drawCentredString(width/2, 0.75*inch, "Thank you for your business!")

        c.save()
        return pdf_filename
# Example usage:
if __name__ == "__main__":
    db_config = {
        "host": "100.65.185.22",
        "user": "diona",
        "password": "cryo950",
        "database": "bakery"
    }

    receipt_generator = BakeryReceiptGenerator(db_config)
    try:
        pdf_path = receipt_generator.generate_pdf_receipt(28)
        print(f"Receipt generated successfully: {pdf_path}")
    except Exception as e:
        print(f"Error generating receipt: {e}")