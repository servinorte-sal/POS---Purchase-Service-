# POS---Purchase-Service-

POS (Point of Sale) system dedicated to register Work Orders, Product Database, and Sales Management including ticket printing station for SERVINORTE Saltillo.

## Features

### 📋 Work Orders (Orden de Trabajo)
- Customer information management
- Equipment tracking with serial numbers
- Service checklist (needles, bobbins, pedals, motors, etc.)
- Equipment type classification (domestic, industrial, sewing, overlock)
- Order printing capabilities
- Work order history

### 💰 Sales/POS (Ventas)
**NEW!** Fully functional Point of Sale system with:
- **Product Search**: Search by part number, name, or category (needles, knives, bobbin cases, etc.)
- **Real-time Filtering**: Auto-updating product list as you type
- **Product Details**: Shows image, description, stock availability, and pricing
- **Shopping Cart**: Add/remove items with quantity control
- **Stock Validation**: Prevents overselling with automatic stock checks
- **Client Management**: Associate orders with client codes
- **Order Processing**: Finalize and save orders to CSV
- **Multiple Orders**: Support for multiple orders per client

### 📊 Records (Registros)
- Search and view historical work orders
- Order tracking and management

## Quick Start

### Prerequisites
- Python 3.6 or higher
- tkinter (usually included with Python)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/servinorte-sal/POS---Purchase-Service-.git
cd POS---Purchase-Service-
```

2. Run the application:
```bash
python3 "Digitalization_SERVINORTE(v2).py"
```

### Product Database

The system uses a CSV-based product database (`productos.csv`). Sample products are included with:
- Needles (Agujas)
- Knives/Scissors (Cuchillas/Tijeras)
- Bobbin cases (Cajas de bobinas)
- Thread (Hilo)
- Motors (Motores)
- Belts (Bandas)
- Presser feet (Prensatelas)
- And more sewing machine parts and accessories

## Usage

### Using the Sales (Ventas) Tab

1. **Select Client**: Enter the client code
2. **Search Products**: Type in the search box to find products by:
   - Part number/barcode (e.g., "XD138572")
   - Product name (e.g., "Brother Rotary Hook")
   - Category (e.g., "needles", "knife", "bobbin cases")
3. **Add to Cart**: 
   - Select a product from the list
   - Set quantity
   - Click "Agregar al Carrito"
4. **Review Cart**: Check items, quantities, and total
5. **Finalize Order**: Click "Finalizar Compra" to save

### Data Files

- `productos.csv` - Product catalog
- `ventas.csv` - Sales orders (auto-created)
- `Registro Ordenes de Trabajo.csv` - Work orders
- `counter.txt` - Work order counter

## Testing

Comprehensive test suite included:

```bash
# Run unit tests
python3 test_ventas.py

# Run integration tests
python3 test_integration.py
```

See [TESTING.md](TESTING.md) for detailed testing information.

### Test Coverage
- ✅ 12 unit tests (100% passing)
- ✅ Product loading and search
- ✅ Cart operations
- ✅ Stock validation
- ✅ Order processing
- ✅ Multiple orders per client

## Security

The codebase has been scanned with CodeQL:
- ✅ **No vulnerabilities detected**
- ✅ Secure file handling
- ✅ Input validation implemented

## Screenshots

### Ventas (Sales/POS) Tab
![Ventas Tab](https://github.com/user-attachments/assets/c91d092b-38de-49df-8b1e-3c8db9ac296f)

The sales interface features:
- Client code entry
- Real-time product search
- Product list with prices and stock
- Product detail panel with image placeholder
- Shopping cart with automatic total calculation
- Order management buttons

## Development

### Project Structure
```
POS---Purchase-Service-/
├── Digitalization_SERVINORTE(v2).py  # Main application (recommended)
├── Digitalization_SERVINORTE.py      # Legacy version
├── productos.csv                      # Product database
├── test_ventas.py                     # Unit tests
├── test_integration.py                # Integration tests
├── test_visual.py                     # Visual/GUI tests
├── TESTING.md                         # Testing documentation
└── README.md                          # This file
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

© 2025 SERVINORTE Saltillo

## Contact

- Email: servinortesaclientes@gmail.com
- Address: Pérez Treviño #147, Centro, Saltillo
- Phone: (844) 311 5686

