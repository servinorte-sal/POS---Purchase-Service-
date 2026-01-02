# Testing the Ventas (Sales/POS) Tab

This directory contains tests for the Point of Sale (POS) functionality implemented in the ventas tab.

## Test Files

### `test_ventas.py`
Unit tests for the core ventas tab functionality:
- Product loading from CSV
- Search by code, name, and category
- Add to cart functionality
- Cart calculations
- Stock validation
- Order saving
- Multiple orders per client

**Run with:**
```bash
python3 test_ventas.py
```

### `test_integration.py`
Integration test that verifies:
- Tkinter availability
- Required modules (csv, datetime)
- Product database loading
- Basic widget creation

**Run with:**
```bash
python3 test_integration.py
```

### `test_visual.py`
Visual test that creates a demo window showing the ventas tab UI.

**Run with (requires X display):**
```bash
DISPLAY=:99 python3 test_visual.py
```

## Running the Full Application

To run the complete application:

```bash
python3 "Digitalization_SERVINORTE(v2).py"
```

**Note:** A display server (X11) is required to run the GUI application.

### For headless environments:

1. Start Xvfb:
```bash
Xvfb :99 -screen 0 1024x768x24 &
```

2. Run the application:
```bash
DISPLAY=:99 python3 "Digitalization_SERVINORTE(v2).py"
```

## Test Results

All 12 unit tests pass successfully:
- ✅ test_add_to_cart
- ✅ test_calculate_cart_total
- ✅ test_clear_cart
- ✅ test_load_products_from_csv
- ✅ test_multiple_category_search
- ✅ test_multiple_orders_same_client
- ✅ test_remove_from_cart
- ✅ test_save_order_to_csv
- ✅ test_search_by_category
- ✅ test_search_by_code
- ✅ test_search_by_name
- ✅ test_stock_validation

## Features Implemented

1. **Product Search**: Real-time search by product code, name, or category
2. **Product Display**: Shows all matching products with price and stock information
3. **Product Details**: Displays detailed information including image placeholder, description, code, availability, and price
4. **Shopping Cart**: Add/remove items with quantity selection
5. **Stock Validation**: Prevents adding more items than available in stock
6. **Order Management**: Saves orders to CSV file with client code
7. **Multiple Orders**: Supports multiple orders per client
8. **Total Calculation**: Automatically calculates cart total

## Product Database

Products are stored in `productos.csv` with the following fields:
- `codigo`: Product code/barcode
- `nombre`: Product name
- `categoria`: Category (needles, knife, bobbin cases, etc.)
- `descripcion`: Product description
- `precio`: Price
- `stock`: Available quantity
- `imagen`: Image path (optional)

## Dependencies

- Python 3.6+
- tkinter (included with Python)
- Standard library: csv, datetime, os
