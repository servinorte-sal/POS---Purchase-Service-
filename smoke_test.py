#!/usr/bin/env python3
"""
Smoke test - Verify the main application can be imported and basic structure is correct
"""
import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import tkinter as tk
        print("✓ tkinter imported")
    except ImportError as e:
        print(f"✗ Failed to import tkinter: {e}")
        return False
    
    try:
        from tkinter import ttk, messagebox
        print("✓ tkinter.ttk and messagebox imported")
    except ImportError as e:
        print(f"✗ Failed to import tkinter components: {e}")
        return False
    
    try:
        import csv
        import datetime
        import os
        import platform
        print("✓ Standard library modules imported")
    except ImportError as e:
        print(f"✗ Failed to import standard library: {e}")
        return False
    
    return True

def test_file_structure():
    """Test that required files exist"""
    print("\nTesting file structure...")
    
    files_to_check = [
        "Digitalization_SERVINORTE(v2).py",
        "productos.csv",
        "test_ventas.py",
        "test_integration.py",
        "TESTING.md",
        "README.md",
        ".gitignore"
    ]
    
    all_exist = True
    for filename in files_to_check:
        filepath = os.path.join(os.getcwd(), filename)
        if os.path.exists(filepath):
            print(f"✓ {filename} exists")
        else:
            print(f"✗ {filename} missing")
            all_exist = False
    
    return all_exist

def test_products_csv():
    """Test that productos.csv has correct structure"""
    print("\nTesting productos.csv structure...")
    
    import csv
    
    productos_file = os.path.join(os.getcwd(), "productos.csv")
    
    try:
        with open(productos_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            products = list(reader)
            
            if len(products) == 0:
                print("✗ productos.csv is empty")
                return False
            
            print(f"✓ productos.csv has {len(products)} products")
            
            # Check required columns
            required_cols = ['codigo', 'nombre', 'categoria', 'descripcion', 'precio', 'stock', 'imagen']
            first_product = products[0]
            
            missing_cols = [col for col in required_cols if col not in first_product]
            if missing_cols:
                print(f"✗ Missing columns: {missing_cols}")
                return False
            
            print(f"✓ All required columns present: {required_cols}")
            
            # Check some sample data
            print(f"\nSample products:")
            for i, product in enumerate(products[:3]):
                print(f"  {i+1}. {product['codigo']} - {product['nombre']} - ${product['precio']}")
            
            return True
            
    except Exception as e:
        print(f"✗ Error reading productos.csv: {e}")
        return False

def test_syntax():
    """Test that main application has valid Python syntax"""
    print("\nTesting Python syntax...")
    
    import py_compile
    
    try:
        py_compile.compile("Digitalization_SERVINORTE(v2).py", doraise=True)
        print("✓ Digitalization_SERVINORTE(v2).py has valid syntax")
        return True
    except py_compile.PyCompileError as e:
        print(f"✗ Syntax error in main file: {e}")
        return False

def main():
    """Run all smoke tests"""
    print("="*60)
    print("SMOKE TESTS - Ventas Tab Implementation")
    print("="*60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("File Structure", test_file_structure()))
    results.append(("Products CSV", test_products_csv()))
    results.append(("Python Syntax", test_syntax()))
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n✓ All smoke tests passed!")
        print("\nThe ventas tab implementation is ready for use.")
        print("\nTo run the full application:")
        print("  python3 'Digitalization_SERVINORTE(v2).py'")
        return 0
    else:
        print("\n✗ Some tests failed. Please review the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
