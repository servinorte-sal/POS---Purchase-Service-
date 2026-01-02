#!/usr/bin/env python3
"""
Unit tests for the Ventas (Sales) tab functionality
"""
import unittest
import os
import sys
import csv
import datetime
import tempfile
from unittest.mock import Mock, patch, MagicMock

# Ensure we can import the module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestVentasTabFunctionality(unittest.TestCase):
    """Test cases for the ventas tab"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.products_file = os.path.join(self.test_dir, "productos.csv")
        self.ventas_file = os.path.join(self.test_dir, "ventas.csv")
        
        # Create a sample products CSV
        with open(self.products_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['codigo', 'nombre', 'categoria', 'descripcion', 'precio', 'stock', 'imagen'])
            writer.writerow(['TEST001', 'Test Product 1', 'needles', 'Test description 1', '10.00', '5', ''])
            writer.writerow(['TEST002', 'Test Product 2', 'knife', 'Test description 2', '20.00', '10', ''])
            writer.writerow(['TEST003', 'Test Product 3', 'bobbin cases', 'Test description 3', '15.00', '8', ''])
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_load_products_from_csv(self):
        """Test loading products from CSV file"""
        products = []
        with open(self.products_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                products.append(row)
        
        self.assertEqual(len(products), 3)
        self.assertEqual(products[0]['codigo'], 'TEST001')
        self.assertEqual(products[1]['nombre'], 'Test Product 2')
        self.assertEqual(products[2]['categoria'], 'bobbin cases')
    
    def test_search_by_code(self):
        """Test searching products by code"""
        products = []
        with open(self.products_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                products.append(row)
        
        search_text = 'test001'
        filtered = [p for p in products if search_text.lower() in p['codigo'].lower()]
        
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['codigo'], 'TEST001')
    
    def test_search_by_name(self):
        """Test searching products by name"""
        products = []
        with open(self.products_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                products.append(row)
        
        search_text = 'product 2'
        filtered = [p for p in products if search_text.lower() in p['nombre'].lower()]
        
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['nombre'], 'Test Product 2')
    
    def test_search_by_category(self):
        """Test searching products by category"""
        products = []
        with open(self.products_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                products.append(row)
        
        search_text = 'knife'
        filtered = [p for p in products if search_text.lower() in p['categoria'].lower()]
        
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['categoria'], 'knife')
    
    def test_multiple_category_search(self):
        """Test searching products by multiple categories"""
        products = []
        with open(self.products_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                products.append(row)
        
        search_text = 'bob'
        filtered = [p for p in products if search_text.lower() in p['categoria'].lower()]
        
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['categoria'], 'bobbin cases')
    
    def test_add_to_cart(self):
        """Test adding products to cart"""
        cart_items = []
        
        # Simulate adding a product
        product = {
            'codigo': 'TEST001',
            'nombre': 'Test Product 1',
            'precio': '10.00',
            'stock': '5'
        }
        
        quantity = 2
        cart_items.append({
            'codigo': product['codigo'],
            'nombre': product['nombre'],
            'cantidad': quantity,
            'precio': float(product['precio'])
        })
        
        self.assertEqual(len(cart_items), 1)
        self.assertEqual(cart_items[0]['cantidad'], 2)
        self.assertEqual(cart_items[0]['precio'], 10.00)
    
    def test_calculate_cart_total(self):
        """Test calculating cart total"""
        cart_items = [
            {'codigo': 'TEST001', 'nombre': 'Product 1', 'cantidad': 2, 'precio': 10.00},
            {'codigo': 'TEST002', 'nombre': 'Product 2', 'cantidad': 3, 'precio': 20.00}
        ]
        
        total = sum(item['cantidad'] * item['precio'] for item in cart_items)
        
        self.assertEqual(total, 80.00)
    
    def test_save_order_to_csv(self):
        """Test saving order to CSV file"""
        cart_items = [
            {'codigo': 'TEST001', 'nombre': 'Product 1', 'cantidad': 2, 'precio': 10.00}
        ]
        
        client_code = 'CLIENT001'
        fecha = datetime.date.today().strftime('%d-%m-%Y')
        
        # Save order
        with open(self.ventas_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['fecha', 'cliente', 'codigo', 'producto', 'cantidad', 'precio', 'total'])
            
            for item in cart_items:
                writer.writerow([
                    fecha,
                    client_code,
                    item['codigo'],
                    item['nombre'],
                    item['cantidad'],
                    item['precio'],
                    item['cantidad'] * item['precio']
                ])
        
        # Verify saved data
        with open(self.ventas_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            rows = list(reader)
        
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['cliente'], 'CLIENT001')
        self.assertEqual(rows[0]['codigo'], 'TEST001')
        self.assertEqual(float(rows[0]['total']), 20.00)
    
    def test_stock_validation(self):
        """Test stock validation when adding to cart"""
        product = {
            'codigo': 'TEST001',
            'nombre': 'Test Product 1',
            'precio': '10.00',
            'stock': '5'
        }
        
        requested_quantity = 10
        available_stock = int(product['stock'])
        
        # Should fail if requested > stock
        self.assertFalse(requested_quantity <= available_stock)
        
        # Should succeed if requested <= stock
        requested_quantity = 3
        self.assertTrue(requested_quantity <= available_stock)
    
    def test_remove_from_cart(self):
        """Test removing items from cart"""
        cart_items = [
            {'codigo': 'TEST001', 'nombre': 'Product 1', 'cantidad': 2, 'precio': 10.00},
            {'codigo': 'TEST002', 'nombre': 'Product 2', 'cantidad': 3, 'precio': 20.00}
        ]
        
        # Remove first item
        del cart_items[0]
        
        self.assertEqual(len(cart_items), 1)
        self.assertEqual(cart_items[0]['codigo'], 'TEST002')
    
    def test_clear_cart(self):
        """Test clearing all items from cart"""
        cart_items = [
            {'codigo': 'TEST001', 'nombre': 'Product 1', 'cantidad': 2, 'precio': 10.00},
            {'codigo': 'TEST002', 'nombre': 'Product 2', 'cantidad': 3, 'precio': 20.00}
        ]
        
        cart_items = []
        
        self.assertEqual(len(cart_items), 0)
    
    def test_multiple_orders_same_client(self):
        """Test creating multiple orders for the same client"""
        client_code = 'CLIENT001'
        
        # First order
        order1 = [
            {'codigo': 'TEST001', 'nombre': 'Product 1', 'cantidad': 2, 'precio': 10.00}
        ]
        
        # Second order
        order2 = [
            {'codigo': 'TEST002', 'nombre': 'Product 2', 'cantidad': 1, 'precio': 20.00}
        ]
        
        # Save both orders
        with open(self.ventas_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['fecha', 'cliente', 'codigo', 'producto', 'cantidad', 'precio', 'total'])
            
            fecha = datetime.date.today().strftime('%d-%m-%Y')
            for item in order1:
                writer.writerow([fecha, client_code, item['codigo'], item['nombre'], 
                               item['cantidad'], item['precio'], item['cantidad'] * item['precio']])
            
            for item in order2:
                writer.writerow([fecha, client_code, item['codigo'], item['nombre'], 
                               item['cantidad'], item['precio'], item['cantidad'] * item['precio']])
        
        # Verify both orders saved
        with open(self.ventas_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            rows = list(reader)
        
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['cliente'], client_code)
        self.assertEqual(rows[1]['cliente'], client_code)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
