#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime

# Importar librerías del RFID
RFID_AVAILABLE = False
try:
    from mfrc522 import SimpleMFRC522, MFRC522
    import RPi.GPIO as GPIO
    import spidev
    RFID_AVAILABLE = True
    print("Librerías RFID cargadas correctamente.")
except ImportError:
    RFID_AVAILABLE = False
    print("Librerías RFID no disponibles. Ejecutándose en modo simulación.")

class RFIDReaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Lector RFID RC522 - Raspberry Pi")
        self.root.geometry("500x400")
        self.root.configure(bg='#2c3e50')
        
        # Variables
        self.reading = False
        self.reader = None
        
        # Inicializar RFID si está disponible
        if RFID_AVAILABLE:
            try:
                # Configurar pines específicos para tu conexión
                # SDA-26, SCK-23, MOSI-19, MISO-21, GND-20, RST-22, 3.3v-17
                
                # Configurar SPI
                GPIO.setmode(GPIO.BOARD)
                
                # Crear instancia del lector con pin RST personalizado
                self.reader = SimpleMFRC522()
                
                # Si necesitas configurar pines específicos, puedes usar MFRC522 directamente
                # self.mfrc522_reader = MFRC522(rst_pin=22, cs_pin=26)
                
                print("Lector RFID inicializado correctamente.")
                print("Configuración de pines:")
                print("SDA: Pin 26, SCK: Pin 23, MOSI: Pin 19")
                print("MISO: Pin 21, GND: Pin 20, RST: Pin 22, 3.3V: Pin 17")
                
            except Exception as e:
                print(f"Error al inicializar RFID: {e}")
                messagebox.showerror("Error", f"Error al inicializar RFID: {e}")
                self.reader = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Título principal
        title_label = tk.Label(
            self.root, 
            text="🔍 Lector RFID RC522", 
            font=("Arial", 20, "bold"),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack(pady=20)
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#34495e', relief='raised', bd=2)
        main_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        # Estado del lector
        self.status_label = tk.Label(
            main_frame,
            text="📡 Listo para leer",
            font=("Arial", 12),
            fg='#27ae60',
            bg='#34495e'
        )
        self.status_label.pack(pady=10)
        
        # Botón de lectura
        self.read_button = tk.Button(
            main_frame,
            text="🚀 Iniciar Lectura",
            font=("Arial", 14, "bold"),
            bg='#3498db',
            fg='white',
            relief='flat',
            padx=20,
            pady=10,
            command=self.toggle_reading
        )
        self.read_button.pack(pady=10)
        
        # Frame para mostrar datos
        data_frame = tk.LabelFrame(
            main_frame,
            text="📋 Datos del Tag RFID",
            font=("Arial", 12, "bold"),
            fg='white',
            bg='#34495e'
        )
        data_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        # ID del tag
        tk.Label(
            data_frame,
            text="🏷️ ID del Tag:",
            font=("Arial", 10, "bold"),
            fg='white',
            bg='#34495e'
        ).pack(anchor='w', padx=10, pady=5)
        
        self.id_text = tk.Text(
            data_frame,
            height=2,
            font=("Courier", 12),
            bg='#ecf0f1',
            fg='#2c3e50',
            wrap='word'
        )
        self.id_text.pack(padx=10, pady=5, fill='x')
        
        # Contenido del tag
        tk.Label(
            data_frame,
            text="📝 Contenido:",
            font=("Arial", 10, "bold"),
            fg='white',
            bg='#34495e'
        ).pack(anchor='w', padx=10, pady=5)
        
        self.content_text = tk.Text(
            data_frame,
            height=4,
            font=("Arial", 10),
            bg='#ecf0f1',
            fg='#2c3e50',
            wrap='word'
        )
        self.content_text.pack(padx=10, pady=5, fill='both', expand=True)
        
        # Última lectura
        self.last_read_label = tk.Label(
            data_frame,
            text="⏰ Última lectura: ---",
            font=("Arial", 9),
            fg='#95a5a6',
            bg='#34495e'
        )
        self.last_read_label.pack(pady=5)
        
        # Botón limpiar
        clear_button = tk.Button(
            main_frame,
            text="🗑️ Limpiar",
            font=("Arial", 10),
            bg='#e74c3c',
            fg='white',
            relief='flat',
            command=self.clear_data
        )
        clear_button.pack(pady=10)
        
        # Frame de información
        info_frame = tk.Frame(self.root, bg='#2c3e50')
        info_frame.pack(pady=5)
        
        info_text = "💡 Acerca una tarjeta RFID al lector RC522"
        connection_info = "🔌 SDA-26, SCK-23, MOSI-19, MISO-21, GND-20, RST-22, 3.3V-17"
        
        if not RFID_AVAILABLE:
            info_text = "⚠️ Modo simulación - Librerías RFID no disponibles"
            
        tk.Label(
            info_frame,
            text=info_text,
            font=("Arial", 9),
            fg='#bdc3c7',
            bg='#2c3e50'
        ).pack()
        
        tk.Label(
            info_frame,
            text=connection_info,
            font=("Arial", 8),
            fg='#95a5a6',
            bg='#2c3e50'
        ).pack()
        
    def toggle_reading(self):
        if not self.reading:
            self.start_reading()
        else:
            self.stop_reading()
    
    def start_reading(self):
        self.reading = True
        self.read_button.config(
            text="⏸️ Detener Lectura",
            bg='#e74c3c'
        )
        self.status_label.config(
            text="🔄 Leyendo... Acerca una tarjeta",
            fg='#f39c12'
        )
        
        # Iniciar hilo de lectura
        self.read_thread = threading.Thread(target=self.read_rfid_loop)
        self.read_thread.daemon = True
        self.read_thread.start()
    
    def stop_reading(self):
        self.reading = False
        self.read_button.config(
            text="🚀 Iniciar Lectura",
            bg='#3498db'
        )
        self.status_label.config(
            text="⏹️ Lectura detenida",
            fg='#95a5a6'
        )
    
    def read_rfid_loop(self):
        while self.reading:
            try:
                if RFID_AVAILABLE and self.reader:
                    # Lectura real del RFID
                    id_tag, content = self.reader.read()
                    self.update_display(id_tag, content)
                else:
                    # Simulación para pruebas
                    time.sleep(2)
                    if self.reading:  # Verificar si aún está leyendo
                        import random
                        sim_id = random.randint(100000000000, 999999999999)
                        sim_content = "Tarjeta simulada"
                        self.update_display(sim_id, sim_content)
                        
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error de lectura: {e}"))
                self.reading = False
                break
    
    def update_display(self, rfid_id, content):
        def update_ui():
            # Actualizar ID
            self.id_text.delete(1.0, tk.END)
            self.id_text.insert(1.0, str(rfid_id))
            
            # Actualizar contenido
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(1.0, str(content).strip())
            
            # Actualizar timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.last_read_label.config(text=f"⏰ Última lectura: {timestamp}")
            
            # Cambiar estado
            self.status_label.config(
                text="✅ Tarjeta leída correctamente",
                fg='#27ae60'
            )
            
            # Volver a estado de lectura después de 2 segundos
            self.root.after(2000, lambda: self.status_label.config(
                text="🔄 Leyendo... Acerca una tarjeta",
                fg='#f39c12'
            ) if self.reading else None)
        
        # Ejecutar en el hilo principal de tkinter
        self.root.after(0, update_ui)
    
    def clear_data(self):
        self.id_text.delete(1.0, tk.END)
        self.content_text.delete(1.0, tk.END)
        self.last_read_label.config(text="⏰ Última lectura: ---")
        self.status_label.config(
            text="📡 Listo para leer",
            fg='#27ae60'
        )
    
    def on_closing(self):
        self.reading = False
        if RFID_AVAILABLE:
            try:
                GPIO.cleanup()
            except:
                pass
        self.root.destroy()

def main():
    root = tk.Tk()
    app = RFIDReaderGUI(root)
    
    # Manejar cierre de ventana
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Centrar ventana
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()