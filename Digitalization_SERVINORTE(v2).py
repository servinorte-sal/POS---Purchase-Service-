from tkinter import messagebox, Button, ttk
import tkinter as tk
import subprocess
import platform
import datetime
import csv
import os

import io
import re


# #Imports necesarios scrap
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


#----------------Functions----------------

def load_counter():
    file_path = os.path.join(os.getcwd(), "counter.txt")
    with open(file_path, "r") as file:
        counter = int(file.read())

    return counter

def incremental_label():
    global counter
    counter += 1
    label.config(text = str(counter))
    save_work_order()

def save_work_order():
    file = open("counter.txt","w")
    file.write(str(counter))

def save_to_csv():
    dict_var ={}
    file_path = os.path.join(os.getcwd(),"Registro Ordenes de Trabajo.csv")

#---------------- Classes -----------------

class main_menu:
    def __init__ (self, x_place= 50, y_place = 40):

        self.x_place = x_place
        self.y_place = y_place
    
    def format(self):
        #Title:
        window.title("SERVINORTE")

        #geometry window
        window.geometry('900x650')
        
        window.geometry('+{}+{}'.format(self.x_place, self.y_place))

class ConfigPrinter:
    """Configuración de impresoras por defecto"""
    ConfigFile="printer_config.json"
    #INCOMPLETO

class TicketGenerator:
    """Genera Tickets para la impresora térmica"""

    def __init__(self,config):
        self.config = config
        self.width= config["paper_width"]
    def center_text(self, text):
        """centrar el texto según el ancho del ticket"""
        if len(text) >= self.width:
            return text[:self.width]
        spaces = (self.width - len(text))//2
        return " " * spaces + text
    def draw_line(self, char="-"):
        """Linea separadora"""
        return char*self.width+"\n"
    def format_two_columns(self, left, right, width_left=30):
        """Formato de dos columnas"""
        width_right = self.width - width_left - 1
        left_part = left[:width_left].ljust(width_left)
        right_part = str(right)[:width_right].ljust(width_right)
        return f"{left_part} {right_part}\n"
    
    def format_table_row(self, service, cost, width_service=30):
        """Formato para tabla de servicios"""
        width_cost = self.width - width_service - 1
        service_part = str(service)[:width_service].ljust(width_service)
        cost_part = f"${str(cost)}"[:width_cost].rjust(width_cost)
        return f"{service_part} {cost_part}\n"
    def generate_ticket(self, data):
        """Genera el contenido completo del ticket"""
        ticket = ""
        
        # Inicializar impresora (comandos ESC/POS)
        ticket = self._init_printer_commands()
        
        # Encabezado de la empresa
        ticket += self.center_text(self.config["company_name"]) + "\n"
        ticket += self.center_text(self.config["company_address"]) + "\n"
        ticket += self.center_text("C.P. 25000, Saltillo, Coahuila") + "\n"
        ticket += self.center_text(self.config["company_phone"]) + "\n"
        ticket += self.center_text(self.config["company_email"]) + "\n"
        ticket += self.draw_line("=")
        
        # Información de la orden
        ticket += self.center_text("ORDEN DE SERVICIO") + "\n"
        ticket += self.draw_line()
        ticket += self.format_two_columns("No. Orden:", data["no_orden"])
        ticket += self.format_two_columns("Fecha:", data["fecha"])
        ticket += self.format_two_columns("Ficha:", data["ficha"])
        ticket += self.format_two_columns("Taller/Domicilio:", data["taller_domi"])
        ticket += self.draw_line()
        
        # Datos del cliente
        ticket += self.center_text("DATOS DEL CLIENTE") + "\n"
        ticket += self.draw_line()
        ticket += self.format_two_columns("Cliente:", data["cliente"])
        ticket += self.format_two_columns("Teléfono 1:", data["tel1"])
        if data["tel2"]:
            ticket += self.format_two_columns("Teléfono 2:", data["tel2"])
        if data["direccion"]:
            ticket += self.format_two_columns("Dirección:", data["direccion"])
        ticket += self.draw_line()
        
        # Datos del equipo
        ticket += self.center_text("DATOS DEL EQUIPO") + "\n"
        ticket += self.draw_line()
        ticket += self.format_two_columns("Equipo:", data["equipo"])
        ticket += self.format_two_columns("No. Serie:", data["no_serie"])
        ticket += self.format_two_columns("Descripción:", data["descripcion"])
        
        # Ramo (tipos de equipo)
        ramo_text = ""
        if data.get("casero"): ramo_text += "Casero "
        if data.get("industrial"): ramo_text += "Industrial "
        if data.get("costura"): ramo_text += "Costura "
        if data.get("sobrehiladora"): ramo_text += "Sobrehiladora "
        if data.get("otro_tipo"): ramo_text += data["otro_tipo"]
        
        ticket += self.format_two_columns("Ramo:", ramo_text.strip())
        
        # Estado de recepción
        estado_text = "Le falta: "
        piezas_faltantes = []
        piezas = ["aguja", "bobina", "carretel", "devanador", "estuche", 
                 "foco", "motor", "banda", "pedal", "pie", "hilo", 
                 "abierta", "tapa", "otro_piezas"]
        
        for pieza in piezas:
            if data.get(pieza):
                piezas_faltantes.append(pieza.capitalize())
        
        estado_text += ", ".join(piezas_faltantes) if piezas_faltantes else "Nada"
        ticket += self.format_two_columns("Estado:", estado_text[:self.width-10])
        
        # Diagnóstico
        ticket += self.format_two_columns("Diagnóstico:", data["diagnostico"])
        ticket += self.draw_line()
        
        # Servicios y costos
        ticket += self.center_text("SERVICIOS") + "\n"
        ticket += self.draw_line()
        ticket += self.format_table_row("SERVICIO", "COSTO")
        ticket += self.draw_line()
        
        # Obtener servicios desde la interfaz
        servicios = [
            (data.get("servicio1", ""), data.get("costo1", "0")),
            (data.get("servicio2", ""), data.get("costo2", "0")),
            (data.get("servicio3", ""), data.get("costo3", "0")),
            (data.get("servicio4", ""), data.get("costo4", "0"))
        ]
        
        total = 0
        for servicio, costo in servicios:
            if servicio and costo:
                try:
                    costo_float = float(costo)
                    total += costo_float
                    ticket += self.format_table_row(servicio, f"{costo_float:.2f}")
                except:
                    ticket += self.format_table_row(servicio, costo)
        
        ticket += self.draw_line()
        ticket += self.format_table_row("TOTAL", f"{total:.2f}")
        ticket += self.draw_line()
        
        # Notas y garantía
        ticket += self.center_text("NOTAS IMPORTANTES") + "\n"
        ticket += self.draw_line("-")
        
        garantia = (
            "GARANTÍA: Cubre misma falla por 30 días. "
            "No incluye refacciones, domicilio ni mal uso. "
            "Equipos no reclamados en 6 meses se donan."
        )
        
        # Dividir texto largo en líneas
        palabras = garantia.split()
        linea = ""
        for palabra in palabras:
            if len(linea + " " + palabra) <= self.width:
                linea += " " + palabra
            else:
                ticket += linea.strip() + "\n"
                linea = palabra
        if linea:
            ticket += linea.strip() + "\n"
        
        ticket += self.draw_line()
        ticket += self.center_text("** GRACIAS POR SU CONFIANZA **") + "\n"
        
        # Espacios para firmas
        ticket += "\n" * 2
        ticket += self.format_two_columns("Firma cliente:", "________________")
        ticket += self.format_two_columns("Fecha entrega:", "________________")
        
        # Comandos finales para la impresora
        ticket += self._end_printer_commands()
        
        return ticket.encode('utf-8', errors='ignore')
    
    def _init_printer_commands(self):
        """Comandos ESC/POS para inicializar"""
        # Convertir a string con caracteres de escape
        return "\x1B\x40" + "\x1B\x0F"  # Init + Font A condensed
    
    def _end_printer_commands(self):
        """Comandos finales ESC/POS"""
        return "\n\n\n\n\x1D\x56\x00"  # Avanzar y cortar
    

class alltabs:
    def __init__(self, tabs):
        self.tabs = tabs
        self.counter = load_counter()

        #Variables to save data
        self.order_text = None
        self.name_entry = None
        self.phone1_entry = None
        self.phone2_entry = None
        self.adress_entry = None
        self.equipo_entry = None
        self.serial_entry = None
        self.turn_entry = None
        self.get_data_entry = None
        self.notes_entry = None
        self.date_entry2 = None

        self.get_data_entry = []
    
        #Checkboxes
        self.chkbx1_var= None
        self.chkbx2_var= None
        self.chkbx3_var= None
        self.chkbx4_var= None
        self.chkbx5_var= None
        self.chkbx6_var= None
        self.chkbx7_var= None
        self.chkbx8_var= None
        self.chkbx9_var= None
        self.chkbx10_var= None
        self.chkbx11_var= None
        self.chkbx12_var= None
        self.chkbx13_var= None
        self.chkbx14_var= None
        self.chkbx15_var= None
        self.chkbx16_var= None
        self.chkbx17_var= None

        self.chkbx1= None
        self.chkbx2= None
        self.chkbx3= None
        self.chkbx4= None
        self.chkbx5= None
        self.chkbx6= None
        self.chkbx7= None
        self.chkbx8= None
        self.chkbx9= None
        self.chkbx10= None
        self.chkbx11= None
        self.chkbx12= None
        self.chkbx13= None
        self.chkbx14= None
        self.chkbx15= None
        self.chkbx16= None
        self.chkbx16= None

        self.other_equip_entry = None
        self.other_entry = None

        self.Domicilio_var = None

        self.entry1 = None
        self.entry2 = None
        self.entry3 = None
        self.entry4 = None
        self.entries1 = None
        self.entries2 = None
        self.entries3 = None
        self.entries4 = None

        self.get_checked_items = []

        self.popup2 = None

    def new_odt_button(self):
        self.name_entry.delete(0,tk.END)
        self.phone1_entry.delete(0,tk.END)
        self.phone2_entry.delete(0,tk.END)
        self.adress_entry.delete(0,tk.END)
        self.notes_entry.delete(0,tk.END)
        self.equip_entry.delete(0,tk.END)
        self.serial_entry.delete(0,tk.END)
        self.desc_entry.delete(0,tk.END)

        self.chkbx1_var.set(0)
        self.chkbx2_var.set(0)
        self.chkbx3_var.set(0)
        self.chkbx4_var.set(0)
        self.chkbx5_var.set(0)
        self.chkbx6_var.set(0)
        self.chkbx7_var.set(0)
        self.chkbx8_var.set(0)
        self.chkbx9_var.set(0)
        self.chkbx10_var.set(0)
        self.chkbx11_var.set(0)
        self.chkbx12_var.set(0)
        self.chkbx13_var.set(0)
        self.chkbx14_var.set(0)
        self.chkbx15_var.set(0)
        self.chkbx16_var.set(0)
        self.chkbx17_var.set(0)   

        self.other_equip_entry.delete(0,tk.END)
        self.other_entry.delete(0,tk.END)
        self.turn_entry.delete(0,tk.END)

        self.entry1.delete(0,tk.END)
        self.entry2.delete(0,tk.END)
        self.entry3.delete(0,tk.END)
        self.entry4.delete(0,tk.END)
        self.entries5.delete(0,tk.END)
        self.entries6.delete(0,tk.END)
        self.entries7.delete(0,tk.END)
        self.entries8.delete(0,tk.END)

        self.Domicilio_var.set(0)

        self.date_entry.delete(0,tk.END)
        self.date_entry.insert(tk.END,date_format)

        incremental_label()
        self.popup_cleaned_data()
        
    def save_data(self):
        #Personal information
        no_orden = str(self.counter)
        nombre = self.name_entry.get()
        tel1 = self.phone1_entry.get()
        tel2 = self.phone2_entry.get()
        direc= self.adress_entry.get()
        equip= self.equip_entry.get()
        serie= self.serial_entry.get()
        turno= self.turn_entry.get()
        fecha= self.date_entry.get()
        diag = self.notes_entry.get()
        domi = self.Domicilio_var.get()
        desc = self.desc_entry.get()

        other_pieces = self.other_equip_entry.get()
        other_types = self.other_entry.get()

        if domi == 1:
            domi = "Domicilio"
        else:
            domi = "Taller"

        datalist = (no_orden,turno,fecha,nombre,equip,serie,diag,tel1,tel2,direc,domi,desc)
        
        with open(fileWO,"a",newline="") as filedata:
            writter = csv.writer(filedata, delimiter =";")
            writter.writerow(datalist)
        
        #registrate the ckeckboxes
        if self.chkbx1_var.get()=="1":
            check1="Aguja, "
        else:
            check1=""

        if self.chkbx2_var.get()=="1":
            check2="Bobina, "
        else:
            check2=""

        if self.chkbx3_var.get()=="1":
            check3="Carretel, "
        else:
            check3=""

        if self.chkbx4_var.get()=="1":
            check4="Devanador, "
        else:
            check4=""
        
        if self.chkbx5_var.get()=="1":
            check5="Estuche/bolsa, "
        else:
            check5=""
        
        if self.chkbx6_var.get()=="1":
            check6="Foco, "
        else:
            check6=""

        if self.chkbx7_var.get()=="1":
            check7="Motor, "
        else:
            check7=""
        
        if self.chkbx8_var.get()=="1":
            check8="Banda, "
        else:
            check8=""
        
        if self.chkbx9_var.get()=="1":
            check9="Pedal, "
        else:
            check9=""

        if self.chkbx10_var.get()=="1":
            check10="Pie, "
        else:
            check10=""
        
        if self.chkbx11_var.get()=="1":
            check11="Hilo, "
        else:
            check11=""

        if self.chkbx16_var.get()=="1":
            check16="Abierta, "
        else:
            check16=""
        if self.other_equip_entry.get() != "None":
            check_other=self.other_equip_entry.get()
        else:
            check_other=""
        
        if self.chkbx17_var.get() == "1":
            check17="TapaFrontal, "
        else:
            check17=""
        #type of equipment
        if self.chkbx12_var.get()=="1":
            check12="Casero, "
        else:
            check12=""

        if self.chkbx13_var.get()=="1":
            check13="Industrial, "
        else:
            check13=""

        if self.chkbx14_var.get()=="1":
            check14="Costura, "
        else:
            check14=""
        
        if self.chkbx15_var.get()=="1":
            check15="Sobrehiladora, "
        else:
            check15=""
        
        if self.other_entry.get() != "None":
            check_other_type=self.other_entry.get()
        else:
            check_other_type=""
        
        data_checks =(no_orden, check1, check2, check3, check4, check5, check6, check7, check8, check9, check10, check11, check16,check17,check_other)
        data_type = (no_orden,check12,check13,check14,check15,check_other_type)

        with open("Estado de equipos.csv","a",newline="") as file_state:
            writter2 = csv.writer(file_state, delimiter =";")
            writter2.writerow(data_checks)
        with open("Tipos de equipos.csv","a",newline="") as file_types:
            writter3 = csv.writer(file_types, delimiter =";")
            writter3.writerow(data_type)
        
        self.popup_saved_data()

    def save_and_load(self):
        self.save_data()
    
    def popup_saved_data(self):
        popup = tk.Toplevel(self.tabs)
        popup.title("Orden de trabajo")
        popup.geometry("400x100+300+300")
        
        label = tk.Label(popup, text="¡Se han guardado los datos con éxito!",font="Arial,24")
        label.pack(pady=20)

        btn_close = ttk.Button(popup, text="Cerrar", command=popup.destroy)
        btn_close.pack()
    
    def popup_cleaned_data(self):
        popup = tk.Toplevel(self.tabs)
        popup.title("Orden de trabajo")
        popup.geometry("400x100+300+300")
        
        label = tk.Label(popup, text="¡Se han limpiado los datos correctamente!",font="Arial,24")
        label.pack(pady=20)

        btn_close = ttk.Button(popup, text="OK", command=popup.destroy)
        btn_close.pack()

    def update_pdf_document(self):
        #Importación de datos para ReportLab (para PDF's)
        # from reportlab.pdfgen import canvas
        # from reportlab.platypus import SimpleDocTemplate,Table,TableStyle,Frame,Spacer,Paragraph
        # from reportlab.platypus import PageBreak
        # from reportlab.lib.styles import getSampleStyleSheet
        # from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
        # from reportlab.lib.colors import PCMYKColor, PCMYKColorSep, Color, black, blue, red
        # from reportlab.lib.units import cm
        # from reportlab.lib import colors

        #Obtención de datos
        with open(fileWO,"r") as Datos1:
            #csv_datos=Datos1.read()
            lector_datos=csv.reader(Datos1,delimiter=";")
            #no_orden, ficha, fecha, cliente, equipo, no_serie, diagnostico, tel1, tel2, direction, taller_domi = Datos_de_archivo
            for fila in lector_datos:
                ultima_fila = list(lector_datos)
            
            dato=ultima_fila[-1]
            Datos1.close()

        no_orden = dato[0]
        ficha = dato[1]
        fecha = dato[2]
        cliente= dato[3]
        equipo = dato[4]
        no_serie = dato[5]
        diagnostico=dato[6]
        tel1 = dato[7]
        tel2 = dato[8]
        direction=dato[9]
        taller_domi=dato[10]
        descripcion = dato[11]

        with open("Estado de equipos.csv","r") as Datos2:
            lector_estado = csv.reader(Datos2,delimiter=";")
            for fila1 in lector_estado:
                ultima_fila_estado = list(lector_estado)
                dato_estado = ultima_fila_estado[-1]
                
                aguja= dato_estado[1]
                bobina=dato_estado[2]
                carretel=dato_estado[3]
                devanador=dato_estado[4]
                estuche=dato_estado[5]
                foco=dato_estado[6]
                motor=dato_estado[7]
                banda=dato_estado[8]
                pedal=dato_estado[9]
                pie=dato_estado[10]
                hilo=dato_estado[11]
                abierta=dato_estado[12]
                tapa=dato_estado[13]
                otro_piezas=dato_estado[14]
            Datos2.close()
        
        with open("Tipos de equipos.csv","r")as Datos3:
            lector_tipos = csv.reader(Datos3,delimiter=";")
            for fila2 in lector_tipos:
                ultima_fila_tipos = list(lector_tipos)
                dato_tipos = ultima_fila_tipos[-1]

                casero=dato_tipos[1]
                industrial=dato_tipos[2]
                costura=dato_tipos[3]
                sobrehiladora=dato_tipos[4]
                otro_tipo=dato_tipos[5]
            Datos3.close()
        ticket_data={
            "no_orden": no_orden,
            "ficha":    ficha,
            "fecha":    fecha,
            "cliente":  cliente,
            "equipo":   equipo,
            "no_serie": no_serie,
            "diagnostico": diagnostico,
            "tel1":     tel1,
            "tel2":     tel2,
            "direccion":direction,
            "taller_domi":taller_domi,
            "descripcion":descripcion,

            "aguja":    aguja,
            "bobina":   bobina,
            "carretel": carretel,
            "devanador":devanador,
            "estuche":  estuche,
            "foco":     foco,
            "motor":    motor,
            "banda":    banda,
            "pedal":    pedal,
            "pie":      pie,
            "hilo":     hilo,
            "abierta":  abierta,
            "tapa":     tapa,
            "otro_piezas":otro_piezas,

            "casero":   casero,
            "industrial":industrial,
            "costura":  costura,
            "sobrehiladora": sobrehiladora,
            "otro_tipo": otro_tipo,

            "servicio1": self.entry1.get() if hasattr(self, 'entry1') else "",
            "costo1": self.entries5.get() if hasattr(self, 'entries5') else "0",
            "servicio2": self.entry2.get() if hasattr(self, 'entry2') else "",
            "costo2": self.entries6.get() if hasattr(self, 'entries6') else "0",
            "servicio3": self.entry3.get() if hasattr(self, 'entry3') else "",
            "costo3": self.entries7.get() if hasattr(self, 'entries7') else "0",
            "servicio4": self.entry4.get() if hasattr(self, 'entry4') else "",
            "costo4": self.entries8.get() if hasattr(self, 'entries8') else "0"
            }
        
        config = {
            "company_name": "SERVINORTE",
            "company_address": "Pérez Treviño #147, Centro",
            "company_phone": "(844) 311 5686",
            "company_email": "servinortesaclientes@gmail.com",
            "paper_width": 48
            }
        
        ticket_gen = TicketGenerator(config)
        ticket_content = ticket_gen.generate_ticket(ticket_data)
        archivo_txt = os.path.join(os.getcwd(), "TICKET.txt")
        
        with open(archivo_txt, 'wb') as f:
            f.write(ticket_content)

        archivo_ticket_orden = os.path.join(os.getcwd(), "Ordenes_de_Trabajo", f"Ticket_Orden_{no_orden}.txt")
        
        with open(archivo_ticket_orden, 'wb') as f:
            f.write(ticket_content)
    
        print(f"Ticket generado: {archivo_txt}")
        print(f"Backup guardado: {archivo_ticket_orden}")
    
        return archivo_txt

        estilo=getSampleStyleSheet()

        carpeta=os.path.join(os.getcwd(),"Ordenes_de_Trabajo")
        archivo = os.path.join(carpeta,"Orden_no_" + no_orden + ".pdf")

        pdf=canvas.Canvas(archivo)
        pdf.translate(cm,cm)

        ancho_doc = 540
        alto_doc  = 750

        columna1_x = 0+5
        columna2_x = 540/3+5
        columna3_x = 540/3*2+5
        fila1_y = 750
        ancho_columna = 540/3

        #Logo
        ruta_logo = os.path.join(os.path.dirname(__file__),"Logo.png")
        logo_x = columna1_x
        logo_y = fila1_y+7
        logo_ancho = 120
        logo_alto = 40

        #Encabezado
        pdf.rect(0,750,560,50)
        pdf.drawImage(ruta_logo, logo_x, logo_y, logo_ancho, logo_alto)
        pdf.drawString(columna2_x-18, fila1_y+25, "Pérez Treviño #147, Centro,")
        pdf.drawString(columna2_x-19,fila1_y+10,"C.P. 25000, Saltillo, Coahuila")
        pdf.drawString(columna3_x-5, fila1_y+25, "Tel. (844) 311 5686")
        pdf.drawString(columna3_x-5, fila1_y+10,"servinortesaclientes@gmail.com")

        fila2_y = fila1_y-30
        pdf.setFont("Helvetica-Bold",16)
        pdf.drawString(columna3_x-5, fila2_y-35,"Fecha: ")
        pdf.drawString(columna1_x,fila2_y-35,"No. Orden: ")
        pdf.drawString(columna3_x-5,fila2_y-75,taller_domi)

        pdf.setFont("Helvetica",16)
        pdf.drawString(columna3_x+53, fila2_y-35, fecha)
        pdf.drawString(columna1_x+100, fila2_y-35,no_orden)
        #Formatos de texto
        #Para secciones ("Helvetica-Bold",16)
        #Para campos de entrada ("Helvetica-Bold",12)
        #Textos pequeños ("Helvetica",9)

        #----------Orden de trabajo---------------
        pdf.line(columna1_x,fila2_y-15,ancho_doc,fila2_y-15)
        pdf.setFont("Helvetica-Bold",18)
        pdf.drawString(columna2_x-5, fila2_y,"Orden de servicio")

        #Enmarcar numero de ficha
        pdf.setFont("Helvetica-Bold",20)
        pdf.rect(0,fila2_y-15-70,columna2_x,70)
        pdf.drawString(columna1_x,fila2_y-75,"Ficha: ")
        pdf.drawString(columna1_x+100,fila2_y-75, ficha)

        #Datos del cliente
        fila3_y = fila2_y-110
        pdf.setFont("Helvetica-Bold",12)
        pdf.drawString(columna1_x,fila3_y,"Cliente:")
        pdf.drawString(columna1_x,fila3_y-15,"Teléfono 1:")
        pdf.drawString(columna1_x,fila3_y-15*2,"Teléfono 2:")
        pdf.drawString(columna1_x,fila3_y-15*3,"Dirección (opcional):")

        pdf.setFont("Helvetica",12)
        pdf.drawString(columna2_x,fila3_y, cliente)
        pdf.drawString(columna2_x,fila3_y-15, tel1)
        pdf.drawString(columna2_x,fila3_y-15*2, tel2)

        pdf.setFont("Helvetica",10)
        pdf.drawString(columna2_x,fila3_y-15*3, direction)

        #----------Datos del equipo---------------
        fila4_y = fila2_y-30*6.5
        pdf.line(columna1_x,fila4_y-10,ancho_doc,fila4_y-10)
        pdf.setFont("Helvetica-Bold",18)
        pdf.drawString(columna2_x, fila2_y-30*6.5,"Datos del equipo")

        pdf.setFont("Helvetica-Bold",12)
        pdf.drawString(columna1_x,fila4_y-10-15,"Equipo:")
        pdf.drawString(columna1_x,fila4_y-10-15*2,"No. Serie:")
        pdf.drawString(columna1_x,fila4_y-10-15*3,"Descripción:")
        pdf.drawString(columna1_x,fila4_y-10-15*4,"Ramo:")
        pdf.drawString(columna1_x,fila4_y-10-15*5,"Estado de recepción:")
        pdf.drawString(columna1_x,fila4_y-10-15*6,"Diagnóstico:")

        pdf.setFont("Helvetica",12)
        pdf.drawString(columna2_x,fila4_y-25,equipo)
        pdf.drawString(columna2_x,fila4_y-10-15*2,no_serie)
        pdf.drawString(columna2_x,fila4_y-10-15*3,descripcion)
        pdf.drawString(columna2_x,fila4_y-10-15*4,casero + industrial + costura + sobrehiladora + otro_tipo)
        pdf.setFont("Helvetica",10)
        pdf.drawString(columna2_x,fila4_y-10-15*5,"Le falta: "+aguja+bobina+carretel+devanador+estuche+foco+motor+banda+pedal+pie+hilo+abierta+tapa+otro_piezas)
        pdf.setFont("Helvetica",12)        
        pdf.drawString(columna2_x,fila4_y-10-15*6,diagnostico)

        #----------Datos del equipo---------------
        fila5_y = fila4_y-100
        pdf.setFont("Helvetica-Bold",18)
        pdf.drawString(columna2_x, fila5_y-30,"Servicio")

        #Formato de tabla
        pdf.setFont("Helvetica-Bold",12)
        pdf.drawString(columna1_x,fila5_y-50-15,"Servicio")
        pdf.drawString(columna3_x+100,fila5_y-50-15,"Costo")

        pdf.line(columna1_x,fila5_y-50,ancho_doc,fila5_y-50)
        pdf.line(columna1_x,fila5_y-50-25,ancho_doc,fila5_y-50-25)
        pdf.line(columna1_x,fila5_y-50-25*5,ancho_doc,fila5_y-50-25*5)

        pdf.setFont("Helvetica",12)
        pdf.drawString(columna1_x,fila5_y-50-20*2, self.entry1.get())
        pdf.drawString(columna1_x,fila5_y-50-20*3,self.entry2.get())
        pdf.drawString(columna1_x,fila5_y-50-20*4,self.entry3.get())
        pdf.drawString(columna1_x,fila5_y-50-20*5,self.entry4.get())

        pdf.drawString(columna3_x+100,fila5_y-50-20*2,self.entries5.get())
        pdf.drawString(columna3_x+100,fila5_y-50-20*3,self.entries6.get())
        pdf.drawString(columna3_x+100,fila5_y-50-20*4,self.entries7.get())
        pdf.drawString(columna3_x+100,fila5_y-50-20*5,self.entries8.get())

        #NOTAS del documento
        pdf.setFont("Helvetica-Bold",18)
        pdf.drawString(columna2_x,fila5_y-60-20*7,"Notas")
        pdf.rect(0,fila5_y-170-20*7,540,100)

        pdf.setFont("Helvetica",12)
        pdf.drawString(columna1_x,fila5_y-50-170-20*7,"")

        fila6_y = fila5_y-170-20*7

        pdf.setFont("Helvetica-Bold",10)
        pdf.drawString(columna1_x,fila6_y-15,"Cláusula de garantía")

        #Garantía
        pdf.setFont("Helvetica",10)
        pdf.drawString(columna1_x,fila6_y-25,"El servicio de garantía incluye reparación del mismo defecto y servicio de ingeniería dentro de la fecha estipulada.")
        pdf.drawString(columna1_x,fila6_y-35,"NO incluye: Refacciones, servicio a domicilio ni servicio a equipos por mal uso ni intervención de equipo. NO nos ")
        pdf.drawString(columna1_x,fila6_y-45,"hacemos responsables de equipos que NO se reciba respuesta por parte del cliente y transcurra un lapso mayor o")
        pdf.drawString(columna1_x,fila6_y-55,"igual a 6 meses. La grantía se cubre a ______ días después de la entrega del equipo")

        #Firma y fecha de entrega
        pdf.drawString(columna2_x,fila6_y-67,"FIRMA____________________")
        pdf.drawString(columna3_x,fila6_y-67,"Entregado _______________________")

        #___________________________Nota del cliente_________________________
        pdf.showPage()
        
        ancho_doc = 540
        alto_doc  = 750

        #estilo
        columna1_x = columna1_x +30
        columna2_x = columna2_x +30
        columna3_x = columna3_x +30

        #Encabezado
        pdf.rect(20,750,560,50)
        pdf.drawImage(ruta_logo, logo_x+20, logo_y, logo_ancho, logo_alto)
        pdf.drawString(columna2_x-18, fila1_y+25, "Pérez Treviño #147, Centro,")
        pdf.drawString(columna2_x-19,fila1_y+10,"C.P. 25000, Saltillo, Coahuila")
        pdf.drawString(columna3_x-5, fila1_y+25, "Tel. (844) 311 5686")
        pdf.drawString(columna3_x-5, fila1_y+10,"servinortesaclientes@gmail.com")

        fila2_y = fila1_y-30
        pdf.setFont("Helvetica-Bold",16)
        pdf.drawString(columna3_x-5, fila2_y-35,"Fecha: ")
        pdf.drawString(columna1_x,fila2_y-35,"No. Orden: ")
        pdf.drawString(columna3_x-5,fila2_y-75,taller_domi)

        pdf.setFont("Helvetica",16)
        pdf.drawString(columna3_x+53, fila2_y-35, fecha)
        pdf.drawString(columna1_x+100, fila2_y-35,no_orden)

        #Formatos de texto
        #Para secciones ("Helvetica-Bold",16)
        #Para campos de entrada ("Helvetica-Bold",12)
        #Textos pequeños ("Helvetica",9)

        #----------Orden de trabajo---------------
        pdf.line(columna1_x+30,fila2_y-15,ancho_doc,fila2_y-15)
        pdf.setFont("Helvetica-Bold",18)
        pdf.drawString(columna2_x-5, fila2_y,"Orden de servicio")

        #Enmarcar numero de ficha
        pdf.setFont("Helvetica-Bold",20)
        pdf.rect(30,fila2_y-15-70,columna2_x,70)
        pdf.drawString(columna1_x,fila2_y-75,"Ficha: ")
        pdf.drawString(columna1_x+100,fila2_y-75, ficha)

        #Datos del cliente
        fila3_y = fila2_y-110
        pdf.setFont("Helvetica-Bold",12)
        pdf.drawString(columna1_x,fila3_y,"Cliente:")
        pdf.drawString(columna1_x,fila3_y-15,"Teléfono 1:")
        pdf.drawString(columna1_x,fila3_y-15*2,"Teléfono 2:")
        pdf.drawString(columna1_x,fila3_y-15*3,"Dirección (opcional):")

        pdf.setFont("Helvetica",12)
        pdf.drawString(columna2_x,fila3_y, cliente)
        pdf.drawString(columna2_x,fila3_y-15, tel1)
        pdf.drawString(columna2_x,fila3_y-15*2, tel2)

        pdf.setFont("Helvetica",10)
        pdf.drawString(columna2_x,fila3_y-15*3, direction)

        #----------Datos del equipo---------------
        fila4_y = fila2_y-30*6.5
        pdf.line(columna1_x,fila4_y-10,ancho_doc,fila4_y-10)
        pdf.setFont("Helvetica-Bold",18)
        pdf.drawString(columna2_x, fila2_y-30*6.5,"Datos del equipo")

        pdf.setFont("Helvetica-Bold",12)
        pdf.drawString(columna1_x,fila4_y-10-15,"Equipo:")
        pdf.drawString(columna1_x,fila4_y-10-15*2,"No. Serie:")
        pdf.drawString(columna1_x,fila4_y-10-15*3,"Descripción:")
        pdf.drawString(columna1_x,fila4_y-10-15*4,"Ramo:")
        pdf.drawString(columna1_x,fila4_y-10-15*5,"Estado de recepción:")
        pdf.drawString(columna1_x,fila4_y-10-15*6,"Diagnóstico:")

        pdf.setFont("Helvetica",12)
        pdf.drawString(columna2_x,fila4_y-25,equipo)
        pdf.drawString(columna2_x,fila4_y-10-15*2,no_serie)
        pdf.drawString(columna2_x,fila4_y-10-15*3,descripcion)
        pdf.drawString(columna2_x,fila4_y-10-15*4,casero + industrial + costura + sobrehiladora + otro_tipo)
        pdf.setFont("Helvetica",10)
        pdf.drawString(columna2_x,fila4_y-10-15*5,"Le falta: "+aguja+bobina+carretel+devanador+estuche+foco+motor+banda+pedal+pie+hilo+abierta+tapa+otro_piezas)
        pdf.setFont("Helvetica",12)
        pdf.drawString(columna2_x,fila4_y-10-15*6,diagnostico)

        #----------Datos del equipo---------------
        fila5_y = fila4_y-100
        pdf.setFont("Helvetica-Bold",18)
        pdf.drawString(columna2_x, fila5_y-30,"Servicio")

        #Formato de tabla
        pdf.setFont("Helvetica-Bold",12)
        pdf.drawString(columna1_x,fila5_y-50-15,"Servicio")
        pdf.drawString(columna3_x+100,fila5_y-50-15,"Costo")

        pdf.line(columna1_x,fila5_y-50,ancho_doc,fila5_y-50)
        pdf.line(columna1_x,fila5_y-50-25,ancho_doc,fila5_y-50-25)
        pdf.line(columna1_x,fila5_y-50-25*5,ancho_doc,fila5_y-50-25*5)

        pdf.setFont("Helvetica",12)
        pdf.drawString(columna1_x,fila5_y-50-20*2, self.entry1.get())
        pdf.drawString(columna1_x,fila5_y-50-20*3,self.entry2.get())
        pdf.drawString(columna1_x,fila5_y-50-20*4,self.entry3.get())
        pdf.drawString(columna1_x,fila5_y-50-20*5,self.entry4.get())

        pdf.drawString(columna3_x+100,fila5_y-50-20*2,self.entries5.get())
        pdf.drawString(columna3_x+100,fila5_y-50-20*3,self.entries6.get())
        pdf.drawString(columna3_x+100,fila5_y-50-20*4,self.entries7.get())
        pdf.drawString(columna3_x+100,fila5_y-50-20*5,self.entries8.get())

        #NOTAS del documento
        pdf.setFont("Helvetica-Bold",18)
        pdf.drawString(columna2_x,fila5_y-60-20*7,"Notas")
        pdf.rect(30,fila5_y-170-20*7,520,100)

        pdf.setFont("Helvetica",12)
        pdf.drawString(columna1_x,fila5_y-50-170-20*7,"")

        fila6_y = fila5_y-170-20*7

        pdf.setFont("Helvetica-Bold",10)
        pdf.drawString(columna1_x,fila6_y-15,"Cláusula de garantía")

        #Garantía
        pdf.setFont("Helvetica",10)
        pdf.drawString(columna1_x,fila6_y-25,"El servicio de garantía incluye reparación del mismo defecto y servicio de ingeniería dentro de la fecha estipulada.")
        pdf.drawString(columna1_x,fila6_y-35,"NO incluye: Refacciones, servicio a domicilio ni servicio a equipos por mal uso ni intervención de equipo. NO nos ")
        pdf.drawString(columna1_x,fila6_y-45,"hacemos responsables de equipos que NO se reciba respuesta por parte del cliente y transcurra un lapso mayor o")
        pdf.drawString(columna1_x,fila6_y-55,"igual a 6 meses. La grantía se cubre a ______ días después de la entrega del equipo")
        
        marca_de_agua = Color(0,0,0,alpha=0.15)
        pdf.rotate(55)

        pdf.setFont("Helvetica-Bold",140)
        pdf.setFillColor(marca_de_agua)
        pdf.drawString(380, 25, "Cliente")
        #_____________________________________________________________________
        #___________________________Reporte___________________________________
        pdf.showPage()

        #estilo
        
        #Colores
        black_transparent = Color( 0, 0, 0, alpha=0.5)
        black = Color( 0, 0, 0, alpha=1)

        pdf.rect(20,750,560,50)
        pdf.drawImage(ruta_logo, logo_x+20, logo_y, logo_ancho, logo_alto)
        pdf.drawString(columna2_x-18, fila1_y+25, "Pérez Treviño #147, Centro,")
        pdf.drawString(columna2_x-19,fila1_y+10,"C.P. 25000, Saltillo, Coahuila")
        pdf.drawString(columna3_x-5, fila1_y+25, "Tel. (844) 311 5686")
        pdf.drawString(columna3_x-5, fila1_y+10,"servinortesaclientes@gmail.com")
        pdf.line(columna1_x,fila2_y-15,ancho_doc,fila2_y-15)
        pdf.setFont("Helvetica-Bold",18)
        pdf.drawString(columna2_x-5, fila2_y,"Reporte")

        #Enmarcar numero de ficha
        pdf.setFont("Helvetica-Bold",16)
        pdf.drawString(columna3_x-5, fila2_y-35,"Fecha: ")
        pdf.drawString(columna1_x,fila2_y-35,"No. Orden: ")
        pdf.drawString(columna3_x-5,fila2_y-75,taller_domi)

        pdf.setFont("Helvetica",16)
        pdf.drawString(columna3_x+53, fila2_y-35, fecha)
        pdf.drawString(columna1_x+100, fila2_y-35,no_orden)
        
        pdf.setFont("Helvetica-Bold",20)
        pdf.rect(30,fila2_y-15-70,columna2_x,70)
        pdf.drawString(columna1_x,fila2_y-75,"Ficha: ")
        pdf.drawString(columna1_x+100,fila2_y-75, ficha)

        #Datos del equipo
        pdf.line(columna1_x,fila3_y-10,ancho_doc,fila3_y-10)
        pdf.setFont("Helvetica-Bold",18)
        pdf.drawString(columna2_x,fila3_y,"Datos del equipo")

        pdf.setFont("Helvetica-Bold",12)
        pdf.drawString(columna1_x,fila3_y-10-15,"Equipo:")
        pdf.drawString(columna1_x,fila3_y-10-15*2,"No. Serie:")
        pdf.drawString(columna1_x,fila3_y-10-15*3,"Descripción:")
        pdf.drawString(columna1_x,fila3_y-10-15*4,"Ramo:")
        pdf.drawString(columna1_x,fila3_y-10-15*5,"Estado de recepción:")
        pdf.drawString(columna1_x,fila3_y-10-15*6,"Diagnóstico:")

        pdf.setFont("Helvetica",12)
        pdf.drawString(columna2_x,fila3_y-25,equipo)
        pdf.drawString(columna2_x,fila3_y-10-15*2,no_serie)
        pdf.drawString(columna2_x,fila3_y-10-15*3,descripcion)
        pdf.drawString(columna2_x,fila3_y-10-15*4,casero + industrial + costura + sobrehiladora + otro_tipo)
        pdf.setFont("Helvetica",10)
        pdf.drawString(columna2_x,fila3_y-10-15*5,"Le falta: "+aguja+bobina+carretel+devanador+estuche+foco+motor+banda+pedal+pie+hilo+abierta+tapa+otro_piezas)
        pdf.setFont("Helvetica",12)
        pdf.drawString(columna2_x,fila3_y-10-15*6,diagnostico)

        #Tabla de chequeo
        inicio_tabla = fila3_y-10*14-10
        
        pdf.setFont("Helvetica-Bold",14)
        pdf.drawString(columna2_x,fila3_y-10*12,"Chequeo general")
        
        pdf.setFont("Helvetica",12)
        pdf.line(columna1_x,fila3_y-10*13,ancho_doc,fila3_y-10*13)
        pdf.drawString(columna2_x,fila3_y-10*14-5,"Estado")
        pdf.drawString(columna3_x,fila3_y-10*14-5,"Notas")

        pdf.setStrokeColor(black_transparent)

        for i in range(0,14):
            pdf.line(columna1_x,inicio_tabla-15*i, ancho_doc, inicio_tabla-15*i)

        #Contenido
        pdf.setFont("Helvetica",10)

        pdf.setFillColor(black)
        pdf.drawString(columna1_x,inicio_tabla-10-1,"Tiempo")
        pdf.drawString(columna1_x,inicio_tabla-25-1,"Alimentación/Avance")
        pdf.drawString(columna1_x,inicio_tabla-25-15-1,"Zig-Zag")
        pdf.drawString(columna1_x,inicio_tabla-25-15*2-1,"Posición barra de aguja")
        pdf.drawString(columna1_x,inicio_tabla-25-15*3-1,"Tensión")
        pdf.drawString(columna1_x,inicio_tabla-25-15*4-1,"Barra del pie")
        pdf.drawString(columna1_x,inicio_tabla-25-15*5-1,"Engranaje")
        pdf.drawString(columna1_x,inicio_tabla-25-15*6-1,"Devanador y Clutch")
        pdf.drawString(columna1_x,inicio_tabla-25-15*7-1,"Cableado")
        pdf.drawString(columna1_x,inicio_tabla-25-15*8-1,"Pedal")
        pdf.drawString(columna1_x,inicio_tabla-25-15*9-1,"Motor/banda")
        pdf.drawString(columna1_x,inicio_tabla-25-15*10-1,"Foco")
        pdf.drawString(columna1_x,inicio_tabla-25-15*11-1,"Lubricado")


        pdf.rect(columna1_x, 185 ,ancho_doc-30, 60)
        pdf.drawString(columna1_x,inicio_tabla-25-15*12-1,"Otro:")
        pdf.drawString(columna1_x,inicio_tabla-15-15*14-1,"Refacciones:")

        #Column splitters
        pdf.setStrokeColor(black)
        pdf.line(columna3_x-130,fila3_y-10*14+10,columna3_x-130, inicio_tabla-30-15*12)
        pdf.line(columna2_x-5,fila3_y-10*14+10,columna2_x-5, inicio_tabla-30-15*12)

        #Talón para pedal
        if pedal=="Pedal, ":
            pdf.setFont("Helvetica-Bold",24)
            pdf.drawString(columna2_x,inicio_tabla-25-20*13-15,"Sin pedal")
        
        else:
            pdf.setStrokeColor(black)

            origen = 35
            inicio_talon=180
            final  = 545
            pdf.line(origen, inicio_talon,final,inicio_talon)
        
            pdf.setFont("Helvetica-Bold",16)
            pdf.drawString(columna3_x-5, inicio_talon-20,"Fecha: ")
            pdf.drawString(origen, inicio_talon-20,"No. Orden: ")
            pdf.drawString(columna3_x, inicio_talon-20*2, taller_domi)

            pdf.setFont("Helvetica",16)
            pdf.drawString(columna3_x+53, inicio_talon-20, fecha)
            pdf.drawString(columna1_x+100, inicio_talon-20, no_orden)
            
            pdf.setFont("Helvetica-Bold",20)
            pdf.rect(30,inicio_talon-46,columna2_x-35,46)
            pdf.drawString(columna1_x,inicio_talon -20*2,"Ficha: ")
            pdf.drawString(columna1_x+100,inicio_talon-20*2, ficha)       

            pdf.setFont("Helvetica-Bold",12)
            pdf.drawString(columna1_x,inicio_talon-20*3,"Equipo:")
            pdf.drawString(columna1_x,inicio_talon-20*3-15,"No. Serie:")
            pdf.drawString(columna1_x,inicio_talon-20*3-15*2,"Descripción:")
            pdf.drawString(columna1_x,inicio_talon-20*3-15*3,"Ramo:")
            pdf.drawString(columna1_x,inicio_talon-20*3-15*4,"Estado de recepción:")

            pdf.setFont("Helvetica",12)
            pdf.drawString(columna2_x,inicio_talon-20*3,equipo)
            pdf.drawString(columna2_x,inicio_talon-20*3-15,no_serie)
            pdf.drawString(columna2_x,inicio_talon-20*3-15*2,descripcion)
            pdf.drawString(columna2_x,inicio_talon-20*3-15*3,casero + industrial + costura + sobrehiladora + otro_tipo)
            pdf.setFont("Helvetica",10)
            pdf.drawString(columna2_x,inicio_talon-20*3-15*4,"Le falta: "+aguja+bobina+carretel+devanador+estuche+foco+motor+banda+pedal+pie+hilo+abierta+tapa+otro_piezas)

            pdf.line(origen, inicio_talon-20*3-15*5,final,inicio_talon-20*3-15*5)

        #Final del documento
        pdf.save()

    def print_function(self):
        self.popup2 = tk.Toplevel(self.tabs)
        self.popup2.title("Orden de trabajo")
        self.popup2.geometry("450x100+300+300")
        
        label = tk.Label(self.popup2, text="Asegurate de haber guardado los datos.",font="Arial,24")
        label.grid(row=0,column=1)
        label2=tk.Label(self.popup2, text = "¿Quieres imprimir el documento guardado?")
        label2.grid(row=1,column=1)

        btn_print = ttk.Button(self.popup2, text="Imprimir", command=self.print_button)
        btn_print.grid(row=3,column=0)

        btn_see_file = ttk.Button(self.popup2, text="Ver archivo", command=self.open_file_path)
        btn_see_file.grid(row=3,column=1)

        btn_cancel = ttk.Button(self.popup2, text="Cancelar", command=self.popup2.destroy)
        btn_cancel.grid(row=3,column=2)

    def print_button(self):
    #Función de impresión modificada para tickets
    
    # 1. Generar ticket en lugar de PDF
        archivo_txt = self.update_pdf_document()
    
    # 2. Determinar sistema operativo
        op_sys = platform.system()
    
        if op_sys == "Windows":
            # Para Windows - imprime el archivo TXT
            try:
                command = f'Start-Process -FilePath "{archivo_txt}" -Verb Print'
                output = subprocess.check_output(
                    ["powershell", command], 
                    stderr=subprocess.STDOUT, 
                    universal_newlines=True
                )
                
            except subprocess.CalledProcessError as e:
                popup = tk.Toplevel(self.tabs)
                popup.title("Error en Windows")
                popup.geometry("500x200+300+300")
                
                error_msg = f"Error al imprimir en Windows:\n\n"
                error_msg += f"Código: {e.returncode}\n"
                if e.output:
                    error_msg += f"Mensaje: {e.output[:200]}\n"
                
                error_msg += "\nSolución alternativa:\n"
                error_msg += "1. Abre el archivo TICKET.txt manualmente\n"
                error_msg += "2. Usa Ctrl+P para imprimir\n"
                error_msg += "3. Selecciona tu impresora térmica"
                
                label = tk.Label(popup, text=error_msg, font=("Arial", 10), justify="left")
                label.pack(pady=20, padx=10)
                
                btn_close = ttk.Button(popup, text="Cerrar", command=popup.destroy)
                btn_close.pack()
        
        elif op_sys == "Linux":
            # Para Linux - enviar directamente a /dev/usb/lp0
            try:
                # Verificar que el archivo existe
                if not os.path.exists(archivo_txt):
                    raise FileNotFoundError(f"Archivo no encontrado: {archivo_txt}")
                
                # Leer contenido del ticket
                with open(archivo_txt, 'rb') as f:
                    ticket_data = f.read()
                
                # Enviar a impresora térmica
                with open('/dev/usb/lp0', 'wb') as impresora:
                    impresora.write(ticket_data)
                
                # Mensaje de éxito
                print("Ticket impreso exitosamente en Linux")
                
                # Opcional: mostrar popup de éxito
                success_popup = tk.Toplevel(self.tabs)
                success_popup.title("Éxito")
                success_popup.geometry("300x100+400+400")
                label = tk.Label(success_popup, text="✅ Ticket impreso correctamente", 
                            font=("Arial", 12))
                label.pack(pady=30)
                success_popup.after(2000, success_popup.destroy)  # Cerrar automáticamente
                
            except PermissionError:
                popup = tk.Toplevel(self.tabs)
                popup.title("Error de permisos")
                popup.geometry("400x150+300+300")
                label = tk.Label(popup, 
                            text="Permiso denegado para /dev/usb/lp0\n\n" +
                                    "Ejecuta en terminal:\n" +
                                    "sudo chmod 666 /dev/usb/lp0\n\n" +
                                    "Luego reintenta la impresión.",
                            font=("Arial", 12))
                label.pack(pady=20)
                btn_close = ttk.Button(popup, text="Cerrar", command=popup.destroy)
                btn_close.pack()
                
            except FileNotFoundError as e:
                popup = tk.Toplevel(self.tabs)
                popup.title("Error")
                popup.geometry("400x100+300+300")
                label = tk.Label(popup, text=str(e), font=("Arial", 12))
                label.pack(pady=20)
                btn_close = ttk.Button(popup, text="Cerrar", command=popup.destroy)
                btn_close.pack()
                
            except Exception as e:
                popup = tk.Toplevel(self.tabs)
                popup.title("Error inesperado")
                popup.geometry("400x150+300+300")
                label = tk.Label(popup, text=f"Error: {str(e)}", font=("Arial", 12))
                label.pack(pady=20)
                btn_close = ttk.Button(popup, text="Cerrar", command=popup.destroy)
                btn_close.pack()
        
        else:
            popup = tk.Toplevel(self.tabs)
            popup.title("Sistema no compatible")
            popup.geometry("400x100+300+300")
            label = tk.Label(popup, text="Sistema operativo no compatible", 
                        font=("Arial", 12))
            label.pack(pady=20)
            btn_close = ttk.Button(popup, text="Cerrar", command=popup.destroy)
            btn_close.pack()
        
        # 3. Cerrar popup2 si existe
        if hasattr(self, 'popup2'):
            self.popup2.destroy()    


        # self.update_pdf_document()
        
        # archivo = os.path.join(os.getcwd(),"Ordenes_de_Trabajo","Orden_no_"+ str(self.counter) + ".pdf")
        # if op_sys == "Windows":
        #     archivo_file = open(archivo, "rb")
        #     command = "Start-Process -FilePath " + '\"' + archivo +'\"' + " -Verb Print"

        #     try:
        #         output = subprocess.check_output(["powershell", command], stderr=subprocess.STDOUT, universal_newlines=True)
        #     except subprocess.CalledProcessError as e:
        #         popup = tk.Toplevel(self.tabs)
        #         popup.title("Orden de trabajo")
        #         popup.geometry("400x100+300+300")
        #         texterr="Error, No se encuentra la impresora " + e
        #         label = tk.Label(popup, text=texterr,font="Arial,24")
        #         label.pack(pady=20)

        #         btn_close = ttk.Button(popup, text="Cerrar", command=popup.destroy)
        #         btn_close.pack()

        # elif op_sys == "Linux":
        #     archivo_txt2 = os.path.join(os.getcwd(), "TEST_TEXT.txt")

        #     archivo_txt2 = os.path.join(os.getcwd(), "TEST_TEXT.txt")
        #     try:
        #         # Verificar que el archivo existe
        #         if not os.path.exists(archivo_txt2):
        #             raise FileNotFoundError(f"Archivo TXT no encontrado: {archivo_txt2}")
                
        #         # Verificar que la impresora existe
        #         if not os.path.exists('/dev/usb/lp0'):
        #             raise Exception("Impresora no detectada en /dev/usb/lp0")
                
        #         # Leer archivo TXT
        #         with open(archivo_txt2, 'r', encoding='utf-8') as f:
        #             contenido = f.read()
                
        #         # Preparar datos para impresión
        #         datos = bytearray()
        #         datos.extend(b'\x1B\x40')  # Inicializar impresora
        #         datos.extend(b'\x1B\x0F')  # Modo condensado
                
        #         # Dividir en líneas de máximo 48 caracteres
        #         lineas = contenido.split('\n')
        #         for linea in lineas:
        #             while len(linea) > 48:
        #                 datos.extend(linea[:48].encode('ascii', errors='ignore'))
        #                 datos.extend(b'\n')
        #                 linea = linea[48:]
        #             if linea:
        #                 datos.extend(linea.encode('ascii', errors='ignore'))
        #             datos.extend(b'\n')
                
        #         # Finalizar
        #         datos.extend(b'\n\n\n\n\x1D\x56\x00')  # Avanzar 4 líneas y cortar
                
        #         # Escribir a impresora
        #         with open('/dev/usb/lp0', 'wb') as impresora:
        #             impresora.write(datos)
                
        #         print("Impresión exitosa en Linux")
                
        #     except FileNotFoundError as e:
        #         popup = tk.Toplevel(self.tabs)
        #         popup.title("Archivo no encontrado")
        #         popup.geometry("400x100+300+300")
        #         label = tk.Label(popup, text=str(e), font=("Arial", 12))
        #         label.pack(pady=20)
        #         btn_close = ttk.Button(popup, text="Cerrar", command=popup.destroy)
        #         btn_close.pack()
            
        #     except PermissionError as e:
        #         popup = tk.Toplevel(self.tabs)
        #         popup.title("Error de permisos")
        #         popup.geometry("400x150+300+300")
        #         label = tk.Label(popup, text=f"Permiso denegado para /dev/usb/lp0\n\nEjecuta:\nsudo chmod 666 /dev/usb/lp0", font=("Arial", 12))
        #         label.pack(pady=20)
        #         btn_close = ttk.Button(popup, text="Cerrar", command=popup.destroy)
        #         btn_close.pack()
            
        #     except Exception as e:
        #         popup = tk.Toplevel(self.tabs)
        #         popup.title("Error en Linux")
        #         popup.geometry("400x150+300+300")
        #         label = tk.Label(popup, text=f"Error: {str(e)}", font=("Arial", 12))
        #         label.pack(pady=20)
        #         btn_close = ttk.Button(popup, text="Cerrar", command=popup.destroy)
        #         btn_close.pack()
        # else:
        #     popup = tk.Toplevel(self.tabs)
        #     popup.title("Orden de trabajo")
        #     popup.geometry("400x100+300+300")
            
        #     label = tk.Label(popup, text="Esta aplicación no esta habilitada para otros OS",font="Arial,24")
        #     label.pack(pady=20)

        #     btn_close = ttk.Button(popup, text="Cerrar", command=popup.destroy)
        
        # self.popup2.destroy()
      
    def open_file_path(self):
        self.update_pdf_document()
        
        archivo = os.path.join(os.getcwd(),"Ordenes_de_Trabajo", "Orden_no_"+ str(self.counter) + ".pdf")
        if platform.system() == "Windows":
            subprocess.Popen(f'explorer.exe /select,"{str(archivo)}"')
        elif platform.system() == "Linux":
            subprocess.Popen(['xdg-open', os.path.dirname(archivo)])
        self.popup2.destroy()
            
    #Tabs
    def mytabs(self):
        # Tabs creation
        tab1 = ttk.Frame(self.tabs)
        tab2 = ttk.Frame(self.tabs)

        # Tabs calling functions
        self.tab_work_order(tab1)
        self.tab_sales_sheet(tab2)

        # Add tabs to the window
        self.tabs.grid(row=0, column=0, sticky="nsew")
        
    def tab_work_order(self, tab):
        #Tab creation
        global counter, label
        self.tabs.add(tab, text="Orden de trabajo")

        #Section 1 data
        title1= ttk.Label(tab, text="Datos del cliente", font="Arial, 18")
        title1.grid(row=0, column=0, columnspan=9, padx=10, pady=5)

        #Separator
        line1 = ttk.Separator(tab, orient="horizontal")
        line1.grid(row=1,column=0, columnspan=9, sticky="ew")

        #Empty label
        empty1=tk.Label(tab, text= "")
        empty1.grid(row=1, column=0, padx=0, pady=0, sticky="e")

        #Name
        name_text = tk.Label(tab, text ="Nombre: ",font="Arial, 14")
        name_text.grid(row=2, column=0, padx=0, pady=0, sticky="e")

        self.name_entry = tk.Entry(tab,width=40)
        self.name_entry.grid(row=2, column=1, padx=0, pady=0)

        #Phone number1
        phone1_text = tk.Label(tab, text ="Teléfono: ",font="Arial, 14")
        phone1_text.grid(row=3, column=0, padx=0, pady=0, sticky="e")

        self.phone1_entry = tk.Entry(tab,width=40)
        self.phone1_entry.grid(row=3, column=1, padx=0, pady=0)

        #Phone number2
        phone2_text = tk.Label(tab, text ="Teléfono2: ",font="Arial, 14")
        phone2_text.grid(row=4, column=0, padx=0, pady=0, sticky="e")

        self.phone2_entry = tk.Entry(tab,width=40)
        self.phone2_entry.grid(row=4, column=1, padx=0, pady=0)

        #Directions
        adress_text = tk.Label(tab, text ="Dirección: ",font="Arial, 14")
        adress_text.grid(row=5, column=0, padx=0, pady=0, sticky="e")

        self.adress_entry = tk.Entry(tab,width=40)
        self.adress_entry.grid(row=5, column=1, padx=0, pady=0)

        #Notes
        notes_text = tk.Label(tab, text ="Diagnostico: ",font="Arial, 14")
        notes_text.grid(row=6, column=0, padx=0, pady=0, sticky="e")

        self.notes_entry = tk.Entry(tab,width=40)
        self.notes_entry.grid(row=6, column=1, padx=0, pady=0)

        #Separator
        line2 = ttk.Separator(tab, orient="horizontal")
        line2.grid(row=7,column=0, columnspan=9, sticky="ew")

        #Empty label
        empty2=tk.Label(tab, text= "")
        empty2.grid(row=8, column=0, padx=0, pady=0, sticky="e")
        
        #Section 2 data
        title1= ttk.Label(tab, text="Datos del equipo", font="Arial, 18")
        title1.grid(row=9, column=0, columnspan=9, padx=10, pady=5)

        #Equipment name
        equip_text = tk.Label(tab, text ="Equipo: ",font="Arial, 14")
        equip_text.grid(row=10, column=0, padx=0, pady=0, sticky="e")

        self.equip_entry = tk.Entry(tab,width=40)
        self.equip_entry.grid(row=10, column=1, padx=0, pady=0)

        #Serial number
        serial_text = tk.Label(tab, text ="No. Serie: ",font="Arial, 14")
        serial_text.grid(row=11, column=0, padx=0, pady=0, sticky="e")

        self.serial_entry = tk.Entry(tab,width=40)
        self.serial_entry.grid(row=11, column=1, padx=0, pady=0)

        #Description
        descrip_text = tk.Label(tab, text ="Descripción: ",font="Arial, 14")
        descrip_text.grid(row=12, column=0, padx=0, pady=0, sticky="e")

        self.desc_entry = tk.Entry(tab,width=40)
        self.desc_entry.grid(row=12, column=1, padx=0, pady=0)

        #Separator
        line3 = ttk.Separator(tab, orient="horizontal")
        line3.grid(row=13,column=0, columnspan=9, sticky="ew")

        check_text = tk.Label(tab, text="Chequeo\t", font="Arial, 18")
        check_text.grid(row=14, column=0, columnspan=9, padx=0, pady=5)

        #Checklist
        self.chkbx1_var = tk.StringVar()
        self.chkbx1 = ttk.Checkbutton(tab, text="Aguja\t\t", variable=self.chkbx1_var)
        self.chkbx1.grid(row=15, column=0,padx=20)

        self.chkbx2_var = tk.StringVar()
        self.chkbx2 = ttk.Checkbutton(tab, text="Bobina\t\t", variable=self.chkbx2_var)
        self.chkbx2.grid(row=16, column=0)

        self.chkbx3_var = tk.StringVar()
        self.chkbx3 = ttk.Checkbutton(tab, text="Carretel\t\t", variable=self.chkbx3_var).grid(row=17, column=0)

        self.chkbx4_var = tk.StringVar()
        self.chkbx4 = ttk.Checkbutton(tab, text="Devanador\t", variable=self.chkbx4_var).grid(row=18, column=0)
        
        self.chkbx5_var = tk.StringVar()
        self.chkbx5 = ttk.Checkbutton(tab, text="Estuche/bolsa\t", variable=self.chkbx5_var).grid(row=19, column=0)

        self.chkbx6_var = tk.StringVar()
        self.chkbx6 = ttk.Checkbutton(tab, text="Foco\t\t", variable=self.chkbx6_var).grid(row=20, column=0)

        self.chkbx7_var = tk.StringVar()
        self.chkbx7 = ttk.Checkbutton(tab, text="Motor\t\t", variable=self.chkbx7_var).grid(row=15, column=1)

        self.chkbx8_var = tk.StringVar()
        self.chkbx8 = ttk.Checkbutton(tab, text="Banda\t\t", variable=self.chkbx8_var).grid(row=16, column=1)

        self.chkbx9_var = tk.StringVar()
        self.chkbx9 = ttk.Checkbutton(tab, text="Pedal\t\t", variable=self.chkbx9_var).grid(row=17, column=1)

        self.chkbx10_var = tk.StringVar()
        self.chkbx10 = ttk.Checkbutton(tab, text="Pie\t\t", variable=self.chkbx10_var).grid(row=18, column=1)

        self.chkbx11_var = tk.StringVar()
        self.chkbx11 = ttk.Checkbutton(tab, text="Hilo\t\t", variable=self.chkbx11_var).grid(row=19, column=1)

        #Branch type of equipment
        self.chkbx12_var = tk.StringVar()
        self.chkbx12 = ttk.Checkbutton(tab, text="Casero\t\t", variable=self.chkbx12_var).grid(row=15, column=2)

        self.chkbx13_var = tk.StringVar()
        self.chkbx13 = ttk.Checkbutton(tab, text="Industrial\t", variable=self.chkbx13_var).grid(row=16, column=2)

        self.chkbx14_var = tk.StringVar()
        self.chkbx14 = ttk.Checkbutton(tab, text="Costura\t\t", variable=self.chkbx14_var).grid(row=18, column=2)

        self.chkbx15_var = tk.StringVar()
        self.chkbx15 = ttk.Checkbutton(tab, text="Sobrehiladora\t", variable=self.chkbx15_var).grid(row=19, column=2)

        self.chkbx16_var = tk.StringVar()
        self.chkbx16 = ttk.Checkbutton(tab, text="Abierta\t\t",variable=self.chkbx16_var).grid(row=21,column=0)

        self.chkbx17_var = tk.StringVar()
        self.chkbx17 = ttk.Checkbutton(tab, text="TapaFrontal\t",variable=self.chkbx17_var).grid(row=22,column=0)
        
        #other equipment
        other_equip_text = tk.Label(tab, text ="Otro: ")
        other_equip_text.grid(row=20, column=1, padx=0, pady=0, sticky="e")

        self.other_equip_entry = tk.Entry(tab,width=10)
        self.other_equip_entry.grid(row=20, column=2, padx=0, pady=0)

        #Other data
        self.other_text = tk.Label(tab, text ="Otros:")
        self.other_text.grid(row=20, column=0, padx=0, pady=0, sticky="ne")

        self.other_entry = tk.Entry(tab, width=20)
        self.other_entry.grid(row=20, column=1, padx=0, pady=0)
        
        #Turn label
        turn_text = tk.Label(tab, text ="  Ficha:",font="Arial, 24")
        turn_text.grid(row=2, column=5, padx=0, pady=0, sticky="ne")

        self.turn_entry = tk.Entry(tab, width=3,font=("Arial", 24))
        self.turn_entry.grid(row=2, column=6, padx=0, pady=0)
        
        #Empty label
        empty3=tk.Label(tab, text= "")
        empty3.grid(row=5, column=5, padx=0, pady=0, sticky="e")

        #Products/Services
        product1_text = tk.Label(tab, text="Servicio", font="Arial, 18")
        product1_text.grid(row=14, column=6, columnspan=9, padx=0, pady=5)

        self.desc_text = tk.Label(tab, text="Descripción", font="Arial, 10")
        self.desc_text.grid(row=15, column=5, columnspan=9, padx=0, pady=5)

        quant_text = tk.Label(tab, text="Costo", font="Arial, 10")
        quant_text.grid(row=15, column=7, columnspan=9, padx=0, pady=5)

        #List of products/services        
        self.entry1= tk.Entry(tab, width=18,font=("Arial", 9, "bold"))
        self.entry1.grid(row=17, column= 6)
        self.entry2= tk.Entry(tab, width=18,font=("Arial", 9, "bold"))
        self.entry2.grid(row=18, column= 6)
        self.entry3= tk.Entry(tab, width=18,font=("Arial", 9, "bold"))
        self.entry3.grid(row=19, column= 6)
        self.entry4= tk.Entry(tab, width=18,font=("Arial", 9, "bold"))
        self.entry4.grid(row=20, column= 6)

        self.entries5 = tk.Entry(tab, width=7, font=("Arial", 9, "bold"))
        self.entries5.grid(row = 17, column=7)
        self.entries6 = tk.Entry(tab, width=7, font=("Arial", 9, "bold"))
        self.entries6.grid(row = 18, column=7)
        self.entries7 = tk.Entry(tab, width=7, font=("Arial", 9, "bold"))
        self.entries7.grid(row = 19, column=7)
        self.entries8 = tk.Entry(tab, width=7, font=("Arial", 9, "bold"))
        self.entries8.grid(row = 20, column=7)
        
        #Location checkbox
        self.Domicilio_var=tk.IntVar()
        Domicilio = ttk.Checkbutton(tab, text="Domicilio\t",variable=self.Domicilio_var)
        Domicilio.grid(row=9, column=6)

        #Order number
        self.order_text = tk.Label(tab, text="No. orden: ", font= "Arial,18")
        self.order_text.grid(row=4,column=5)

        counter = self.counter
        label = tk.Label(tab, text=str(counter), font= "Arial,18")
        label.grid(row=4,column=6)

        #Date
        date_text = tk.Label(tab, text="Fecha: ", font= "Arial,18")
        date_text.grid(row=5,column=5)

        self.date_entry = tk.Entry(tab,font="Arial,18",width=13)
        self.date_entry.insert(0,date_format)
        self.date_entry.grid(row=5,column=6)

        #Save button
        save_btn = tk.Button(tab, text="Guardar",command=self.save_and_load)
        save_btn.grid(row=10,column=7)

        #Print button
        print_btn = tk.Button(tab, text="Imprimir",command=self.print_function)
        print_btn.grid(row=10,column=6)

        #New button
        new_btn = tk.Button(tab, text="Nueva ODT",command=self.new_odt_button)
        new_btn.grid(row=10,column=5)

        #Empty label
        empty4=tk.Label(tab, text= "  ")
        empty4.grid(row=6, column=8, padx=0, pady=0, sticky="e")

    def tab_sales_sheet(self, tab):
        self.tabs.add(tab, text="Hoja de Ventas")
    
    def tab_product_list(self, tab):
        self.tabs.add(tab, text="Lista de prouctos")

#--------------Start program--------------

#Main variables
today_date = datetime.date.today()
date_format = today_date.strftime("%d - %m - %Y")
op_sys = platform.system()
op_ver = platform.version()
fileWO = os.path.join(os.getcwd(), "Registro Ordenes de Trabajo.csv")
        
#Tk
window = tk.Tk()
tabs = ttk.Notebook(window)

#Calling main functions
main_menu().format()
alltabs(tabs).mytabs()

#Print window
window.mainloop()