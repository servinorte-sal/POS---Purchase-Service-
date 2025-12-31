#Edgar F. Glz. A. 2025 - SERVINORTE
#sevinortesaclientes@gmail.com
#Py 3.14

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

    #------PESTAÑA REGISTROS---------------
    def load_all_orders(self) -> List[Dict]:
        """Carga todas las órdenes del archivo CSV"""
        orders = []
        
        try:
            if not os.path.exists(self.orders_file):
                print(f"⚠️ Archivo {self.orders_file} no existe")
                return orders
            
            with open(self.orders_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                
                # Saltar encabezado si existe
                try:
                    headers = next(reader)
                except StopIteration:
                    return orders
                
                for row in reader:
                    if len(row) >= 12:  # Verificar que tenga todos los campos
                        order = {
                            'no_orden': row[0].strip(),
                            'turno': row[1].strip(),
                            'fecha': row[2].strip(),
                            'nombre': row[3].strip(),
                            'equipo': row[4].strip(),
                            'no_serie': row[5].strip(),
                            'diagnostico': row[6].strip(),
                            'tel1': row[7].strip(),
                            'tel2': row[8].strip(),
                            'direccion': row[9].strip(),
                            'taller_domi': row[10].strip(),
                            'descripcion': row[11].strip()
                        }
                        orders.append(order)
            
            print(f"📊 {len(orders)} órdenes cargadas del archivo")
            return orders
            
        except Exception as e:
            print(f"❌ Error cargando órdenes: {e}")
            return []
    
    def load_order_details(self, order_number: int) -> Dict:
        """Carga todos los detalles de una orden específica"""
        try:
            orders = self.load_all_orders()
            
            for order in orders:
                if str(order.get('no_orden', '')) == str(order_number):
                    # Cargar datos adicionales si existen
                    
                    # Cargar estado del equipo
                    estado_file = os.path.join(self.app_dir, "Estado de equipos.csv")
                    if os.path.exists(estado_file):
                        with open(estado_file, 'r', encoding='utf-8') as f:
                            reader = csv.reader(f, delimiter=';')
                            for row in reader:
                                if len(row) >= 2 and row[0].strip() == str(order_number):
                                    order['estado_equipo'] = row[1].strip()
                    
                    # Cargar tipo de equipo
                    tipo_file = os.path.join(self.app_dir, "Tipos de equipos.csv")
                    if os.path.exists(tipo_file):
                        with open(tipo_file, 'r', encoding='utf-8') as f:
                            reader = csv.reader(f, delimiter=';')
                            for row in reader:
                                if len(row) >= 2 and row[0].strip() == str(order_number):
                                    order['tipo_equipo'] = row[1].strip()
                    
                    return order
            
            return {}
            
        except Exception as e:
            print(f"❌ Error cargando detalles orden #{order_number}: {e}")
            return {}
    
    def load_services(self, order_number: int) -> List[Dict]:
        """Carga los servicios de una orden"""
        services = []
        services_file = os.path.join(self.app_dir, "Servicios.csv")
        
        try:
            if os.path.exists(services_file):
                with open(services_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter=';')
                    
                    try:
                        headers = next(reader)  # Saltar encabezado
                    except StopIteration:
                        return services
                    
                    for row in reader:
                        if len(row) >= 3 and row[0].strip() == str(order_number):
                            service = {
                                'servicio': row[1].strip(),
                                'costo': row[2].strip()
                            }
                            services.append(service)
            
            return services
            
        except Exception as e:
            print(f"❌ Error cargando servicios orden #{order_number}: {e}")
            return []
    
    def search_orders(self, search_type: str, search_term: str) -> List[Dict]:
        """Busca órdenes según criterio"""
        all_orders = self.load_all_orders()
        results = []
        
        search_term = search_term.lower()
        
        for order in all_orders:
            match = False
            
            if search_type == "no_orden":
                match = search_term in str(order.get('no_orden', '')).lower()
            elif search_type == "nombre":
                match = search_term in order.get('nombre', '').lower()
            elif search_type == "telefono":
                match = (search_term in order.get('tel1', '').lower() or 
                        search_term in order.get('tel2', '').lower())
            elif search_type == "equipo":
                match = search_term in order.get('equipo', '').lower()
            elif search_type == "serie":
                match = search_term in order.get('no_serie', '').lower()
            elif search_type == "diagnostico":
                match = search_term in order.get('diagnostico', '').lower()
            
            if match:
                results.append(order)
        
        return results    

    def load_equipment_state(self, order_number: int) -> str:
        """Carga el estado del equipo para una orden"""
        try:
            if not os.path.exists(self.equipment_file):
                return ""
            
            with open(self.equipment_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                
                try:
                    next(reader)  # Saltar encabezado
                except StopIteration:
                    return ""
                
                for row in reader:
                    if len(row) >= 2 and row[0].strip() == str(order_number):
                        return row[1].strip()
            
            return ""
            
        except Exception as e:
            print(f"❌ Error cargando estado orden #{order_number}: {e}")
            return ""
    
    def load_equipment_type(self, order_number: int) -> str:
        """Carga el tipo de equipo para una orden"""
        try:
            if not os.path.exists(self.types_file):
                return ""
            
            with open(self.types_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                
                try:
                    next(reader)  # Saltar encabezado
                except StopIteration:
                    return ""
                
                for row in reader:
                    if len(row) >= 2 and row[0].strip() == str(order_number):
                        return row[1].strip()
            
            return ""
            
        except Exception as e:
            print(f"❌ Error cargando tipo orden #{order_number}: {e}")
            return ""

# ---------------UI TABS-------------------
class UITabs:
    #-------------SETUP--------------------
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
        self.tab_registro = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_work_order, text="Orden de trabajo")
        self.notebook.add(self.tab_sales, text="Hoja de Ventas")
        self.notebook.add(self.tab_registro, text="Registros")
        
        self._create_work_order_tab()
        self._create_sales_tab()
        self._create_registro_tab()

    #-----------WORK ORDER------------------
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
        popup.geometry("400x200")
        
        # Centrar
        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f'{width}x{height}+{x}+{y}')
        
        # Contenido
        tk.Label(popup, text=f"Orden #{order_number} guardada exitosamente", 
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
        print("Limpiando algunos campos después de guardar...")
        
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

    # ------PESTAÑA DE VENTAS--------------
    def _create_sales_tab(self):
        tab = self.tab_sales
        label = tk.Label(tab, text="Hoja de Ventas - En desarrollo", 
                        font="Arial, 20", fg="blue")
        label.pack(pady=100)
    
    # -----PESTAÑA DE REGISTROS------------
    def _create_registro_tab(self):
        """Crea la pestaña de registro/búsqueda de órdenes"""
        tab = self.tab_registro
        
        # Configurar grid
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        # --- MARCO SUPERIOR: BÚSQUEDA ---
        search_frame = ttk.LabelFrame(tab, text="🔍 Búsqueda Avanzada", padding=10)
        search_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        # Fila 1: Tipo de búsqueda y término
        ttk.Label(search_frame, text="Buscar por:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.search_type = tk.StringVar(value="no_orden")
        search_options = ttk.Combobox(search_frame, textvariable=self.search_type, 
                                     state="readonly", width=20)
        search_options['values'] = (
            "No. Orden", 
            "Nombre del cliente", 
            "Teléfono", 
            "Equipo",
            "No. Serie", 
            "Fecha",
            "Diagnóstico"
        )
        search_options.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Término:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        
        self.search_term = tk.Entry(search_frame, width=30)
        self.search_term.grid(row=0, column=3, padx=5, pady=5)
        self.search_term.bind('<Return>', lambda e: self._search_orders())  # Buscar con Enter
        
        # Botones de búsqueda
        search_btn = ttk.Button(search_frame, text="🔍 Buscar", 
                               command=self._search_orders)
        search_btn.grid(row=0, column=4, padx=5, pady=5)
        
        clear_btn = ttk.Button(search_frame, text="🗑️ Limpiar", 
                              command=self._clear_search)
        clear_btn.grid(row=0, column=5, padx=5, pady=5)
        
        # Fila 2: Filtros adicionales
        filter_frame = ttk.Frame(search_frame)
        filter_frame.grid(row=1, column=0, columnspan=6, pady=10, sticky="w")
        
        ttk.Label(filter_frame, text="Mostrar:").pack(side="left", padx=5)
        
        self.show_all_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(filter_frame, text="Todas", 
                       variable=self.show_all_var).pack(side="left", padx=5)
        
        ttk.Label(filter_frame, text="Ordenar por:").pack(side="left", padx=(20, 5))
        
        self.sort_by = tk.StringVar(value="no_orden_desc")
        sort_options = ttk.Combobox(filter_frame, textvariable=self.sort_by, 
                                   state="readonly", width=15)
        sort_options['values'] = (
            "No. Orden ↑", 
            "No. Orden ↓", 
            "Fecha ↑", 
            "Fecha ↓",
            "Nombre A-Z", 
            "Nombre Z-A"
        )
        sort_options.pack(side="left", padx=5)
        
        # --- MARCO IZQUIERDO: LISTA DE RESULTADOS ---
        list_frame = ttk.LabelFrame(tab, text="📋 Resultados de Búsqueda", padding=5)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=(0, 10))
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        # Treeview para mostrar resultados
        columns = ('no_orden', 'fecha', 'nombre', 'telefono', 'equipo', 'no_serie', 'diagnostico')
        self.results_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        self.results_tree.heading('no_orden', text='No. Orden')
        self.results_tree.heading('fecha', text='Fecha')
        self.results_tree.heading('nombre', text='Nombre')
        self.results_tree.heading('telefono', text='Teléfono')
        self.results_tree.heading('equipo', text='Equipo')
        self.results_tree.heading('no_serie', text='No. Serie')
        self.results_tree.heading('diagnostico', text='Diagnóstico')
        
        # Ancho de columnas
        self.results_tree.column('no_orden', width=80, anchor='center')
        self.results_tree.column('fecha', width=100)
        self.results_tree.column('nombre', width=150)
        self.results_tree.column('telefono', width=100)
        self.results_tree.column('equipo', width=120)
        self.results_tree.column('no_serie', width=100)
        self.results_tree.column('diagnostico', width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", 
                                 command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar
        self.results_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Evento al seleccionar
        self.results_tree.bind('<<TreeviewSelect>>', self._on_order_selected)
        
        # Botones debajo de la lista
        btn_frame = ttk.Frame(list_frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=5)
        
        ttk.Button(btn_frame, text="📄 Ver Detalles", 
                  command=self._show_order_details_by_number).pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="🖨️ Imprimir Ticket", 
                  command=self._print_selected_order).pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="📋 Copiar Info", 
                  command=self._copy_order_info).pack(side="left", padx=5)
        
        # --- MARCO DERECHO: DETALLES DE LA ORDEN ---
        detail_frame = ttk.LabelFrame(tab, text="📄 Detalles de la Orden", padding=10)
        detail_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=(0, 10))
        detail_frame.grid_columnconfigure(0, weight=1)
        
        # Canvas con scroll para detalles
        self.detail_canvas = tk.Canvas(detail_frame, width=400)
        scrollbar_detail = ttk.Scrollbar(detail_frame, orient="vertical", 
                                        command=self.detail_canvas.yview)
        self.detail_scrollable_frame = ttk.Frame(self.detail_canvas)
        
        self.detail_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.detail_canvas.configure(
                scrollregion=self.detail_canvas.bbox("all")
            )
        )
        
        self.detail_canvas.create_window((0, 0), window=self.detail_scrollable_frame, anchor="nw")
        self.detail_canvas.configure(yscrollcommand=scrollbar_detail.set)
        
        # Empaquetar canvas
        self.detail_canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar_detail.grid(row=0, column=1, sticky="ns")
        
        # Inicializar detalles vacíos
        

        self._init_order_details()
        
        # Cargar todas las órdenes al inicio
        self._load_all_orders()

    def _init_order_details(self):
        """Inicializa los widgets de detalles de orden"""
        frame = self.detail_scrollable_frame
        
        # Etiqueta inicial
        self.detail_label = ttk.Label(frame, text="Seleccione una orden para ver los detalles", 
                                     font=("Arial", 10, "italic"), foreground="gray")
        self.detail_label.pack(pady=20)
        
        # Frame para los detalles (oculto inicialmente)
        self.detail_content = ttk.Frame(frame)
        # Se mostrará cuando haya una orden seleccionada
    
    def _load_all_orders(self):
        """Carga todas las órdenes al iniciar la pestaña"""
        try:
            orders = self.data_mgr.load_all_orders()
            self._display_results(orders)
            print(f"✅ Cargadas {len(orders)} órdenes en el registro")
        except Exception as e:
            print(f"❌ Error cargando órdenes: {e}")
            self._show_error_in_tab(f"Error cargando registros:\n{str(e)}")
    
    def _search_orders(self):
        """Realiza búsqueda según criterios seleccionados"""
        search_type = self.search_type.get()
        search_term = self.search_term.get().strip().lower()
        
        if not search_term:
            # Si no hay término, cargar todas
            self._load_all_orders()
            return
        
        try:
            # Cargar todas las órdenes
            all_orders = self.data_mgr.load_all_orders()
            
            # Filtrar según tipo de búsqueda
            filtered_orders = []
            
            for order in all_orders:
                match = False
                
                if search_type == "No. Orden":
                    match = search_term in str(order.get('no_orden', ''))
                elif search_type == "Nombre del cliente":
                    match = search_term in order.get('nombre', '').lower()
                elif search_type == "Teléfono":
                    match = (search_term in order.get('tel1', '').lower() or 
                            search_term in order.get('tel2', '').lower())
                elif search_type == "Equipo":
                    match = search_term in order.get('equipo', '').lower()
                elif search_type == "No. Serie":
                    match = search_term in order.get('no_serie', '').lower()
                elif search_type == "Fecha":
                    match = search_term in order.get('fecha', '').lower()
                elif search_type == "Diagnóstico":
                    match = search_term in order.get('diagnostico', '').lower()
                
                if match:
                    filtered_orders.append(order)
            
            # Mostrar resultados
            self._display_results(filtered_orders)
            
            # Mostrar mensaje
            if filtered_orders:
                self._update_status(f"✅ Encontradas {len(filtered_orders)} órdenes")
            else:
                self._update_status("❌ No se encontraron órdenes")
                
        except Exception as e:
            print(f"❌ Error en búsqueda: {e}")
            self._show_error_in_tab(f"Error en búsqueda:\n{str(e)}")
    
    def _display_results(self, orders):
        """Muestra órdenes en el Treeview"""
        # Limpiar treeview
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Ordenar si es necesario
        if self.sort_by.get() == "No. Orden ↑":
            orders.sort(key=lambda x: int(x.get('no_orden', 0)))
        elif self.sort_by.get() == "No. Orden ↓":
            orders.sort(key=lambda x: int(x.get('no_orden', 0)), reverse=True)
        elif self.sort_by.get() == "Fecha ↑":
            orders.sort(key=lambda x: x.get('fecha', ''))
        elif self.sort_by.get() == "Fecha ↓":
            orders.sort(key=lambda x: x.get('fecha', ''), reverse=True)
        elif self.sort_by.get() == "Nombre A-Z":
            orders.sort(key=lambda x: x.get('nombre', '').lower())
        elif self.sort_by.get() == "Nombre Z-A":
            orders.sort(key=lambda x: x.get('nombre', '').lower(), reverse=True)
        
        # Insertar en treeview
        for order in orders:
            self.results_tree.insert('', 'end', values=(
                order.get('no_orden', ''),
                order.get('fecha', ''),
                order.get('nombre', '')[:30],  # Limitar longitud
                order.get('tel1', ''),
                order.get('equipo', '')[:20],
                order.get('no_serie', '')[:15],
                order.get('diagnostico', '')[:30]
            ))
    
    def _on_order_selected(self, event):
        """Cuando se selecciona una orden en la lista"""
        selection = self.results_tree.selection()
        if selection:
            item = self.results_tree.item(selection[0])
            order_number = item['values'][0]
            self._show_order_details_by_number(order_number)
    
    def _show_order_details_by_number(self, order_number):
        """Muestra los detalles de una orden específica"""
        try:
            # Cargar datos completos de la orden
            order_data = self.data_mgr.load_order_details(order_number)
            
            if not order_data:
                self._show_error_in_tab(f"Orden #{order_number} no encontrada")
                return
            
            # Ocultar label inicial y mostrar detalles
            self.detail_label.pack_forget()
            
            # Destruir contenido anterior si existe
            if hasattr(self, 'detail_content'):
                self.detail_content.destroy()
            
            # Crear nuevo frame de detalles
            self.detail_content = ttk.Frame(self.detail_scrollable_frame)
            self.detail_content.pack(fill="both", expand=True)
            
            # Título
            title = ttk.Label(self.detail_content, 
                            text=f"📄 Orden #{order_number}",
                            font=("Arial", 14, "bold"))
            title.pack(pady=(0, 15))
            
            # Marco de información general
            info_frame = ttk.LabelFrame(self.detail_content, text="Información General", padding=10)
            info_frame.pack(fill="x", padx=5, pady=5)
            
            # Crear etiquetas de información
            fields = [
                ("📅 Fecha:", order_data.get('fecha', '')),
                ("👤 Cliente:", order_data.get('nombre', '')),
                ("📞 Teléfono 1:", order_data.get('tel1', '')),
                ("📞 Teléfono 2:", order_data.get('tel2', '')),
                ("📍 Dirección:", order_data.get('direccion', '')),
                ("🏠 Taller/Domicilio:", order_data.get('taller_domi', ''))
            ]
            
            for label, value in fields:
                frame = ttk.Frame(info_frame)
                frame.pack(fill="x", pady=2)
                ttk.Label(frame, text=label, width=15, anchor="w").pack(side="left")
                ttk.Label(frame, text=value, anchor="w").pack(side="left", padx=5)
            
            # Marco de equipo
            equip_frame = ttk.LabelFrame(self.detail_content, text="Datos del Equipo", padding=10)
            equip_frame.pack(fill="x", padx=5, pady=5)
            
            equip_fields = [
                ("🔧 Equipo:", order_data.get('equipo', '')),
                ("🔢 No. Serie:", order_data.get('no_serie', '')),
                ("📝 Descripción:", order_data.get('descripcion', '')),
                ("💡 Diagnóstico:", order_data.get('diagnostico', ''))
            ]
            
            for label, value in equip_fields:
                frame = ttk.Frame(equip_frame)
                frame.pack(fill="x", pady=2)
                ttk.Label(frame, text=label, width=15, anchor="w").pack(side="left")
                # Text widget para diagnósticos largos
                if label == "💡 Diagnóstico:" and len(value) > 50:
                    text_widget = tk.Text(frame, height=3, width=30, wrap="word")
                    text_widget.insert("1.0", value)
                    text_widget.config(state="disabled")
                    text_widget.pack(side="left", padx=5)
                else:
                    ttk.Label(frame, text=value, anchor="w").pack(side="left", padx=5)
            
            # Cargar servicios si existen
            servicios = self.data_mgr.load_services(order_number)
            if servicios:
                services_frame = ttk.LabelFrame(self.detail_content, text="Servicios", padding=10)
                services_frame.pack(fill="x", padx=5, pady=5)
                
                for servicio in servicios:
                    frame = ttk.Frame(services_frame)
                    frame.pack(fill="x", pady=2)
                    ttk.Label(frame, text="•", width=2).pack(side="left")
                    ttk.Label(frame, text=servicio.get('servicio', ''), 
                             anchor="w").pack(side="left", padx=5)
                    ttk.Label(frame, text=f"${servicio.get('costo', '0')}", 
                             anchor="e").pack(side="right")
            
            # Botones de acción
            btn_frame = ttk.Frame(self.detail_content)
            btn_frame.pack(pady=15)
            
            ttk.Button(btn_frame, text="🖨️ Imprimir Ticket",
                      command=lambda num=order_number: self._print_order_ticket_by_number(num)).pack(side="left", padx=5)
            
            ttk.Button(btn_frame, text="📋 Copiar al Portapapeles",
                      command=lambda num=order_number: self._copy_order_to_clipboard_by_number(num)).pack(side="left", padx=5)
            
            ttk.Button(btn_frame, text="✏️ Editar",
                      command=lambda num=order_number: self._edit_order(num)).pack(side="left", padx=5)
            
        except Exception as e:
            print(f"❌ Error mostrando detalles: {e}")
            self._show_error_in_tab(f"Error cargando detalles:\n{str(e)}")

    # ---------CLIPBOARD REGISTRO ---------
    
    def _print_order_ticket_by_number(self, order_number: int):
        """Imprime ticket de una orden por su número"""
        try:
            print(f"🖨️ Imprimiendo ticket para orden #{order_number}")
            
            # Cargar datos completos
            order_data = self.data_mgr.load_order_details(order_number)
            
            if not order_data:
                self._show_error_in_tab(f"Orden #{order_number} no encontrada")
                return
            
            # Llamar al método de impresión
            self._print_order_ticket(order_data)
            
        except Exception as e:
            self._show_error_in_tab(f"Error imprimiendo orden #{order_number}:\n{str(e)}")
    
    def _copy_order_to_clipboard_by_number(self, order_number: int):
        """Copia orden al portapapeles por su número"""
        try:
            print(f"📋 Copiando orden #{order_number} al portapapeles")
            
            # Cargar datos completos
            order_data = self.data_mgr.load_order_details(order_number)
            
            if not order_data:
                self._show_error_in_tab(f"Orden #{order_number} no encontrada")
                return
            
            # Llamar al método de copiado
            self._copy_order_to_clipboard(order_data)
            
        except Exception as e:
            self._show_error_in_tab(f"Error copiando orden #{order_number}:\n{str(e)}")
    
    def _print_order_ticket(self, order_data: Dict):
        """Genera e imprime el ticket de una orden específica"""
        try:
            order_number = order_data.get('no_orden', 'N/A')
            print(f"🖨️ Preparando ticket para orden #{order_number}")
            
            # Validar que tenemos datos mínimos
            required_fields = ['no_orden', 'fecha', 'cliente', 'equipo', 'diagnostico']
            missing_fields = [field for field in required_fields if not order_data.get(field)]
            
            if missing_fields:
                self._show_error_in_tab(
                    f"No se puede generar ticket. Faltan campos:\n"
                    f"{', '.join(missing_fields)}"
                )
                return
            
            # Preparar datos completos para el ticket
            ticket_data = self._prepare_ticket_data_from_order(order_data)
            
            # Generar el ticket
            config = TicketConfig()
            generator = TicketGenerator(config)
            ticket_content = generator.generate_ticket(ticket_data)
            
            print(f"✅ Ticket generado ({len(ticket_content)} bytes)")
            
            # Imprimir usando PrinterManager
            success = self.printer_mgr.print_ticket(ticket_content)
            
            if success:
                self._show_success_in_tab(
                    f"✅ Ticket de orden #{order_number} enviado a impresión"
                )
            else:
                self._show_warning_in_tab(
                    "⚠️ No se pudo imprimir automáticamente.\n"
                    "Se mostrarán instrucciones para impresión manual."
                )
                
        except Exception as e:
            print(f"❌ Error imprimiendo ticket: {e}")
            self._show_error_in_tab(f"Error al imprimir ticket:\n{str(e)}")
    
    def _copy_order_to_clipboard(self, order_data: Dict):
        """Copia toda la información de la orden al portapapeles"""
        
        try:
            order_number = order_data.get('no_orden', 'N/A')
            print(f"📋 Copiando orden #{order_number} al portapapeles")
            
            # Formatear la información de manera legible
            clipboard_text = self._format_order_for_clipboard(order_data)
            
            # Método CORRECTO para copiar al portapapeles en tkinter
            # Necesitamos acceder a la ventana raíz (self.window)
            root_window = self._get_root_window()
            
            if root_window:
                # Limpiar portapapeles
                root_window.clipboard_clear()
                # Agregar texto
                root_window.clipboard_append(clipboard_text)
                
                # Opcional: mantener en portapapeles después de cerrar
                root_window.clipboard_append(clipboard_text)  # Esto es redundante, pero asegura
                
                print(f"✅ Texto copiado ({len(clipboard_text)} caracteres)")
            else:
                # Fallback: usar tkinter básico
                import tkinter as tk
                tk_root = tk.Tk()
                tk_root.withdraw()  # Ocultar ventana
                tk_root.clipboard_clear()
                tk_root.clipboard_append(clipboard_text)
                tk_root.update()  # Ahora se guarda en el portapapeles
                tk_root.destroy()
                print("✅ Texto copiado (usando fallback)")
            
            # Mostrar confirmación
            self._show_success_in_tab(
                f"✅ Orden #{order_number} copiada al portapapeles\n"
                "Puedes pegarla en cualquier aplicación con Ctrl+V"
            )
            
        except Exception as e:
            print(f"❌ Error copiando al portapapeles: {e}")
            import traceback
            print(f"🔍 Traceback: {traceback.format_exc()}")
            self._show_error_in_tab(f"Error al copiar:\n{str(e)}")

    def _format_order_for_clipboard(self, order_data: Dict) -> str:
        """Formatea la información de la orden para el portapapeles"""
        order_number = order_data.get('no_orden', 'N/A')
        
        # Encabezado
        text = f"🚀 SERVINORTE - ORDEN DE SERVICIO #{order_number}\n"
        text += "=" * 50 + "\n\n"
        
        # Información básica
        text += "📅 INFORMACIÓN DE LA ORDEN:\n"
        text += f"   • Número: {order_number}\n"
        text += f"   • Fecha: {order_data.get('fecha', 'No especificada')}\n"
        text += f"   • Ficha: {order_data.get('turno', '0')}\n"
        text += f"   • Tipo: {order_data.get('taller_domi', 'Taller')}\n\n"
        
        # Datos del cliente
        text += "👤 DATOS DEL CLIENTE:\n"
        text += f"   • Nombre: {order_data.get('nombre', 'No especificado')}\n"
        text += f"   • Teléfono 1: {order_data.get('tel1', 'No especificado')}\n"
        
        if order_data.get('tel2'):
            text += f"   • Teléfono 2: {order_data.get('tel2')}\n"
        
        if order_data.get('direccion'):
            text += f"   • Dirección: {order_data.get('direccion')}\n"
        
        text += "\n"
        
        # Datos del equipo
        text += "🔧 DATOS DEL EQUIPO:\n"
        text += f"   • Equipo: {order_data.get('equipo', 'No especificado')}\n"
        text += f"   • No. Serie: {order_data.get('no_serie', 'No especificado')}\n"
        
        if order_data.get('descripcion'):
            text += f"   • Descripción: {order_data.get('descripcion')}\n"
        
        text += f"   • Diagnóstico: {order_data.get('diagnostico', 'No especificado')}\n\n"
        
        # Estado del equipo (si está disponible)
        if order_number and order_number != 'N/A':
            estado = self.data_mgr.load_equipment_state(order_number)
            if estado and estado.lower() != 'nada':
                text += f"⚙️ ESTADO: {estado}\n\n"
        
        # Servicios (si están disponibles)
        if order_number and order_number != 'N/A':
            servicios = self.data_mgr.load_services(order_number)
            if servicios:
                text += "💰 SERVICIOS:\n"
                total = 0
                for servicio in servicios:
                    servicio_text = servicio.get('servicio', '')
                    costo = servicio.get('costo', '0')
                    
                    # Intentar calcular total
                    try:
                        costo_float = float(costo)
                        total += costo_float
                        costo_formatted = f"${costo_float:.2f}"
                    except:
                        costo_formatted = f"${costo}"
                    
                    text += f"   • {servicio_text}: {costo_formatted}\n"
                
                if total > 0:
                    text += f"   ─────────────────────\n"
                    text += f"   TOTAL: ${total:.2f}\n\n"
        
        # Pie de página
        text += "=" * 50 + "\n"
        text += "📞 SERVINORTE - (844) 311 5686\n"
        text += "📍 Pérez Treviño #147, Centro, Saltillo, Coahuila\n"
        from datetime import datetime
        text += f"🕒 Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        
        return text
    
    def _get_root_window(self):
        """Obtiene la ventana raíz de tkinter"""
        try:
            # Intentar diferentes formas de obtener la ventana raíz
            if hasattr(self, 'notebook'):
                widget = self.notebook
                # Subir por la jerarquía hasta encontrar la ventana raíz
                while widget and not isinstance(widget, tk.Tk) and hasattr(widget, 'master'):
                    widget = widget.master
                if isinstance(widget, tk.Tk):
                    return widget
            
            # Intentar otra forma
            if hasattr(self, 'window'):  # Si UITabs tiene referencia a la ventana
                return self.window
            
            # Último intento: buscar entre todos los widgets
            import tkinter as tk
            for widget in tk._default_root.children.values():
                if isinstance(widget, tk.Tk):
                    return widget
            
            return None
            
        except Exception as e:
            print(f"⚠️ Error obteniendo ventana raíz: {e}")
            return None

    def _prepare_ticket_data_from_order(self, order_data: Dict) -> Dict:
        """Prepara los datos completos para generar un ticket desde una orden existente"""
        order_number = order_data.get('no_orden', 'N/A')
        print(f"📋 Preparando datos para ticket #{order_number}")
        
        # Datos básicos de la orden
        ticket_data = {
            "no_orden": order_data.get('no_orden', ''),
            "ficha": order_data.get('turno', '0'),
            "fecha": order_data.get('fecha', ''),
            "cliente": order_data.get('nombre', ''),
            "equipo": order_data.get('equipo', ''),
            "no_serie": order_data.get('no_serie', ''),
            "diagnostico": order_data.get('diagnostico', ''),
            "tel1": order_data.get('tel1', ''),
            "tel2": order_data.get('tel2', ''),
            "direccion": order_data.get('direccion', ''),
            "taller_domi": order_data.get('taller_domi', 'Taller'),
            "descripcion": order_data.get('descripcion', '')
        }
        
        # Cargar datos adicionales si están disponibles
        if order_number and order_number != 'N/A':
            # Cargar estado del equipo
            estado = self.data_mgr.load_equipment_state(order_number)
            if estado:
                # Parsear estado (ej: "Aguja, Bobina, Motor")
                piezas = estado.split(',')
                for pieza in piezas:
                    pieza_limpia = pieza.strip().lower()
                    if pieza_limpia in ['aguja', 'bobina', 'carretel', 'devanador', 
                                       'estuche', 'foco', 'motor', 'banda', 'pedal', 
                                       'pie', 'hilo', 'abierta', 'tapa']:
                        ticket_data[pieza_limpia] = True
                    elif pieza_limpia and pieza_limpia != 'nada':
                        ticket_data['otro_piezas'] = pieza_limpia
            
            # Cargar tipo de equipo
            tipo = self.data_mgr.load_equipment_type(order_number)
            if tipo:
                tipos = tipo.split(',')
                for t in tipos:
                    t_limpio = t.strip().lower()
                    if t_limpio in ['casero', 'industrial', 'costura', 'sobrehiladora']:
                        ticket_data[t_limpio] = True
                    elif t_limpio and t_limpio != 'no especificado':
                        ticket_data['otro_tipo'] = t_limpio
            
            # Cargar servicios
            servicios = self.data_mgr.load_services(order_number)
            if servicios:
                for i, servicio in enumerate(servicios[:4], 1):  # Máximo 4 servicios
                    ticket_data[f'servicio{i}'] = servicio.get('servicio', '')
                    ticket_data[f'costo{i}'] = servicio.get('costo', '0')
        
        # Asegurar que todos los campos booleanos existan
        boolean_fields = ['aguja', 'bobina', 'carretel', 'devanador', 'estuche', 
                         'foco', 'motor', 'banda', 'pedal', 'pie', 'hilo', 
                         'abierta', 'tapa', 'casero', 'industrial', 'costura', 'sobrehiladora']
        
        for field in boolean_fields:
            if field not in ticket_data:
                ticket_data[field] = False
        
        # Asegurar campos de texto
        if 'otro_piezas' not in ticket_data:
            ticket_data['otro_piezas'] = ""
        if 'otro_tipo' not in ticket_data:
            ticket_data['otro_tipo'] = ""
        
        print(f"✅ Datos del ticket preparados: {len(ticket_data)} campos")
        return ticket_data

    # -----------CLEAR REGISTRO------------   
    def _clear_search(self):
        """Limpia los campos de búsqueda"""
        self.search_term.delete(0, tk.END)
        self._load_all_orders()
    
    def _update_status(self, message):
        """Actualiza mensaje de estado"""
        # Puedes agregar una barra de estado si quieres
        print(f"📢 {message}")
    
    def _show_error_in_tab(self, message):
        """Muestra error en la pestaña actual"""
        from tkinter import messagebox
        messagebox.showerror("Error", message, parent=self.tab_registro)

    #-------BOTONES DE EDICION------------- (Registro Tab)
    def _print_order_ticket(self, order_data: Dict):
        """Genera e imprime el ticket de una orden específica"""
        try:
            print(f"🖨️ Preparando ticket para orden #{order_data.get('no_orden', 'N/A')}")
            
            # Validar que tenemos datos mínimos
            required_fields = ['no_orden', 'fecha', 'cliente', 'equipo', 'diagnostico']
            missing_fields = [field for field in required_fields if not order_data.get(field)]
            
            if missing_fields:
                self._show_error_in_tab(
                    f"No se puede generar ticket. Faltan campos:\n"
                    f"{', '.join(missing_fields)}"
                )
                return
            
            # Preparar datos completos para el ticket
            ticket_data = self._prepare_ticket_data_from_order(order_data)
            
            # Generar el ticket
            config = TicketConfig()
            generator = TicketGenerator(config)
            ticket_content = generator.generate_ticket(ticket_data)
            
            print(f"✅ Ticket generado ({len(ticket_content)} bytes)")
            
            # Imprimir usando PrinterManager
            success = self.printer_mgr.print_ticket(ticket_content)
            
            if success:
                self._show_success_in_tab(
                    f"✅ Ticket de orden #{order_data.get('no_orden')} enviado a impresión"
                )
            else:
                self._show_warning_in_tab(
                    "⚠️ No se pudo imprimir automáticamente.\n"
                    "Se mostrarán instrucciones para impresión manual."
                )
                
        except Exception as e:
            print(f"❌ Error imprimiendo ticket: {e}")
            self._show_error_in_tab(f"Error al imprimir ticket:\n{str(e)}")
    
    def _prepare_ticket_data_from_order(self, order_data: Dict) -> Dict:
        """Prepara los datos completos para generar un ticket desde una orden existente"""
        print(f"📋 Preparando datos para ticket #{order_data.get('no_orden', 'N/A')}")
        
        # Datos básicos de la orden
        ticket_data = {
            "no_orden": order_data.get('no_orden', ''),
            "ficha": order_data.get('turno', '0'),
            "fecha": order_data.get('fecha', ''),
            "cliente": order_data.get('nombre', ''),
            "equipo": order_data.get('equipo', ''),
            "no_serie": order_data.get('no_serie', ''),
            "diagnostico": order_data.get('diagnostico', ''),
            "tel1": order_data.get('tel1', ''),
            "tel2": order_data.get('tel2', ''),
            "direccion": order_data.get('direccion', ''),
            "taller_domi": order_data.get('taller_domi', 'Taller'),
            "descripcion": order_data.get('descripcion', '')
        }
        
        # Cargar datos adicionales si están disponibles
        order_number = order_data.get('no_orden')
        
        if order_number:
            # Cargar estado del equipo
            estado = self.data_mgr.load_equipment_state(order_number)
            if estado:
                # Parsear estado (ej: "Aguja, Bobina, Motor")
                piezas = estado.split(',')
                for pieza in piezas:
                    pieza_limpia = pieza.strip().lower()
                    if pieza_limpia in ['aguja', 'bobina', 'carretel', 'devanador', 
                                       'estuche', 'foco', 'motor', 'banda', 'pedal', 
                                       'pie', 'hilo', 'abierta', 'tapa']:
                        ticket_data[pieza_limpia] = True
                    elif pieza_limpia and pieza_limpia != 'nada':
                        ticket_data['otro_piezas'] = pieza_limpia
            
            # Cargar tipo de equipo
            tipo = self.data_mgr.load_equipment_type(order_number)
            if tipo:
                tipos = tipo.split(',')
                for t in tipos:
                    t_limpio = t.strip().lower()
                    if t_limpio in ['casero', 'industrial', 'costura', 'sobrehiladora']:
                        ticket_data[t_limpio] = True
                    elif t_limpio and t_limpio != 'no especificado':
                        ticket_data['otro_tipo'] = t_limpio
            
            # Cargar servicios
            servicios = self.data_mgr.load_services(order_number)
            if servicios:
                for i, servicio in enumerate(servicios[:4], 1):  # Máximo 4 servicios
                    ticket_data[f'servicio{i}'] = servicio.get('servicio', '')
                    ticket_data[f'costo{i}'] = servicio.get('costo', '0')
        
        # Asegurar que todos los campos booleanos existan
        boolean_fields = ['aguja', 'bobina', 'carretel', 'devanador', 'estuche', 
                         'foco', 'motor', 'banda', 'pedal', 'pie', 'hilo', 
                         'abierta', 'tapa', 'casero', 'industrial', 'costura', 'sobrehiladora']
        
        for field in boolean_fields:
            if field not in ticket_data:
                ticket_data[field] = False
        
        # Asegurar campos de texto
        if 'otro_piezas' not in ticket_data:
            ticket_data['otro_piezas'] = ""
        if 'otro_tipo' not in ticket_data:
            ticket_data['otro_tipo'] = ""
        
        print(f"✅ Datos del ticket preparados: {len(ticket_data)} campos")
        return ticket_data

    #Popups (Registro Tab)
    def _show_success_in_tab(self, message: str):
        """Muestra mensaje de éxito en la pestaña registro"""
        from tkinter import messagebox
        messagebox.showinfo("Éxito", message, parent=self.tab_registro)
    
    def _show_warning_in_tab(self, message: str):
        """Muestra advertencia en la pestaña registro"""
        from tkinter import messagebox
        messagebox.showwarning("Advertencia", message, parent=self.tab_registro)
    
    def _show_error_in_tab(self, message: str):
        """Muestra error en la pestaña registro"""
        from tkinter import messagebox
        messagebox.showerror("Error", message, parent=self.tab_registro)
    
    # ------METODOS ADICIONALES------------ (Registro Tab)
    def _print_selected_order(self):
        """Imprime la orden seleccionada"""
        selection = self.results_tree.selection()
        if not selection:
            self._show_error_in_tab("Seleccione una orden para imprimir")
            return
        
        item = self.results_tree.item(selection[0])
        order_number = item['values'][0]
        
        try:
            # Cargar datos completos
            order_data = self.data_mgr.load_order_details(order_number)
            
            if order_data:
                # Generar ticket
                config = TicketConfig()
                generator = TicketGenerator(config)
                ticket_content = generator.generate_ticket(order_data)
                
                # Imprimir
                success = self.printer_mgr.print_ticket(ticket_content)
                
                if success:
                    self._update_status(f"✅ Ticket de orden #{order_number} enviado a impresión")
                else:
                    self._show_error_in_tab("No se pudo imprimir el ticket")
            else:
                self._show_error_in_tab(f"Orden #{order_number} no encontrada")
                
        except Exception as e:
            self._show_error_in_tab(f"Error imprimiendo orden:\n{str(e)}")
    
    def _copy_order_info(self):
        """Copia información de la orden seleccionada al portapapeles"""
        selection = self.results_tree.selection()
        if not selection:
            self._show_error_in_tab("Seleccione una orden para copiar")
            return
        
        item = self.results_tree.item(selection[0])
        values = item['values']
        
        # Formatear información
        info_text = {f"""Orden #{values[0]}
            Fecha: {values[1]}
            Cliente: {values[2]}
            Teléfono: {values[3]}
            Equipo: {values[4]}
            No. Serie: {values[5]}
            Diagnóstico: {values[6]}"""}
        
        try:
            self.notebook.clipboard_clear()
            self.notebook.clipboard_append(info_text)
            self._update_status("✅ Información copiada al portapapeles")
        except Exception as e:
            self._show_error_in_tab(f"Error copiando:\n{str(e)}")
    
    def _edit_order(self, order_number: int):
        """Carga una orden existente para editar"""
        from tkinter import messagebox
        
        response = messagebox.askyesno(
            "Editar Orden",
            f"¿Desea cargar la orden #{order_number} para editarla?\n\n"
            "Nota: Los datos actuales del formulario se perderán.",
            parent=self.tab_registro
        )
        
        if response:
            self._load_order_for_editing(order_number)
    
    def _load_order_for_editing(self, order_number: int):
        """Carga una orden en el formulario principal para editar"""
        try:
            # Cargar datos de la orden
            order_data = self.data_mgr.load_order_details(order_number)
            
            if not order_data:
                self._show_error_in_tab(f"Orden #{order_number} no encontrada")
                return
            
            # Cambiar a pestaña de trabajo
            self.notebook.select(0)  # Primera pestaña
            
            # Limpiar formulario primero
            self._clear_all_fields()
            
            # Establecer número de orden (no editable)
            self.counter = int(order_number)
            if hasattr(self, 'counter_label') and self.counter_label:
                self.counter_label.config(text=str(self.counter))
            
            # Llenar campos
            self.name_entry.insert(0, order_data.get('nombre', ''))
            self.phone1_entry.insert(0, order_data.get('tel1', ''))
            self.phone2_entry.insert(0, order_data.get('tel2', ''))
            self.adress_entry.insert(0, order_data.get('direccion', ''))
            self.notes_entry.insert(0, order_data.get('diagnostico', ''))
            self.equip_entry.insert(0, order_data.get('equipo', ''))
            self.serial_entry.insert(0, order_data.get('no_serie', ''))
            self.desc_entry.insert(0, order_data.get('descripcion', ''))
            self.turn_entry.insert(0, order_data.get('turno', ''))
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, order_data.get('fecha', ''))
            
            # Domicilio
            if order_data.get('taller_domi', '').lower() == 'domicilio':
                self.Domicilio_var.set(1)
            
            self._update_status(f"✅ Orden #{order_number} cargada para editar")
            
        except Exception as e:
            self._show_error_in_tab(f"Error cargando orden para editar:\n{str(e)}")

# ------------MENU PRINCIPAL---------------
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