# Crumb Console

This repository contains a dashboard application for the upcoming e-commerce website.

## Project Overview

This application is designed to streamline various aspects of a modern e-commerce platform.  Key features include:

* **Product Management:**  Add, update, and delete products with comprehensive attributes like weight, availability, and tags.  A user-friendly interface is provided for managing product listings.
* **Order Management:**  Handles order creation, tracking, and dispatching.   A system for generating thermal receipts is included.
* **Receipt Generation:**  Generates printable thermal receipts for orders. This includes both PDF generation and integration with receipt printers.


## Features

* **Improved Product Management:**
    * Product weight, availability, and tags are now managed.
    * Validation prevents accidental deletion of products linked to orders or reviews.
    * Efficient image handling is integrated for product updates.
    * Robust tag management.
    * Integrated tag input in product forms.
    * Improved error handling for deletion.
* **Enhanced Order Management:**
    * Optimized database queries and diagnostic logging for order counts.
    * Database connection robustness with `ping` operations and transaction isolation.
    * Enhanced order fetching to reduce latency.
* **Secure Receipt Generation:**
    * Thermal receipt generation in PDF format.
    * Receipt generation from database data.
    * Order dispatching functionality integrated into the UI.
* **Intuitive UI/UX:**
    * Product management UI allows for efficient addition, editing, and deletion of products, including image previews and search functionality.
    * Clear display of order details for viewing and dispatching.
    * Modern web design principles are applied to improve user experience.


## Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/danish-mar/crumb-console.git
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the database:**
    - Execute the SQL scripts in the `sql` directory to create the necessary tables.

4. **Run the application:**
   ```bash
   python app.py
   ```

   This will start the development server. Access the application in your web browser at `http://127.0.0.1:5000/`.


## API Endpoints

* **Product Management:**
    * `/api/products/create`: Create a new product (POST).
    * `/api/products/all`: Retrieve all products (GET).
    * `/api/products/update/<product_id>`: Update an existing product (PUT).
    * `/api/products/delete/<product_id>`: Delete a product (DELETE).
    * `/api/categories`: Retrieve product categories (GET).

* **Order Management:**
    * `/generate-receipt/<order_id>`: Generate and download a thermal receipt for an order (GET).
    * `/orders/<order_id>`: View order details and manage dispatching (GET).


## Technical Details

* **Programming Language:** Python
* **Web Framework:** Flask
* **Database:** MySQL


## Contributing

Contributions are welcome!  Please follow the style guidelines and create pull requests.



## Team

* Denizuh


