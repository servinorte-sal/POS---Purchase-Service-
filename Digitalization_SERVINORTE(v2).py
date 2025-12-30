# -------------- IMPORTS ---------------
import tkinter as tk
from tkinter import ttk, messagebox
import platform
import datetime
import csv
import os
import subprocess
import json
import time
import threading
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import tempfile
import base64

# ------------Imports potenciales ------
# import _frozen_importlib_external
# import importlib._bootstrap
# import importlib.abc
# import zipimport

# import pickle

# import shutil
# import tarfile
# import posixpath
# import pathlib
# import netrc
# import getpass
# import http.server
# import webbrowser

# import platform
# import xml.sax
# import copy

# import multiprocessing
# import multiprocessing.connection
# import multiprocessing.resource_tracker
# import multiprocessing.shared_memory
# import multiprocessing.util
# import multiprocessing.pool
# import multiprocessing.managers
# import multiprocessing.sharedctypes

# import multiprocessing.util
# import urllib.request
# import getpass
# import reportlab.lib.pdfencrypt
# from reportlab.platypus.paragraph import pyphen


#-----------------Functions----------------


# ------------- DATA CLASSES --------------
@dataclass
class TicketConfig:
    """Configuración para generación de tickets"""
    paper_width: int = 42
    paper_width_chars: int = 42
    company_name: str = "SERVINORTE"
    company_address: str = "Pérez Treviño #147, Centro"
    company_phone: str = "(844) 311 5686"
    company_email: str = "servinortesaclientes@gmail.com"

#Tal vez Borrar.
@dataclass
class TicketData:
    """Datos para generar un ticket"""
    # Datos de orden
    no_orden: str
    ficha: str
    fecha: str
    cliente: str
    equipo: str
    no_serie: str
    diagnostico: str
    tel1: str
    tel2: str = ""
    direccion: str = ""
    taller_domi: str = "Taller"
    descripcion: str = ""
    
    # Estado del equipo
    aguja: bool = False
    bobina: bool = False
    carretel: bool = False
    devanador: bool = False
    estuche: bool = False
    foco: bool = False
    motor: bool = False
    banda: bool = False
    pedal: bool = False
    pie: bool = False
    hilo: bool = False
    abierta: bool = False
    tapa: bool = False
    otro_piezas: str = ""
    
    # Tipo de equipo
    casero: bool = False
    industrial: bool = False
    costura: bool = False
    sobrehiladora: bool = False
    otro_tipo: str = ""
    
    # Servicios
    servicios: List[Tuple[str, float]] = None
    
    def __post_init__(self):
        if self.servicios is None:
            self.servicios = []

#------------------------------------------
#---------------- Classes -----------------
#------------------------------------------

#----------------TICKETS-------------------
class TicketGenerator:

    def __init__(self, config: TicketConfig):
        self.config = config
        self.width = config.paper_width
        self.width_chars = config.paper_width_chars

    def _escpos_center(self, text):
        return b'\x1B\x61\x01' + text.encode('cp437', errors='replace') + b'\n'
    
    def _escpos_left(self, text):
        """Alinear izquierda usando ESC/POS"""
        return b'\x1B\x61\x00' + text.encode('cp437', errors='replace') + b'\n'
    
    def format_two_columns(self, left, right, width_left=20):
        """Formato de dos columnas"""
        width_right = self.width - width_left - 1
        left_part = left[:width_left].ljust(width_left)
        right_part = str(right)[:width_right].ljust(width_right)
        return f"{left_part} {right_part}\n"
    
    def format_table_row(self, service, cost, width_service=28):
        """Formato para tabla de servicios"""
        width_cost = self.width - width_service - 1
        # Si el servicio cabe en una línea
        if len(service) <= width_service:
            service_part = service.ljust(width_service)
            cost_part = f"${str(cost)}".rjust(width_cost)
            return f"{service_part} {cost_part}\n"
        
        # Si el servicio es largo, dividirlo
        result = ""
        words = service.split()
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 <= width_service:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
            else:
                # Primera línea con costo
                if not result:  # Es la primera línea
                    service_part = current_line.ljust(width_service)
                    cost_part = f"${str(cost)}".rjust(width_cost)
                    result += f"{service_part} {cost_part}\n"
                else:
                    # Líneas siguientes sin costo
                    result += f"{current_line.ljust(width_service)}{' ' * (width_cost + 1)}\n"
                
                current_line = word
        # Última línea
        if current_line:
            if not result:  # Si solo hubo una línea
                service_part = current_line.ljust(width_service)
                cost_part = f"${str(cost)}".rjust(width_cost)
                result += f"{service_part} {cost_part}\n"
            else:
                # Línea final sin costo
                result += f"{current_line.ljust(width_service)}{' ' * (width_cost + 1)}\n"
        return result
 
    def generate_ticket(self, data: Dict) -> bytes:
        ticket = bytearray()
        
        # 1. INICIALIZAR IMPRESORA
        ticket.extend(b'\x1B\x40')  # Inicializar impresora
        ticket.extend(b'\x1B\x61\x01')  # Centrar texto
        
        # 2. ENCABEZADO DE LA EMPRESA
        ticket.extend(b'\x1B\x61\x01')
        company_header = (
            self.config.company_name + "\n" + 
            self.config.company_address + "\n" + 
            "C.P. 25000, Saltillo, Coahuila\n" + 
            self.config.company_phone + "\n" + 
            "R.F.C.AUSN740518G12 RESICO\n" + 
            self.config.company_email + "\n\n\n"
        )
        ticket.extend(company_header.encode('cp437', errors='replace'))
        
        # 3. TÍTULO ORDEN DE SERVICIO
        ticket.extend(b'\x1B\x45\x01')  # Negrita ON
        ticket.extend("ORDEN DE SERVICIO".encode('cp437', errors='replace'))
        ticket.extend(b'\n')
        ticket.extend(b'\x1B\x45\x00')  # Negrita OFF
        
        # 4. DATOS DE LA ORDEN
        ticket.extend(b'\x1B\x61\x00')  # Izquierda
        orden_info = (
            self.format_two_columns("No. Orden:", data.get("no_orden", ""), width_left=15) +
            self.format_two_columns("Fecha:", data.get("fecha", ""), width_left=15) +
            self.format_two_columns("Ficha:", data.get("ficha", ""), width_left=15) +
            self.format_two_columns("Taller/Domicilio:", data.get("taller_domi", ""), width_left=20)
        )
        ticket.extend(orden_info.encode('cp437', errors='replace'))
        
        # 5. DATOS DEL CLIENTE
        ticket.extend(b'\x1B\x61\x01')  # Centrar
        ticket.extend(b'\x1B\x45\x01')  # Negrita ON
        ticket.extend("DATOS DEL CLIENTE".encode('cp437', errors='replace'))
        ticket.extend(b'\n')
        ticket.extend(b'\x1B\x45\x00')  # Negrita OFF
        ticket.extend(b'\x1B\x61\x00')  # Volver a izquierda
        
        cliente_info = self.format_two_columns("Cliente:", data.get("cliente", ""), width_left=15)
        cliente_info += self.format_two_columns("Teléfono 1:", data.get("tel1", ""), width_left=15)
        
        if data.get("tel2"):
            cliente_info += self.format_two_columns("Teléfono 2:", data["tel2"], width_left=15)
        if data.get("direccion"):
            cliente_info += self.format_two_columns("Dirección:", data["direccion"], width_left=15)
        
        ticket.extend(cliente_info.encode('cp437', errors='replace'))
        
        # 6. DATOS DEL EQUIPO
        ticket.extend(b'\x1B\x61\x01')  # Centrar
        ticket.extend(b'\x1B\x45\x01')  # Negrita ON
        ticket.extend("DATOS DEL EQUIPO".encode('cp437', errors='replace'))
        ticket.extend(b'\n')
        ticket.extend(b'\x1B\x45\x00')  # Negrita OFF
        ticket.extend(b'\x1B\x61\x00')  # Volver a izquierda
        
        equipo_info = (
            self.format_two_columns("Equipo:", data.get("equipo", ""), width_left=15) +
            self.format_two_columns("No. Serie:", data.get("no_serie", ""), width_left=15) +
            self.format_two_columns("Descripción:", data.get("descripcion", ""), width_left=15)
        )
        
        # Ramo (tipo de equipo)
        ramo_text = ""
        if data.get("casero"): ramo_text += "Casero "
        if data.get("industrial"): ramo_text += "Industrial "
        if data.get("costura"): ramo_text += "Costura "
        if data.get("sobrehiladora"): ramo_text += "Sobrehiladora "
        if data.get("otro_tipo"): ramo_text += data.get("otro_tipo", "")
        
        equipo_info += self.format_two_columns("Ramo:", ramo_text.strip(), width_left=15)
        
        # Estado (piezas faltantes)
        estado_text = "Le falta: "
        piezas_faltantes = []
        piezas = ["aguja", "bobina", "carretel", "devanador", "estuche", 
                 "foco", "motor", "banda", "pedal", "pie", "hilo", 
                 "abierta", "tapa", "otro_piezas"]
        
        for pieza in piezas:
            if data.get(pieza):
                if pieza == "otro_piezas" and data[pieza]:
                    piezas_faltantes.append(data[pieza])
                elif pieza != "otro_piezas":
                    piezas_faltantes.append(pieza.capitalize())
        
        estado_text += ", ".join(piezas_faltantes) if piezas_faltantes else "Nada"
        equipo_info += self.format_two_columns("Estado:", estado_text, width_left=15)
        
        # Diagnóstico
        equipo_info += self.format_two_columns("Diagnóstico:", data.get("diagnostico", ""), width_left=15)
        ticket.extend(equipo_info.encode('cp437', errors='replace'))
        
        # 7. SERVICIOS
        ticket.extend(b'\x1B\x61\x01')  # Centrar
        ticket.extend(b'\x1B\x45\x01')  # Negrita ON
        ticket.extend("SERVICIOS".encode('cp437', errors='replace'))
        ticket.extend(b'\n')
        ticket.extend(b'\x1B\x45\x00')  # Negrita OFF
        ticket.extend(b'\x1B\x61\x00')  # Volver a izquierda
        
        servicios = []
        for i in range(1, 5):
            servicio = data.get(f"servicio{i}", "")
            costo = data.get(f"costo{i}", "0")
            if servicio and costo and costo != "0":
                servicios.append((servicio, costo))
        
        total = 0
        servicios_text = ""
        for servicio, costo in servicios:
            try:
                costo_float = float(costo)
                total += costo_float
                servicios_text += self.format_table_row(servicio, f"{costo_float:.2f}", width_service=28)
            except ValueError:
                servicios_text += self.format_table_row(servicio, costo, width_service=28)
        
        ticket.extend(servicios_text.encode('cp437', errors='replace'))
        
        # TOTAL
        total_line = "TOTAL".ljust(28) + f"${total:.2f}".rjust(14) + "\n"
        ticket.extend(b'\x1B\x45\x01')  # Negrita ON
        ticket.extend(total_line.encode('cp437', errors='replace'))
        ticket.extend(b'\x1B\x45\x00')  # Negrita OFF
        
        # 8. NOTAS
        ticket.extend(b'\x1B\x61\x01')  # Centrar
        ticket.extend("NOTAS".encode('cp437', errors='replace'))
        ticket.extend(b'\n')
        ticket.extend(b'\x1B\x61\x00')  # Izquierda
        
        ticket.extend(b'\x1B\x61\x00') 
        ticket.extend(b'\x1B\x45\x01')  # Negrita ON
        ticket.extend("NOTAS IMPORTANTES".encode('cp437', errors='replace'))
        ticket.extend(b'\n')
        ticket.extend(b'\x1B\x45\x00')  # Negrita OFF
        
        notas = [
            "Garantía 30 días por misma falla",
            "Refacciones y domicilio tienen \n costo extra",
            "Equipos no reclamados en 6 meses",
            "se cobra almacenamiento."
        ]
        
        for nota in notas:
            ticket.extend(nota.encode('cp437', errors='replace'))
            ticket.extend(b'\n')
        
        ticket.extend(b'\n')
        
        # 9. PIE
        ticket.extend(b'\x1B\x61\x01')  # Centrar
        ticket.extend(b'\x1B\x45\x01')  # Negrita ON
        ticket.extend("GRACIAS POR SU PREFERENCIA".encode('cp437', errors='replace'))
        ticket.extend(b'\n')
        ticket.extend(b'\x1B\x45\x00')  # Negrita OFF
        ticket.extend(b'\x1B\x61\x00')  # Izquierda
        
        # 10. FIRMAS
        ticket.extend(b'\n')
        ticket.extend("Firma: ________________\n\n\n".encode('cp437', errors='replace'))
        ticket.extend("Fecha: ________________\n\n".encode('cp437', errors='replace'))
        
        # 11. FINALIZAR
        ticket.extend(b'\n\n\n')
        ticket.extend(b'\x1D\x56\x00')  # Cortar papel
        
        print(f"✅ Ticket #{data.get('no_orden', 'N/A')} generado ({len(ticket)} bytes)")
        return bytes(ticket)
#---------------DECORADORES----------------
# Decorador para medir tiempo de ejecución
def medir_tiempo(func):
    def wrapper(*args, **kwargs):
        inicio = time.time()
        resultado = func(*args, **kwargs)
        fin = time.time()
        print(f"{func.__name__} tardó {fin-inicio:.2f} segundos")
        return resultado
    return wrapper

# Decorador para manejar errores de impresión
def manejar_errores_impresion(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Error: Archivo no encontrado")
            return False
        except PermissionError:
            print("Error: Permiso denegado")
            return False
        except Exception as e:
            print(f"Error inesperado: {e}")
            return False
    return wrapper

#-------------PRRINTER MANAGER-------------
class PrinterManager:
    
    def __init__(self, parent_window=None):
        self.parent = parent_window
        self.system = platform.system()
        print(f"PrinterManager inicializado para {self.system}")
    
    @manejar_errores_impresion
    def print_ticket(self, ticket_content: bytes) -> bool:
        # Guardar temporalmente
        print(f"Intentando imprimir ticket ({len(ticket_content)} bytes)...")
        temp_file = self._save_temp_file(ticket_content)
        
        if self.system == "Windows":
            return self._print_windows(temp_file)
        elif self.system == "Linux":
            return self._print_linux(temp_file)
        else:
            print(f"Sistema no soportado: {self.system}")
            self._show_error(f"Sistema operativo no soportado: {self.system}")
            return False
        
    def _save_temp_file(self, content: bytes) -> str:
        import tempfile
        import time

        temp_dir = tempfile.gettempdir()
        timestamp = int(time.time())
        temp_file = os.path.join(temp_dir, f"ticket_servinorte_{timestamp}.txt")
        with open(temp_file, 'wb') as f:
            f.write(content)
        print(f"Archivo temporal creado: {temp_file}")
        return temp_file

    def _print_windows(self, filepath: str) -> bool:
        """Lógica de impresión para Windows"""
        print("Usando método Windows...")
        
        # Método 1: Notepad (el más confiable)
        if self._print_windows_notepad(filepath):
            return True
        
        # Método 2: PowerShell
        if self._print_windows_powershell(filepath):
            return True
        
        # Método 3: Mostrar instrucciones
        self._show_windows_instructions(filepath)
        return False
    
    def _print_windows_notepad(self, filepath: str) -> bool:
        """Impresión usando Notepad"""
        try:
            import subprocess
            import time
            
            # Comando para imprimir con Notepad
            cmd = f'notepad /p "{filepath}"'
            
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Pequeña pausa
            time.sleep(1)
            
            # Limpiar archivo temporal después de 15 segundos
            def limpiar_temporal():
                time.sleep(15)
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        print(f"🧹 Temporal limpiado: {filepath}")
                except:
                    pass
            
            import threading
            thread = threading.Thread(target=limpiar_temporal)
            thread.daemon = True
            thread.start()
            
            print("Notepad recibió el trabajo de impresión")
            return True
            
        except Exception as e:
            print(f"Error Notepad: {e}")
            return False
    
    def _print_windows_powershell(self, filepath: str) -> bool:
        """Impresión usando PowerShell"""
        try:
            import subprocess
            import base64
            
            # Leer y codificar archivo en base64
            with open(filepath, 'rb') as f:
                contenido = f.read()
            
            contenido_b64 = base64.b64encode(contenido).decode('ascii')
            
            # Script PowerShell
            ps_script = f"""
            $bytes = [System.Convert]::FromBase64String('{contenido_b64}')
            $tempFile = [System.IO.Path]::GetTempFileName() + "_ticket.txt"
            [System.IO.File]::WriteAllBytes($tempFile, $bytes)
            Start-Process -FilePath $tempFile -Verb Print -WindowStyle Hidden
            Start-Sleep -Seconds 2
            """
            
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                print("PowerShell imprimió exitosamente")
                return True
            else:
                print(f"PowerShell falló: {result.stderr[:200]}")
                return False
                
        except Exception as e:
            print(f"Error PowerShell: {e}")
            return False
    
    def _print_linux(self, filepath: str) -> bool:
        """Lógica de impresión para Linux"""
        print("Usando método Linux...")
        
        try:
            # Verificar archivo
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"No se encontró: {filepath}")
            
            # Leer contenido
            with open(filepath, 'rb') as f:
                ticket_data = f.read()
            
            # Intentar dispositivos USB comunes
            dispositivos = ['/dev/usb/lp0', '/dev/usb/lp1', '/dev/usb/lp2', '/dev/ttyUSB0']
            impreso = False
            
            for dispositivo in dispositivos:
                if os.path.exists(dispositivo):
                    print(f"Intentando imprimir en {dispositivo}...")
                    try:
                        with open(dispositivo, 'wb') as impresora:
                            impresora.write(ticket_data)
                        print(f"Ticket impreso en {dispositivo}")
                        impreso = True
                        break
                    except PermissionError:
                        print(f"Permiso denegado para {dispositivo}")
                        self._show_error(
                            f"Permiso denegado para {dispositivo}\n\n"
                            "Ejecuta en terminal:\n"
                            f"sudo chmod 666 {dispositivo}"
                        )
                        break
                    except Exception as e:
                        print(f"Error con {dispositivo}: {e}")
                        continue
            
            if not impreso:
                print("Impresora no detectada")
                self._show_error(
                    "Impresora no detectada.\n"
                    "1. Conecta la impresora USB\n"
                    "2. Verifica que esté encendida\n"
                    "3. Reintenta"
                )
                return False
            
            # Limpiar archivo temporal
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    print(f" Temporal limpiado: {filepath}")
            except:
                pass
            
            return True
            
        except Exception as e:
            print(f" Error en Linux: {e}")
            self._show_error(f"Error en Linux:\n{str(e)}")
            return False
    
    def _show_windows_instructions(self, filepath: str):
        """Muestra instrucciones para impresión manual en Windows"""
        from tkinter import Toplevel, Label, Text, Scrollbar, Frame, Button
        import tkinter as tk
        
        if not self.parent:
            return
        
        popup = Toplevel(self.parent)
        popup.title("🔥 IMPRESIÓN MANUAL REQUERIDA")
        popup.geometry("700x550")
        
        # Hacer modal
        popup.transient(self.parent)
        popup.grab_set()
        
        # Frame principal
        main_frame = Frame(popup)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        Label(main_frame, text="🔥 IMPRESIÓN MANUAL REQUERIDA", 
              font=("Arial", 14, "bold"), fg="red").pack(pady=(0, 15))
        
        Label(main_frame, text="No se pudo imprimir automáticamente. Sigue estos pasos:",
              font=("Arial", 10)).pack(pady=(0, 10))
        
        # Texto con scroll
        text_frame = Frame(main_frame)
        text_frame.pack(fill="both", expand=True)
        
        text_widget = Text(text_frame, wrap="word", font=("Consolas", 9), height=20)
        scrollbar = Scrollbar(text_frame, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Contenido
        contenido = f"""📋 INSTRUCCIONES PASO A PASO:

        1.  LOCALIZA EL ARCHIVO:
        Ruta exacta: 
        {filepath}

        2.  ABRE EL ARCHIVO:
        • Haz DOBLE CLIC en el archivo arriba
        • O usa CTRL+O en el Bloc de Notas

        3.  IMPRIME:
        • Presiona CTRL + P
        • O ve a: Archivo → Imprimir

        4.  CONFIGURA LA IMPRESORA:
        • Selecciona tu impresora térmica
        • Ve a: Propiedades → Avanzadas
        • Tipo de documento: RAW
        • O usa driver: "Generic / Text Only"

        5.  AJUSTES ESPECÍFICOS:
        • Tamaño: Personalizado
        • Ancho: 58mm (2.28")
        • Alto: Dejar en blanco
        • Orientación: Vertical

        SOLUCIONES A PROBLEMAS COMUNES:

        "No aparece mi impresora":
        • Ve a Panel de Control → Impresoras
        • Agrega como impresora local
        • Conéctala y enciéndela primero

        "Imprime código extraño":
        • Cambia a driver "RAW"
        • O selecciona "Texto plano"

        "No imprime nada":
        • Reinicia la impresora
        • Prueba imprimir una página de prueba
        • Verifica los niveles de tinta/papel

        CONSEJO FINAL:
        Antes de imprimir el ticket, haz una 
        prueba desde el Panel de Control."""
        
        text_widget.insert("1.0", contenido)
        text_widget.config(state="disabled")
        
        # Botones
        btn_frame = Frame(main_frame)
        btn_frame.pack(pady=15)
        
        def ejecutar_accion(accion):
            try:
                if accion == "abrir":
                    os.startfile(filepath)
                elif accion == "carpeta":
                    os.startfile(os.path.dirname(filepath))
                elif accion == "impresoras":
                    os.system("control printers")
                elif accion == "cerrar":
                    popup.destroy()
            except Exception as e:
                print(f"Error en {accion}: {e}")
        
        Button(btn_frame, text="Abrir Ticket", 
               command=lambda: ejecutar_accion("abrir")).pack(side="left", padx=5)
        
        Button(btn_frame, text="Abrir Carpeta", 
               command=lambda: ejecutar_accion("carpeta")).pack(side="left", padx=5)
        
        Button(btn_frame, text="Ver Impresoras", 
               command=lambda: ejecutar_accion("impresoras")).pack(side="left", padx=5)
        
        Button(btn_frame, text="Cerrar", 
               command=lambda: ejecutar_accion("cerrar")).pack(side="left", padx=5)
        
        # Centrar
        popup.update_idletasks()
        ancho = popup.winfo_width()
        alto = popup.winfo_height()
        x = (popup.winfo_screenwidth() // 2) - (ancho // 2)
        y = (popup.winfo_screenheight() // 2) - (alto // 2)
        popup.geometry(f'{ancho}x{alto}+{x}+{y}')
    
    def _show_error(self, message: str):
        if self.parent:
            from tkinter import messagebox
            messagebox.showerror("Error de impresión", message, parent=self.parent)

# ------------- DATA MANAGER --------------
class DataManager:
    
    def __init__(self, app_directory: str):
        self.app_dir = app_directory
        self.counter_file = os.path.join(app_directory, "counter.txt")
        self.orders_file = os.path.join(app_directory, "Registro Ordenes de Trabajo.csv")
        self.equipment_file = os.path.join(app_directory, "Estado de equipos.csv")
        self.types_file = os.path.join(app_directory, "Tipos de equipos.csv")

        self._initialize_files()
    
    def load_counter(self) -> int:
        """Carga el contador actual - VERSIÓN MÁS ROBUSTA"""
        print(f"📖 Intentando cargar contador de: {self.counter_file}")
        
        try:
            # Si el archivo no existe, crearlo con valor 1
            if not os.path.exists(self.counter_file):
                print(f"📄 Archivo {self.counter_file} no existe, creando...")
                self.save_counter(1)
                return 1
            
            # Leer el archivo
            with open(self.counter_file, 'r', encoding='utf-8') as f:
                contenido = f.read().strip()
                print(f"📄 Contenido leído: '{contenido}'")
            
            # Verificar que no esté vacío
            if not contenido:
                print("⚠️ Archivo counter.txt está vacío, usando 1")
                self.save_counter(1)
                return 1
            
            # Convertir a entero
            try:
                counter = int(contenido)
                print(f"✅ Contador cargado correctamente: {counter}")
                return counter
                
            except ValueError:
                print(f"⚠️ Contador no es número válido: '{contenido}', usando 1")
                self.save_counter(1)
                return 1
                
        except PermissionError:
            print("❌ Error de permisos al leer counter.txt")
            return 1
        except Exception as e:
            print(f"❌ Error inesperado cargando contador: {e}")
            return 1
        
    def save_counter(self, counter: int):
        try:
            print(f"Guardando contador #{counter} en {self.counter_file}")
            
            with open(self.counter_file, 'w', encoding='utf-8') as f:
                f.write(str(counter))
            
            # Verificar que se guardó correctamente
            if os.path.exists(self.counter_file):
                with open(self.counter_file, 'r', encoding='utf-8') as f:
                    contenido = f.read().strip()
                    print(f"✅ Contador verificado: '{contenido}' (debería ser: {counter})")
                    
                    if contenido != str(counter):
                        print("⚠️  ¡ADVERTENCIA! El contador no se guardó correctamente")
                        # Reintentar
                        with open(self.counter_file, 'w', encoding='utf-8') as f:
                            f.write(str(counter))
                        print("Reintentado...")
            
        except Exception as e:
            print(f"Error grave guardando contador: {e}")
            # Intentar crear el archivo si no existe
            try:
                with open(self.counter_file, 'w', encoding='utf-8') as f:
                    f.write(str(counter))
                print(f"Archivo counter.txt creado con valor: {counter}")
            except Exception as e2:
                print(f"Error crítico: {e2}")

    def _initialize_files(self):
        """Crea los archivos CSV si no existen"""
        # Archivo de órdenes
        if not os.path.exists(self.orders_file):
            with open(self.orders_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow([
                    'No_Orden', 'Ficha', 'Fecha', 'Cliente', 'Equipo',
                    'No_Serie', 'Diagnostico', 'Tel1', 'Tel2', 'Direccion',
                    'Taller_Domicilio', 'Descripcion'
                ])
        
        # Archivo de estado de equipos
        if not os.path.exists(self.equipment_file):
            with open(self.equipment_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(['No_Orden', 'Estado'])
        
        # Archivo de tipos de equipos
        if not os.path.exists(self.types_file):
            with open(self.types_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(['No_Orden', 'Tipo'])
        
    def save_order(self, order_data: Dict) -> int:
        current_counter = self.load_counter()

        row = [
            current_counter,  # No_Orden
            order_data.get('turno', ''),  # Ficha
            order_data.get('fecha', ''),  # Fecha
            order_data.get('nombre', ''),  # Cliente
            order_data.get('equipo', ''),  # Equipo
            order_data.get('serie', ''),  # No_Serie
            order_data.get('diagnostico', ''),  # Diagnostico
            order_data.get('tel1', ''),  # Tel1
            order_data.get('tel2', ''),  # Tel2
            order_data.get('direccion', ''),  # Direccion
            order_data.get('taller_domi', ''),  # Taller_Domicilio
            order_data.get('descripcion', '')  # Descripcion
        ]

        # Guardar en archivo CSV
        with open(self.orders_file, 'a', newline='', encoding="UTF-8") as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(row)
        
        # Incrementar contador
            self.save_counter(self.load_counter() + 1)
            return self.load_counter()

        if 'servicios' in order_data:
            self._save_services(current_counter, order_data['servicios'])
            
            # Incrementar y guardar contador
            self.save_counter(current_counter + 1)
            return current_counter
    
    def _save_services(self, order_number: int, servicios: List[Tuple[str, str]]):
        """Guarda los servicios asociados a una orden"""
        services_file = os.path.join(self.app_dir, "Servicios.csv")
        
        # Crear archivo si no existe
        if not os.path.exists(services_file):
            with open(services_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(['No_Orden', 'Servicio', 'Costo'])
        
        # Guardar cada servicio
        with open(services_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            for servicio, costo in servicios:
                if servicio.strip():  # Solo guardar si hay servicio
                    writer.writerow([order_number, servicio.strip(), costo.strip()])
    
    def save_checkboxes(self, order_number: int, piezas_faltantes: List[str], 
                       tipos_equipo: List[str]):
        """Guarda datos de checkboxes"""
        # Guardar estado del equipo
        estado_text = ", ".join(piezas_faltantes) if piezas_faltantes else "Nada"
        with open(self.equipment_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow([order_number, estado_text])
        
        # Guardar tipos de equipo
        tipo_text = ", ".join(tipos_equipo) if tipos_equipo else "No especificado"
        with open(self.types_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow([order_number, tipo_text])
    
    def load_counter(self) -> int:
        """Carga el contador actual"""
        try:
            with open(self.counter_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    return int(content)
                else:
                    return 1
        except (FileNotFoundError, ValueError):
            # Si el archivo no existe o está vacío, empezar en 1
            return 1
    
    def save_order_with_number(self, order_data: Dict, order_number: int) -> int:
        """Guarda una orden con un número específico"""
        print(f"Guardando orden #{order_number}")
        
        # Preparar fila para CSV
        row = [
            order_number,  # Usar el número proporcionado
            order_data.get('turno', ''),
            order_data.get('fecha', ''),
            order_data.get('nombre', ''),
            order_data.get('equipo', ''),
            order_data.get('serie', ''),
            order_data.get('diagnostico', ''),
            order_data.get('tel1', ''),
            order_data.get('tel2', ''),
            order_data.get('direccion', ''),
            order_data.get('taller_domi', ''),
            order_data.get('descripcion', '')
        ]
        
        # Guardar en archivo CSV
        with open(self.orders_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(row)
        
        # Actualizar contador SOLO si es mayor al actual
        current_counter = self.load_counter()
        if order_number >= current_counter:
            self.save_counter(order_number + 1)
            print(f"🔢 Contador actualizado a: {order_number + 1}")
        
        return order_number
    
# ---------------UI TABS-------------------
class UITabs:
    def __init__(self, notebook, data_manager, printer_manager):
        self.notebook = notebook
        self.data_mgr = data_manager
        self.printer_mgr = printer_manager
        saved_counter = self.data_mgr.load_counter()  # IMPORTANTE
        self.counter = saved_counter
        print(f"Contador cargado: {saved_counter}, mostrando: {self.counter}")

        # Inicializar TODOS los atributos que usas en el método
        self.name_entry = None
        self.phone1_entry = None
        self.phone2_entry = None
        self.adress_entry = None
        self.notes_entry = None
        self.equip_entry = None
        self.serial_entry = None
        self.desc_entry = None
        self.other_equip_entry = None
        self.other_entry = None
        self.turn_entry = None
        self.date_entry = None
        self.entry1 = None
        self.entry2 = None
        self.entry3 = None
        self.entry4 = None
        self.entries5 = None
        self.entries6 = None
        self.entries7 = None
        self.entries8 = None
        self.order_text = None
        self.desc_text = None
        
        # Checkboxes (¡usa el diccionario que ya definiste!)
        self.chkbx_vars = {}
        for i in range(1, 18):
            self.chkbx_vars[i] = tk.StringVar()
        
        # Domicilio
        self.Domicilio_var = tk.IntVar()
        
        # Fecha global (necesitas esto)
        today_date = datetime.date.today()
        self.date_format = today_date.strftime("%d - %m - %Y")
        
        # Inicializar UI
        self._setup_ui()
    
    def _setup_ui(self):
        self.tab_work_order = ttk.Frame(self.notebook)
        self.tab_sales = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_work_order, text="Orden de trabajo")
        self.notebook.add(self.tab_sales, text="Hoja de Ventas")
        
        self._create_work_order_tab()
        self._create_sales_tab()
    
    def _create_work_order_tab(self):
        tab = self.tab_work_order
        # Section 1 data
        title1 = ttk.Label(tab, text="Datos del cliente", font="Arial, 18")
        title1.grid(row=0, column=0, columnspan=9, padx=10, pady=5)

        # Separator
        line1 = ttk.Separator(tab, orient="horizontal")
        line1.grid(row=1, column=0, columnspan=9, sticky="ew")

        # Empty label
        empty1 = tk.Label(tab, text="")
        empty1.grid(row=1, column=0, padx=0, pady=0, sticky="e")

        # Name
        name_text = tk.Label(tab, text="Nombre: ", font="Arial, 14")
        name_text.grid(row=2, column=0, padx=0, pady=0, sticky="e")

        self.name_entry = tk.Entry(tab, width=40)
        self.name_entry.grid(row=2, column=1, padx=0, pady=0)

        # Phone number1
        phone1_text = tk.Label(tab, text="Teléfono: ", font="Arial, 14")
        phone1_text.grid(row=3, column=0, padx=0, pady=0, sticky="e")

        self.phone1_entry = tk.Entry(tab, width=40)
        self.phone1_entry.grid(row=3, column=1, padx=0, pady=0)

        # Phone number2
        phone2_text = tk.Label(tab, text="Teléfono2: ", font="Arial, 14")
        phone2_text.grid(row=4, column=0, padx=0, pady=0, sticky="e")

        self.phone2_entry = tk.Entry(tab, width=40)
        self.phone2_entry.grid(row=4, column=1, padx=0, pady=0)

        # Directions
        adress_text = tk.Label(tab, text="Dirección: ", font="Arial, 14")
        adress_text.grid(row=5, column=0, padx=0, pady=0, sticky="e")

        self.adress_entry = tk.Entry(tab, width=40)
        self.adress_entry.grid(row=5, column=1, padx=0, pady=0)

        # Notes
        notes_text = tk.Label(tab, text="Diagnostico: ", font="Arial, 14")
        notes_text.grid(row=6, column=0, padx=0, pady=0, sticky="e")

        self.notes_entry = tk.Entry(tab, width=40)
        self.notes_entry.grid(row=6, column=1, padx=0, pady=0)

        # Separator
        line2 = ttk.Separator(tab, orient="horizontal")
        line2.grid(row=7, column=0, columnspan=9, sticky="ew")

        # Empty label
        empty2 = tk.Label(tab, text="")
        empty2.grid(row=8, column=0, padx=0, pady=0, sticky="e")
        
        # Section 2 data
        title2 = ttk.Label(tab, text="Datos del equipo", font="Arial, 18")
        title2.grid(row=9, column=0, columnspan=9, padx=10, pady=5)

        # Equipment name
        equip_text = tk.Label(tab, text="Equipo: ", font="Arial, 14")
        equip_text.grid(row=10, column=0, padx=0, pady=0, sticky="e")

        self.equip_entry = tk.Entry(tab, width=40)
        self.equip_entry.grid(row=10, column=1, padx=0, pady=0)

        # Serial number
        serial_text = tk.Label(tab, text="No. Serie: ", font="Arial, 14")
        serial_text.grid(row=11, column=0, padx=0, pady=0, sticky="e")

        self.serial_entry = tk.Entry(tab, width=40)
        self.serial_entry.grid(row=11, column=1, padx=0, pady=0)

        # Description
        descrip_text = tk.Label(tab, text="Descripción: ", font="Arial, 14")
        descrip_text.grid(row=12, column=0, padx=0, pady=0, sticky="e")

        self.desc_entry = tk.Entry(tab, width=40)
        self.desc_entry.grid(row=12, column=1, padx=0, pady=0)

        # Separator
        line3 = ttk.Separator(tab, orient="horizontal")
        line3.grid(row=13, column=0, columnspan=9, sticky="ew")

        check_text = tk.Label(tab, text="Chequeo\t", font="Arial, 18")
        check_text.grid(row=14, column=0, columnspan=9, padx=0, pady=5)

        # Checklist - ¡USANDO EL DICCIONARIO chkbx_vars!
        self.chkbx1 = ttk.Checkbutton(tab, text="Aguja\t\t", 
                                      variable=self.chkbx_vars[1])
        self.chkbx1.grid(row=15, column=0, padx=20)

        self.chkbx2 = ttk.Checkbutton(tab, text="Bobina\t\t", 
                                      variable=self.chkbx_vars[2])
        self.chkbx2.grid(row=16, column=0)

        ttk.Checkbutton(tab, text="Carretel\t\t", 
                       variable=self.chkbx_vars[3]).grid(row=17, column=0)

        ttk.Checkbutton(tab, text="Devanador\t", 
                       variable=self.chkbx_vars[4]).grid(row=18, column=0)
        
        ttk.Checkbutton(tab, text="Estuche/bolsa\t", 
                       variable=self.chkbx_vars[5]).grid(row=19, column=0)

        ttk.Checkbutton(tab, text="Foco\t\t", 
                       variable=self.chkbx_vars[6]).grid(row=20, column=0)

        ttk.Checkbutton(tab, text="Motor\t\t", 
                       variable=self.chkbx_vars[7]).grid(row=15, column=1)

        ttk.Checkbutton(tab, text="Banda\t\t", 
                       variable=self.chkbx_vars[8]).grid(row=16, column=1)

        ttk.Checkbutton(tab, text="Pedal\t\t", 
                       variable=self.chkbx_vars[9]).grid(row=17, column=1)

        ttk.Checkbutton(tab, text="Pie\t\t", 
                       variable=self.chkbx_vars[10]).grid(row=18, column=1)

        ttk.Checkbutton(tab, text="Hilo\t\t", 
                       variable=self.chkbx_vars[11]).grid(row=19, column=1)

        # Branch type of equipment
        ttk.Checkbutton(tab, text="Casero\t\t", 
                       variable=self.chkbx_vars[12]).grid(row=15, column=2)

        ttk.Checkbutton(tab, text="Industrial\t", 
                       variable=self.chkbx_vars[13]).grid(row=16, column=2)

        ttk.Checkbutton(tab, text="Costura\t\t", 
                       variable=self.chkbx_vars[14]).grid(row=18, column=2)

        ttk.Checkbutton(tab, text="Sobrehiladora\t", 
                       variable=self.chkbx_vars[15]).grid(row=19, column=2)

        ttk.Checkbutton(tab, text="Abierta\t\t",
                       variable=self.chkbx_vars[16]).grid(row=21, column=0)

        ttk.Checkbutton(tab, text="TapaFrontal\t",
                       variable=self.chkbx_vars[17]).grid(row=22, column=0)
        
        # Other equipment
        other_equip_text = tk.Label(tab, text="Otro: ")
        other_equip_text.grid(row=20, column=1, padx=0, pady=0, sticky="e")

        self.other_equip_entry = tk.Entry(tab, width=10)
        self.other_equip_entry.grid(row=20, column=2, padx=0, pady=0)

        # Other data
        self.other_text = tk.Label(tab, text="Otros:")
        self.other_text.grid(row=20, column=0, padx=0, pady=0, sticky="ne")

        self.other_entry = tk.Entry(tab, width=20)
        self.other_entry.grid(row=20, column=1, padx=0, pady=0)
        
        # Turn label
        turn_text = tk.Label(tab, text="  Ficha:", font="Arial, 24")
        turn_text.grid(row=2, column=5, padx=0, pady=0, sticky="ne")

        self.turn_entry = tk.Entry(tab, width=3, font=("Arial", 24))
        self.turn_entry.grid(row=2, column=6, padx=0, pady=0)
        
        # Empty label
        empty3 = tk.Label(tab, text="")
        empty3.grid(row=5, column=5, padx=0, pady=0, sticky="e")

        # Products/Services
        product1_text = tk.Label(tab, text="Servicio", font="Arial, 18")
        product1_text.grid(row=14, column=6, columnspan=9, padx=0, pady=5)

        self.desc_text = tk.Label(tab, text="Descripción", font="Arial, 10")
        self.desc_text.grid(row=15, column=5, columnspan=9, padx=0, pady=5)

        quant_text = tk.Label(tab, text="Costo", font="Arial, 10")
        quant_text.grid(row=15, column=7, columnspan=9, padx=0, pady=5)

        # List of products/services        
        self.entry1 = tk.Entry(tab, width=18, font=("Arial", 9, "bold"))
        self.entry1.grid(row=17, column=6)
        self.entry2 = tk.Entry(tab, width=18, font=("Arial", 9, "bold"))
        self.entry2.grid(row=18, column=6)
        self.entry3 = tk.Entry(tab, width=18, font=("Arial", 9, "bold"))
        self.entry3.grid(row=19, column=6)
        self.entry4 = tk.Entry(tab, width=18, font=("Arial", 9, "bold"))
        self.entry4.grid(row=20, column=6)

        self.entries5 = tk.Entry(tab, width=7, font=("Arial", 9, "bold"))
        self.entries5.grid(row=17, column=7)
        self.entries6 = tk.Entry(tab, width=7, font=("Arial", 9, "bold"))
        self.entries6.grid(row=18, column=7)
        self.entries7 = tk.Entry(tab, width=7, font=("Arial", 9, "bold"))
        self.entries7.grid(row=19, column=7)
        self.entries8 = tk.Entry(tab, width=7, font=("Arial", 9, "bold"))
        self.entries8.grid(row=20, column=7)
        
        # Location checkbox
        Domicilio = ttk.Checkbutton(tab, text="Domicilio\t", 
                                   variable=self.Domicilio_var)
        Domicilio.grid(row=9, column=6)

        # Order number
        self.order_text = tk.Label(tab, text="No. orden: ", font="Arial, 18")
        self.order_text.grid(row=4, column=5)

        # ¡IMPORTANTE: Usa self.counter en lugar de counter global!
        self.counter_label = tk.Label(tab, text=str(self.counter), 
                                     font="Arial, 18")
        self.counter_label.grid(row=4, column=6)

        # Date
        date_text = tk.Label(tab, text="Fecha: ", font="Arial, 18")
        date_text.grid(row=5, column=5)

        self.date_entry = tk.Entry(tab, font="Arial, 18", width=13)
        self.date_entry.insert(0, self.date_format)  # ¡Usa self.date_format!
        self.date_entry.grid(row=5, column=6)

        # Save button
        save_btn = tk.Button(tab, text="Guardar", command=self.on_save_button)
        save_btn.grid(row=10, column=7)

        # Print button
        print_btn = tk.Button(tab, text="Imprimir", command=self.on_print_button)
        print_btn.grid(row=10, column=6)

        # New button
        new_btn = tk.Button(tab, text="Nueva ODT", command=self.on_new_button)
        new_btn.grid(row=10, column=5)

        # Empty label
        empty4 = tk.Label(tab, text="  ")
        empty4.grid(row=6, column=8, padx=0, pady=0, sticky="e")
        
    def _create_sales_tab(self):
        tab = self.tab_sales
        label = tk.Label(tab, text="Hoja de Ventas - En desarrollo", 
                        font="Arial, 20", fg="blue")
        label.pack(pady=100)
    
    def on_print_button(self):
        try:
            print("Iniciando proceso de impresión...")
            
            # 1. Verificar si hay datos guardados primero
            if not self._check_if_data_saved():
                response = self._ask_save_before_print()
                if response == "cancel":
                    return
                elif response == "save":
                    # Guardar primero
                    self.on_save_button()
                    # Pequeña pausa para que se guarde
                    self.notebook.update()
            
            # 2. Recoger datos actuales del formulario
            ticket_data = self._prepare_ticket_data()
            
            # 3. Generar el ticket
            config = TicketConfig()
            generator = TicketGenerator(config)
            ticket_content = generator.generate_ticket(ticket_data)
            
            # 4. Imprimir usando PrinterManager
            success = self.printer_mgr.print_ticket(ticket_content)
            
            if success:
                self._show_print_success()
            else:
                self._show_print_failed()
                
        except Exception as e:
            self._show_error(f"Error al imprimir:\n{str(e)}", "Error de impresión")
    
    def on_new_button(self):
        self._prepare_new_order()

    def _clear_all_fields(self):
        """Limpia TODOS los campos del formulario"""
        print("🧹 Limpiando TODOS los campos...")
        
        # Lista de todos los campos de texto/entry
        campos_texto = [
            self.name_entry,      # Nombre
            self.phone1_entry,    # Teléfono 1
            self.phone2_entry,    # Teléfono 2
            self.adress_entry,    # Dirección
            self.notes_entry,     # Diagnóstico
            self.equip_entry,     # Equipo
            self.serial_entry,    # No. Serie
            self.desc_entry,      # Descripción
            self.other_equip_entry,  # Otro equipo
            self.other_entry,     # Otro tipo
            self.turn_entry,      # Ficha
            self.entry1, self.entry2, self.entry3, self.entry4,  # Servicios
            self.entries5, self.entries6, self.entries7, self.entries8  # Costos
        ]
        
        # Limpiar cada campo de texto
        for campo in campos_texto:
            if campo and hasattr(campo, 'delete'):  # Verificar que exista y sea un Entry
                try:
                    campo.delete(0, tk.END)
                except:
                    pass  # Ignorar errores si el widget no existe aún
        
        # Limpiar TODOS los checkboxes (1-17)
        for i in range(1, 18):
            if i in self.chkbx_vars:
                try:
                    self.chkbx_vars[i].set("0")
                except:
                    pass
        
        # Limpiar domicilio
        try:
            self.Domicilio_var.set(0)
        except:
            pass
        
        print("✅ Todos los campos limpiados")
    
    def on_save_button(self):
        """Guarda los datos SIN incrementar automáticamente"""
        try:
            print(f"Guardando orden #{self.counter}...")
            
            # 1. Recoger datos
            order_data = self._collect_form_data()
            
            # 2. Validar
            if not self._validate_form_data(order_data):
                return
            
            # 3. Guardar con número ACTUAL
            saved_number = self.data_mgr.save_order_with_number(
                order_data, 
                self.counter  # Usar self.counter actual
            )
            
            # 4. Guardar checkboxes
            self._save_checkboxes_data(saved_number)
            
            # 5. Mostrar popup con opciones
            self._show_success_popup(saved_number)
            
            # IMPORTANTE: NO incrementar aquí
            # El usuario decidirá en el popup si quiere nueva orden
            
            print(f"Orden #{saved_number} guardada")
            print(f"Contador sigue en: #{self.counter} (esperando decisión del usuario)")
            
        except Exception as e:
            print(f"Error guardando: {e}")
            self._show_error(f"Error guardando datos:\n{str(e)}")

    def _check_if_data_saved(self) -> bool:
        if not self.name_entry.get().strip():
            return False
        return True

    def _ask_save_before_print(self):
        from tkinter import messagebox
        
        result = messagebox.askyesnocancel(
            "Guardar antes de imprimir",
            "Los datos no están guardados.\n\n"
            "¿Desea guardar antes de imprimir?\n\n"
            "• Sí: Guardar e imprimir\n"
            "• No: Imprimir sin guardar\n"
            "• Cancelar: Volver al formulario",
            parent=self.notebook
        )
        if result is None:  # Cancelar
            return "cancel"
        elif result:  # Sí
            return "save"
        else:  # No
            return "print"

    def _prepare_ticket_data(self) -> Dict:
        numero_ticket = self.counter
        print(f"Preparando ticket #{numero_ticket}")

        # Datos básicos del formulario
        data = {
            "no_orden": str(self.counter),  # Usar el contador actual
            "ficha": self.turn_entry.get().strip() or "0",
            "fecha": self.date_entry.get().strip(),
            "cliente": self.name_entry.get().strip(),
            "equipo": self.equip_entry.get().strip(),
            "no_serie": self.serial_entry.get().strip(),
            "diagnostico": self.notes_entry.get().strip(),
            "tel1": self.phone1_entry.get().strip(),
            "tel2": self.phone2_entry.get().strip(),
            "direccion": self.adress_entry.get().strip(),
            "taller_domi": "Domicilio" if self.Domicilio_var.get() == 1 else "Taller",
            "descripcion": self.desc_entry.get().strip()
        }
        
        # Estado del equipo (checkboxes 1-11, 16-17)
        piezas_mapping = {
            1: "aguja", 2: "bobina", 3: "carretel", 4: "devanador",
            5: "estuche", 6: "foco", 7: "motor", 8: "banda",
            9: "pedal", 10: "pie", 11: "hilo", 16: "abierta", 
            17: "tapa"
        }
        
        for idx, nombre in piezas_mapping.items():
            data[nombre] = self.chkbx_vars[idx].get() == "1"
        
        # Otro pieza
        otro_pieza = self.other_equip_entry.get().strip()
        data["otro_piezas"] = otro_pieza if otro_pieza else ""
        
        # Tipo de equipo (checkboxes 12-15)
        tipo_mapping = {
            12: "casero", 13: "industrial", 14: "costura", 15: "sobrehiladora"
        }
        
        for idx, nombre in tipo_mapping.items():
            data[nombre] = self.chkbx_vars[idx].get() == "1"
        
        # Otro tipo
        otro_tipo = self.other_entry.get().strip()
        data["otro_tipo"] = otro_tipo if otro_tipo else ""
        
        # Servicios
        servicios_data = [
            (self.entry1.get().strip(), self.entries5.get().strip()),
            (self.entry2.get().strip(), self.entries6.get().strip()),
            (self.entry3.get().strip(), self.entries7.get().strip()),
            (self.entry4.get().strip(), self.entries8.get().strip())
        ]
        
        # Agregar servicios al diccionario
        for i, (servicio, costo) in enumerate(servicios_data, 1):
            if servicio:  # Solo agregar si hay servicio
                data[f"servicio{i}"] = servicio
                data[f"costo{i}"] = costo
        
        print(f"Datos preparados para ticket #{data['no_orden']}")
        return data

    def _show_print_success(self):
        """Muestra mensaje de éxito de impresión"""
        popup = tk.Toplevel(self.notebook)
        popup.title("Impresión exitosa")
        popup.geometry("350x120")
        
        # Centrar
        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f'{width}x{height}+{x}+{y}')
        
        # Contenido
        tk.Label(popup, text="✅ Ticket enviado a impresión", 
                font=("Arial", 12, "bold"), fg="green", pady=20).pack()
        
        tk.Label(popup, text="El ticket se está imprimiendo...", 
                font=("Arial", 10)).pack()
        
        # Auto-cerrar después de 3 segundos
        popup.after(3000, popup.destroy)
    
    def _show_print_failed(self):
        """Muestra que la impresión falló"""
        from tkinter import messagebox
        messagebox.showwarning(
            "Impresión fallida",
            "No se pudo imprimir automáticamente.\n\n"
            "Se abrirá una ventana con instrucciones\n"
            "para imprimir manualmente.",
            parent=self.notebook
        )

    def _collect_form_data(self) -> Dict:
        """Recopila todos los datos del formulario"""
        # Datos básicos
        data = {
            'nombre': self.name_entry.get().strip(),
            'tel1': self.phone1_entry.get().strip(),
            'tel2': self.phone2_entry.get().strip(),
            'direccion': self.adress_entry.get().strip(),
            'equipo': self.equip_entry.get().strip(),
            'serie': self.serial_entry.get().strip(),
            'turno': self.turn_entry.get().strip(),
            'fecha': self.date_entry.get().strip(),
            'diagnostico': self.notes_entry.get().strip(),
            'descripcion': self.desc_entry.get().strip(),
            'taller_domi': "Domicilio" if self.Domicilio_var.get() == 1 else "Taller"
        }
        
        # Servicios
        servicios = []
        servicios.append((self.entry1.get().strip(), self.entries5.get().strip()))
        servicios.append((self.entry2.get().strip(), self.entries6.get().strip()))
        servicios.append((self.entry3.get().strip(), self.entries7.get().strip()))
        servicios.append((self.entry4.get().strip(), self.entries8.get().strip()))
        data['servicios'] = servicios
        
        # Otros campos
        data['otro_equipo'] = self.other_equip_entry.get().strip()
        data['otro_tipo'] = self.other_entry.get().strip()
        
        return data
    
    def _validate_form_data(self, data: Dict) -> bool:
        """Valida que los datos mínimos estén completos"""
        errors = []
        
        if not data['nombre']:
            errors.append("El nombre del cliente es obligatorio")
        
        if not data['tel1']:
            errors.append("El teléfono es obligatorio")
        
        if not data['equipo']:
            errors.append("El equipo es obligatorio")
        
        if not data['diagnostico']:
            errors.append("El diagnóstico es obligatorio")
        
        if errors:
            error_msg = "Por favor complete:\n" + "\n".join(f"• {e}" for e in errors)
            self._show_error(error_msg, "Campos incompletos")
            return False
        
        return True
    
    def _save_checkboxes_data(self, order_number: int):
        """Guarda el estado de los checkboxes"""
        # Estado del equipo (piezas faltantes)
        piezas_faltantes = []
        for i in range(1, 18):
            if self.chkbx_vars[i].get() == "1":
                # Mapear número a nombre de pieza
                pieza_nombre = self._get_pieza_name(i)
                if pieza_nombre:
                    piezas_faltantes.append(pieza_nombre)
        
        # Tipo de equipo
        tipos_equipo = []
        tipo_mapping = {
            12: "Casero",
            13: "Industrial", 
            14: "Costura",
            15: "Sobrehiladora"
        }
        for tipo_num, tipo_nombre in tipo_mapping.items():
            if self.chkbx_vars[tipo_num].get() == "1":
                tipos_equipo.append(tipo_nombre)
        
        # Guardar usando DataManager
        self.data_mgr.save_checkboxes(order_number, piezas_faltantes, tipos_equipo)
    
    def _get_pieza_name(self, index: int) -> str:
        """Convierte índice de checkbox a nombre de pieza"""
        piezas = {
            1: "Aguja", 2: "Bobina", 3: "Carretel", 4: "Devanador",
            5: "Estuche/bolsa", 6: "Foco", 7: "Motor", 8: "Banda",
            9: "Pedal", 10: "Pie", 11: "Hilo", 16: "Abierta", 
            17: "TapaFrontal"
        }
        return piezas.get(index, "")
    
    def _update_ui_after_save(self, order_number: int):
        """Actualiza la interfaz después de guardar"""
        # Incrementar contador
        self.counter = order_number + 1
        self.counter_label.config(text=str(self.counter))
        
        # Opcional: Limpiar algunos campos
        self.turn_entry.delete(0, tk.END)
        
        # Actualizar fecha automáticamente
        today_date = datetime.date.today()
        self.date_format = today_date.strftime("%d - %m - %Y")
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, self.date_format)
    
    def _show_success_popup(self, order_number: int):
        """Muestra popup de éxito"""
        popup = tk.Toplevel(self.notebook)
        popup.title(f"Orden #{order_number} guardada")
        popup.geometry("400x150")
        
        # Centrar
        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f'{width}x{height}+{x}+{y}')
        
        # Contenido
        tk.Label(popup, text=f"✅ Orden #{order_number} guardada exitosamente", 
            font=("Arial", 12, "bold"), fg="green", pady=20).pack()
    
        tk.Label(popup, text=f"Próxima orden será: #{self.counter}", 
            font=("Arial", 10)).pack()
    
        tk.Label(popup, text="¿Qué deseas hacer ahora?", 
            font=("Arial", 10)).pack(pady=10)
        
        # Botones
        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Continuar Editando", 
                  command=lambda: [self._clear_after_save(), popup.destroy()]).pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Nueva Orden", 
              command=lambda: [self._prepare_new_order(), popup.destroy()]).pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Imprimir", 
                  command=lambda: [self.on_print_button(), popup.destroy()]).pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Cerrar", 
              command=popup.destroy).pack(side="left", padx=5)
        
        popup.after(5000, popup.destroy)
        
    def _show_error(self, message: str, title="Error"):
        from tkinter import messagebox
        messagebox.showerror(title, message, parent=self.notebook)

    def _clear_after_save(self):
        print("🧹 Limpiando algunos campos después de guardar...")
        
        # Limpiar solo estos campos (no todo)
        campos_a_limpiar = [
            self.turn_entry,      # Ficha
            self.entry1, self.entry2, self.entry3, self.entry4,  # Servicios
            self.entries5, self.entries6, self.entries7, self.entries8  # Costos
        ]
        
        for campo in campos_a_limpiar:
            if campo and hasattr(campo,'delete'):
                try:
                    campo.delete(0, tk.END)
                except:
                    pass
        
        checkboxes_a_limpiar = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 16, 17]
        for i in checkboxes_a_limpiar:
            if i in self.chkbx_vars:
                try:
                    self.chkbx_vars[i].set("0")
                except:
                    pass
        # Enfocar en nombre para siguiente cliente
        try:
            self.name_entry.focus_set()
        except:
            pass
        
        print(f"Campos limpiados, listo para nuevo cliente en orden #{self.counter}")

    def _prepare_new_order(self):
        """Prepara una NUEVA orden completa (incrementa y limpia todo)"""
        print("Preparando NUEVA orden completa...")
        
        # 1. INCREMENTAR contador
        old_counter = self.counter
        self.counter += 1
        print(f"Contador incrementado: #{old_counter} → #{self.counter}")
        
        # 2. Actualizar en pantalla y guardar nuevo counter en archivo
        self.data_mgr.save_counter(self.counter)
        print(f"Valor del contador guardado en archivo: #{self.counter}")
        
        if hasattr(self, 'counter_label') and self.counter_label:
            self.counter_label.config(text=str(self.counter))
        
        # 3. Limpiar TODOS los campos
        self._clear_all_fields()
        
        # 4. Actualizar fecha automáticamente
        try:
            today_date = datetime.date.today()
            self.date_format = today_date.strftime("%d - %m - %Y")
            if self.date_entry and hasattr(self.date_entry, 'delete'):
                self.date_entry.delete(0, tk.END)
                self.date_entry.insert(0, self.date_format)
        except:
            pass
        
        # 5. Enfocar primer campo
        try:
            self.name_entry.focus_set()
        except:
            pass
        
        print(f"Nueva orden #{self.counter} lista")

class main_menu:
    def __init__ (self, x_place= 50, y_place = 40):

        self.x_place = x_place
        self.y_place = y_place
    
    def format(self):
        #Title:
        window.title("SERVINORTE")

        #geometry window
        window.geometry('1000x700')
        
        window.geometry('+{}+{}'.format(self.x_place, self.y_place))
         
#-----------------MAIN---------------------
class ServinorteApp:
    
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Servinorte - Sistema de Tickets")
        
        # Inicializar componentes
        app_dir = os.getcwd()
        self.data_manager = DataManager(app_dir)
        self.printer_manager = PrinterManager(self.window)
        
        # Crear notebook para tabs
        self.notebook = ttk.Notebook(self.window)
        
        # Crear interfaz
        self.ui_tabs = UITabs(self.notebook, self.data_manager, self.printer_manager)
        
        # Configurar ventana
        self._setup_window()
    
    def _setup_window(self):
        """Configura la ventana principal"""
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tamaño mínimo
        self.window.minsize(800, 600)
        
        # Centrar ventana
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def run(self):
        """Ejecuta la aplicación"""
        self.window.mainloop()

#------------------------------------------
#--------------Start program---------------
#------------------------------------------
if __name__ == "__main__":
    # Variables globales (ahora manejadas por las clases)
    today_date = datetime.date.today()
    date_format = today_date.strftime("%d - %m - %Y")
    
    # Crear y ejecutar aplicación
    app = ServinorteApp()
    app.run()