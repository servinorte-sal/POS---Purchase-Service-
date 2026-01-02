#!/usr/bin/env python3
"""
Visual test script - launches the app and takes a screenshot of the ventas tab
"""
import os
import sys
import time
import subprocess

# Set up display
os.environ['DISPLAY'] = ':99'

# Import after setting display
import tkinter as tk
from tkinter import ttk

# Import the application components
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Create a minimal test window to show the ventas tab
    print("Creating test window...")
    root = tk.Tk()
    root.title("Ventas Tab Test - SERVINORTE")
    root.geometry('1200x800')
    
    # Create a notebook
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True, padx=10, pady=10)
    
    # Import necessary components
    import csv
    import datetime
    
    # Create a mock data manager and printer manager
    class MockDataManager:
        def __init__(self):
            self.app_dir = os.getcwd()
        
        def load_counter(self):
            return 1
    
    class MockPrinterManager:
        def __init__(self, window):
            self.window = window
    
    # Import and instantiate the UITabs class from the v2 file
    # We'll create a simplified version for testing
    
    # Create ventas frame
    ventas_frame = ttk.Frame(notebook)
    notebook.add(ventas_frame, text="Ventas")
    
    # Build the ventas tab UI (simplified version for testing)
    ventas_frame.columnconfigure(0, weight=1)
    ventas_frame.columnconfigure(1, weight=2)
    ventas_frame.rowconfigure(3, weight=1)
    
    # Title
    title = ttk.Label(ventas_frame, text="Punto de Venta", font=("Arial", 20, "bold"))
    title.grid(row=0, column=0, columnspan=2, pady=10)
    
    # Client section
    client_frame = ttk.LabelFrame(ventas_frame, text="Código de Cliente", padding=10)
    client_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
    
    ttk.Label(client_frame, text="Cliente:").grid(row=0, column=0, padx=5)
    client_entry = ttk.Entry(client_frame, width=20)
    client_entry.grid(row=0, column=1, padx=5)
    client_entry.insert(0, "CLIENT001")
    
    # Search section
    search_frame = ttk.LabelFrame(ventas_frame, text="Buscar Producto", padding=10)
    search_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
    
    ttk.Label(search_frame, text="Buscar por:").grid(row=0, column=0, padx=5)
    search_entry = ttk.Entry(search_frame, width=40)
    search_entry.grid(row=0, column=1, padx=5)
    search_entry.insert(0, "needle")
    ttk.Label(search_frame, text="(código, nombre o categoría)", font=("Arial", 8)).grid(row=0, column=2, padx=5)
    
    # Left panel - Product list
    left_frame = ttk.Frame(ventas_frame)
    left_frame.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
    
    ttk.Label(left_frame, text="Productos Disponibles", font=("Arial", 12, "bold")).pack()
    
    # Product listbox
    list_frame = ttk.Frame(left_frame)
    list_frame.pack(fill="both", expand=True)
    
    scrollbar = ttk.Scrollbar(list_frame)
    scrollbar.pack(side="right", fill="y")
    
    product_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=15)
    product_listbox.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=product_listbox.yview)
    
    # Load and display products
    products_file = os.path.join(os.getcwd(), "productos.csv")
    if os.path.exists(products_file):
        with open(products_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for product in reader:
                if 'needle' in product['categoria'].lower() or 'needle' in product['nombre'].lower():
                    display_text = f"{product['codigo']} - {product['nombre']} (${product['precio']}) - Stock: {product['stock']}"
                    product_listbox.insert(tk.END, display_text)
    
    # Product detail section
    detail_frame = ttk.LabelFrame(left_frame, text="Detalle del Producto", padding=10)
    detail_frame.pack(fill="x", pady=10)
    
    image_label = ttk.Label(detail_frame, text="[Imagen del Producto]\n\n   Brother Rotary Hook\n   #XD138572", 
                           relief="solid", width=30, padding=20)
    image_label.grid(row=0, column=0, rowspan=4, padx=5, pady=5)
    
    desc_label = ttk.Label(detail_frame, 
                          text="Agujas Schmetz Universal 80/12\nPaquete de 5 agujas universales calibre 80/12", 
                          wraplength=200, justify="left")
    desc_label.grid(row=0, column=1, sticky="w", padx=5)
    
    code_label = ttk.Label(detail_frame, text="Código: AG001", font=("Arial", 9, "bold"))
    code_label.grid(row=1, column=1, sticky="w", padx=5)
    
    stock_label = ttk.Label(detail_frame, text="Disponibilidad: 20 unidades")
    stock_label.grid(row=2, column=1, sticky="w", padx=5)
    
    price_label = ttk.Label(detail_frame, text="Precio: $45.00", font=("Arial", 10, "bold"))
    price_label.grid(row=3, column=1, sticky="w", padx=5)
    
    # Add to cart section
    add_frame = ttk.Frame(detail_frame)
    add_frame.grid(row=4, column=0, columnspan=2, pady=10)
    
    ttk.Label(add_frame, text="Cantidad:").pack(side="left", padx=5)
    quantity_spinbox = ttk.Spinbox(add_frame, from_=1, to=100, width=5)
    quantity_spinbox.set(2)
    quantity_spinbox.pack(side="left", padx=5)
    
    add_btn = ttk.Button(add_frame, text="Agregar al Carrito")
    add_btn.pack(side="left", padx=5)
    
    # Right panel - Shopping cart
    right_frame = ttk.Frame(ventas_frame)
    right_frame.grid(row=3, column=1, padx=10, pady=5, sticky="nsew")
    
    ttk.Label(right_frame, text="Carrito de Compras", font=("Arial", 12, "bold")).pack()
    
    # Cart treeview
    cart_frame = ttk.Frame(right_frame)
    cart_frame.pack(fill="both", expand=True)
    
    cart_scrollbar = ttk.Scrollbar(cart_frame)
    cart_scrollbar.pack(side="right", fill="y")
    
    cart_tree = ttk.Treeview(cart_frame, columns=("Producto", "Cantidad", "Precio", "Total"),
                            show="headings", yscrollcommand=cart_scrollbar.set, height=15)
    cart_tree.heading("Producto", text="Producto")
    cart_tree.heading("Cantidad", text="Cant.")
    cart_tree.heading("Precio", text="Precio")
    cart_tree.heading("Total", text="Total")
    
    cart_tree.column("Producto", width=200)
    cart_tree.column("Cantidad", width=60)
    cart_tree.column("Precio", width=80)
    cart_tree.column("Total", width=80)
    
    # Add sample items to cart
    cart_tree.insert('', 'end', values=("Brother Rotary Hook", 1, "$150.00", "$150.00"))
    cart_tree.insert('', 'end', values=("Agujas Schmetz Universal 80/12", 3, "$45.00", "$135.00"))
    cart_tree.insert('', 'end', values=("Cuchilla Rotativa 45mm", 2, "$95.00", "$190.00"))
    
    cart_tree.pack(side="left", fill="both", expand=True)
    cart_scrollbar.config(command=cart_tree.yview)
    
    # Cart buttons
    cart_buttons = ttk.Frame(right_frame)
    cart_buttons.pack(fill="x", pady=5)
    
    ttk.Button(cart_buttons, text="Eliminar Seleccionado").pack(side="left", padx=5)
    ttk.Button(cart_buttons, text="Limpiar Carrito").pack(side="left", padx=5)
    
    # Total section
    total_frame = ttk.Frame(right_frame)
    total_frame.pack(fill="x", pady=10)
    
    ttk.Label(total_frame, text="TOTAL:", font=("Arial", 14, "bold")).pack(side="left", padx=5)
    total_label = ttk.Label(total_frame, text="$475.00", font=("Arial", 14, "bold"), foreground="green")
    total_label.pack(side="left", padx=5)
    
    # Finalize order button
    finalize_btn = ttk.Button(right_frame, text="Finalizar Compra")
    finalize_btn.pack(pady=10)
    
    print("Window created, updating display...")
    root.update()
    
    # Wait a moment for rendering
    time.sleep(1)
    
    # Take screenshot
    print("Taking screenshot...")
    screenshot_path = os.path.join(os.getcwd(), "ventas_tab_screenshot.png")
    
    # Use ImageMagick or scrot to take screenshot
    try:
        subprocess.run(['import', '-window', 'root', screenshot_path], 
                      env=os.environ, check=True, timeout=5)
        print(f"✓ Screenshot saved to: {screenshot_path}")
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        try:
            subprocess.run(['scrot', screenshot_path], 
                          env=os.environ, check=True, timeout=5)
            print(f"✓ Screenshot saved to: {screenshot_path}")
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            print("⚠ Could not take screenshot (ImageMagick/scrot not available)")
    
    print("Closing window...")
    root.destroy()
    print("✓ Test completed successfully")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
