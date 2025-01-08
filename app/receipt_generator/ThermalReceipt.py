import datetime
from typing import Dict, List
import mysql.connector
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
import os
from barcode import Code128
from barcode.writer import ImageWriter

from app import get_db


class ThermalReceiptGenerator:
    def __init__(self, receipt_path: str = "receipts"):
        self.company_name = "Adarsh Bakery"
        self.company_address = "New Osmanpura Aurangabad"
        self.company_phone = "+91 8446968664"
        self.company_email = "support@adarsh-bakery.com"

        # Register font for receipt
        pdfmetrics.registerFont(TTFont('NotoSans', 'app/receipt_generator/NotoSans-Regular.ttf'))

        # Thermal receipt width (80mm ~ 3.15 inches)
        self.receipt_width = 80 * mm
        self.receipt_path = receipt_path

        self.margin = 3 * mm

    def _connect_db(self):
        """
        Get the database connection using the get_db function
        """
        db = get_db()
        return db

    def _generate_barcode(self, order_id: int, output_path: str) -> str:
        os.makedirs(output_path, exist_ok=True)
        barcode_instance = Code128(str(order_id), writer=ImageWriter())
        barcode_path = f"{output_path}/barcode_{order_id}"
        barcode_instance.save(barcode_path, options={"write_text": False})
        return f"{barcode_path}.png"

    def _fetch_order_details(self, order_id: int) -> tuple:
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

    def generate_thermal_receipt(self, order_id: int, output_path: str) -> str:

        order_info, order_items = self._fetch_order_details(order_id)

        print(output_path)

        if not order_info:
            raise ValueError(f"Order {order_id} not found")

        # Generate barcode
        barcode_path = self._generate_barcode(order_id, output_path)

        # Create PDF with custom page size
        pdf_filename = f"{output_path}/receipt_{order_id}.pdf"
        # Calculate height based on content
        content_height = 180 * mm  # Base height, will adjust based on items
        pagesize = (self.receipt_width, content_height)
        c = canvas.Canvas(pdf_filename, pagesize=pagesize)

        current_y = content_height - 10*mm
        line_height = 5*mm

        # Header

        c.drawCentredString(self.receipt_width/2, current_y, self.company_name)
        current_y -= line_height * 1.5

        c.setFont("Helvetica", 8)
        c.drawCentredString(self.receipt_width/2, current_y, self.company_address)
        current_y -= line_height
        c.drawCentredString(self.receipt_width/2, current_y, f"Tel: {self.company_phone}")
        current_y -= line_height * 1.5

        # Divider line
        c.line(self.margin, current_y, self.receipt_width - self.margin, current_y)
        current_y -= line_height

        # Order info
        c.setFont("NotoSans", 8)
        c.drawString(self.margin, current_y, f"Order #: {order_id}")
        current_y -= line_height
        c.drawString(self.margin, current_y,
                     f"Date: {order_info['order_place_date'].strftime('%Y-%m-%d %H:%M')}")
        current_y -= line_height
        c.drawString(self.margin, current_y,
                     f"Customer: {order_info['first_name']} {order_info['last_name']}")
        current_y -= line_height
        c.drawString(self.margin, current_y, f"Payment: {order_info['method_name']}")
        current_y -= line_height * 1.5

        # Divider line
        c.line(self.margin, current_y, self.receipt_width - self.margin, current_y)
        current_y -= line_height * 1.5

        # Items header
        c.setFont("Helvetica-Bold", 8)
        c.drawString(self.margin, current_y, "Item")
        c.drawRightString(45*mm, current_y, "Qty")
        c.drawRightString(60*mm, current_y, "Price")
        c.drawRightString(self.receipt_width - self.margin, current_y, "Total")
        current_y -= line_height

        # Divider line
        c.line(self.margin, current_y, self.receipt_width - self.margin, current_y)
        current_y -= line_height

        # Items
        c.setFont("Helvetica", 8)
        for item in order_items:
            item_total = item['quantity'] * item['price']
            # Truncate long item names
            item_name = item['name'][:20] + '...' if len(item['name']) > 20 else item['name']
            c.drawString(self.margin, current_y, item_name)
            c.drawRightString(45*mm, current_y, str(item['quantity']))
            c.drawRightString(60*mm, current_y, f"{item['price']:.2f}")
            c.drawRightString(self.receipt_width - self.margin, current_y, f"{item_total:.2f}")
            current_y -= line_height

        current_y -= line_height
        # Totals
        c.line(self.margin, current_y, self.receipt_width - self.margin, current_y)
        current_y -= line_height

        c.setFont("Helvetica-Bold", 8)
        subtotal = sum(item['quantity'] * item['price'] for item in order_items)
        delivery_charges = order_info['delivery_charges']
        total = order_info['total']

        c.drawRightString(60*mm, current_y, "Subtotal:")
        c.drawRightString(self.receipt_width - self.margin, current_y, f"Rs {subtotal:.2f}")
        current_y -= line_height

        c.drawRightString(60*mm, current_y, "Delivery:")
        c.drawRightString(self.receipt_width - self.margin, current_y, f"Rs {delivery_charges:.2f}")
        current_y -= line_height

        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(60*mm, current_y, "Total:  ")
        c.drawRightString(self.receipt_width - self.margin, current_y, f"Rs {total:.2f}")
        current_y -= line_height * 2

        # Divider line
        c.line(self.margin, current_y, self.receipt_width - self.margin, current_y)
        current_y -= line_height

        # Barcode
        barcode_width = 50*mm
        barcode_height = 10*mm
        x_centered = (self.receipt_width - barcode_width) / 2
        c.drawImage(barcode_path, x_centered, current_y, width=barcode_width, height=barcode_height)
        current_y -= barcode_height + line_height

        # Footer
        c.setFont("Helvetica", 8)
        c.drawCentredString(self.receipt_width/2, current_y, "Thanks for shopping with us")
        current_y -= line_height
        c.drawCentredString(self.receipt_width/2, current_y, "Please come again!")

        c.save()
        print(pdf_filename)
        return pdf_filename

