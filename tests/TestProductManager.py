# test_product_manager.py
import unittest
import mysql.connector
from unittest.mock import patch, MagicMock
from datetime import datetime
from app.product_management.product_manager import ProductManager
from app.config import AlphaTestingConfig  # Using test config instead of production


class TestProductManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test database connection."""
        cls.db_config = {
            'host': AlphaTestingConfig.SERVER,
            'user': AlphaTestingConfig.USERNAME,
            'port': AlphaTestingConfig.PORT,
            'password': AlphaTestingConfig.PASSWORD,
            'database': AlphaTestingConfig.DATABASE
        }

    def setUp(self):
        """Set up test environment before each test."""
        self.db_connection = mysql.connector.connect(**self.db_config)
        self.product_manager = ProductManager(self.db_connection)

        # Create test category
        cursor = self.db_connection.cursor()
        cursor.execute("""
            INSERT IGNORE INTO product_category (name, description)
            VALUES ('Test Category', 'Test Category Description')
        """)
        self.db_connection.commit()
        cursor.close()

    def tearDown(self):
        """Clean up test environment after each test."""
        cursor = self.db_connection.cursor()
        # Clean up test data
        cursor.execute("DELETE FROM products WHERE name LIKE 'Test Product%'")
        cursor.execute("DELETE FROM product_category WHERE name LIKE 'Test Category%'")

        self.db_connection.commit()
        cursor.close()

        if self.db_connection:
            self.db_connection.close()

    def test_add_product(self):
        """Test adding a new product."""
        product_id = self.product_manager.add_product(
            'Test Product 1',
            'Test Category',
            10.99,
            100,
            'Test Description'
        )

        # Verify product was added
        product = self.product_manager.get_product(product_id)
        self.assertIsNotNone(product)
        self.assertEqual(product['name'], 'Test Product 1')
        self.assertEqual(float(product['price']), 10.99)
        self.assertEqual(product['stock_quantity'], 100)

    def test_update_product(self):
        """Test updating a product."""
        # First add a product
        product_id = self.product_manager.add_product(
            'Test Product 2',
            'Test Category',
            10.99,
            100,
            'Test Description'
        )

        # Update the product
        success = self.product_manager.update_product(
            product_id,
            price=12.99,
            stock_quantity=150
        )
        self.assertTrue(success)

        # Verify updates
        product = self.product_manager.get_product(product_id)
        self.assertEqual(float(product['price']), 12.99)
        self.assertEqual(product['stock_quantity'], 150)

    def test_delete_product(self):
        """Test deleting a product."""
        # First add a product
        product_id = self.product_manager.add_product(
            'Test Product 3',
            'Test Category',
            10.99,
            100,
            'Test Description'
        )

        # Delete the product
        success = self.product_manager.delete_product(product_id)
        self.assertTrue(success)

        # Verify product was deleted
        product = self.product_manager.get_product(product_id)
        self.assertIsNone(product)

    def test_add_product_invalid_category(self):
        """Test adding a product with invalid category."""
        with self.assertRaises(Exception):
            self.product_manager.add_product(
                'Test Product 4',
                'Invalid Category',
                10.99,
                100,
                'Test Description'
            )

    def test_add_category(self):
        """Test adding a new category."""
        category_id = self.product_manager.add_category('Test Category 0','Test Description')
        self.assertIsNotNone(category_id)

        # Verify category was added
        category = self.product_manager.get_category(category_id)
        self.assertIsNotNone(category)
        self.assertEqual(category['name'], 'Test Category 0')
        self.assertEqual(category['description'], 'Test Description')

    def test_remove_category(self):
        """Test removing a category."""
        # First add a category
        category_id = self.product_manager.add_category('Test Category 0', 'Test Description')

        # Remove the category
        success = self.product_manager.remove_category(category_id)
        self.assertTrue(success)

        # Verify category was removed
        category = self.product_manager.get_category(category_id)
        self.assertIsNone(category)

    def test_get_category(self):
        """Test getting a category by ID."""
        # First add a category
        category_id = self.product_manager.add_category('Test Category 0', 'Test Description')

        # Get the category
        category = self.product_manager.get_category(category_id)
        self.assertIsNotNone(category)
        self.assertEqual(category['name'], 'Test Category 0')
        self.assertEqual(category['description'], 'Test Description')

    def test_get_all_categories(self):
        """Test getting all categories."""
        # Add multiple categories
        self.product_manager.add_category('Test Category 2', 'Test Description 1')
        self.product_manager.add_category('Test Category 1', 'Test Description 2')

        # Get all categories
        categories = self.product_manager.get_all_categories()
        self.assertGreaterEqual(len(categories), 2)


if __name__ == '__main__':
    unittest.main()
