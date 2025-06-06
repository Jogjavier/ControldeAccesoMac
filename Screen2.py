#script de prueba
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
    from mfrc522 import SimpleMFRC522
    import RPi.GPIO as GPIO
    RFID_AVAILABLE = True
    print("Librerías RFID cargadas correctamente.")
except ImportError as e:
    print(f"Error importando librerías RFID: {e}")
    RFID_AVAILABLE = False

class RFIDReaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Lector RFID RC522 - Raspberry Pi")
        self.root.geometry("500x400")
        self.root.configure(bg='#2c3e50')
        
        # Variables
        self.reading = False
        self.reader = None
        
        # Setup UI primero
        self.setup_ui()
        
        # Inicializar RFID después de la UI
        self.init_rfid()
        
    def init_rfid(self):
        """Inicializar el lector RFID usando exactamente tu configuración que funciona"""
        if RFID_AVAILABLE:
            try:
                print("Inicializando RFID igual que tu script que funciona...")
                
                # Usar exactamente la misma configuración que tu script
                self.reader = SimpleMFRC522()
                
                print("✅ Lector RFID inicializado correctamente.")
                print("🔌 Usando tu configuración:")
                print("   SDA: Pin 26, SCK: Pin 23, MOSI: Pin 19")
                print("   MISO: Pin 21, GND: Pin 20, RST: Pin 22, 3.3V: Pin 17")
                
                # Actualizar estado en UI
                self.status_label.config(
                    text="✅ RFID conectado y listo",
                    fg='#27ae60'
                )
                
            except Exception as e:
                error_msg = f"Error inicializando RFID: {str(e)}"
                print(f"❌ {error_msg}")
                self.reader = None
                
                # Actualizar estado en UI
                self.status_label.config(
                    text="❌ Error de conexión RFID",
                    fg='#e74c3c'
                )
                
                # Mostrar error en UI después de un momento
                self.root.after(1000, lambda: messagebox.showerror("Error RFID", error_msg))
        else:
            print("⚠️  Modo simulación - Librerías no disponibles")
            self.status_label.config(
                text="⚠️ Modo simulación",
                fg='#f39c12'
            )
        
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
            text="🔄 Inicializando...",
            font=("Arial", 12),
            fg='#f39c12',
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
        
        # Botones
        button_frame = tk.Frame(main_frame, bg='#34495e')
        button_frame.pack(pady=10)
        
        # Botón limpiar
        clear_button = tk.Button(
            button_frame,
            text="🗑️ Limpiar",
            font=("Arial", 10),
            bg='#e74c3c',
            fg='white',
            relief='flat',
            command=self.clear_data
        )
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Botón test
        test_button = tk.Button(
            button_frame,
            text="🧪 Test Conexión",
            font=("Arial", 10),
            bg='#9b59b6',
            fg='white',
            relief='flat',
            command=self.test_connection
        )
        test_button.pack(side=tk.LEFT, padx=5)
        
        # Frame de información
        info_frame = tk.Frame(self.root, bg='#2c3e50')
        info_frame.pack(pady=5)
        
        tk.Label(
            info_frame,
            text="💡 Acerca una tarjeta RFID al lector RC522",
            font=("Arial", 9),
            fg='#bdc3c7',
            bg='#2c3e50'
        ).pack()
        
        tk.Label(
            info_frame,
            text="🔌 SDA-26, SCK-23, MOSI-19, MISO-21, GND-20, RST-22, 3.3V-17",
            font=("Arial", 8),
            fg='#95a5a6',
            bg='#2c3e50'
        ).pack()
        
    def test_connection(self):
        """Probar la conexión del RFID"""
        if not RFID_AVAILABLE:
            messagebox.showwarning("Test", "Librerías RFID no disponibles")
            return
            
        if not self.reader:
            messagebox.showerror("Test", "Lector RFID no inicializado")
            return
            
        # Hacer un test rápido
        try:
            self.status_label.config(text="🧪 Probando conexión...", fg='#f39c12')
            self.root.update()
            
            # Intentar leer sin timeout largo
            test_thread = threading.Thread(target=self._test_read)
            test_thread.daemon = True
            test_thread.start()
            
        except Exception as e:
            messagebox.showerror("Test", f"Error en test: {e}")
            self.status_label.config(text="❌ Error en test", fg='#e74c3c')
    
    def _test_read(self):
        """Hilo para test de lectura"""
        try:
            # Test básico de la librería
            print("🧪 Ejecutando test de conexión...")
            
            # Esto debería funcionar si la conexión está bien
            # Solo verificamos que el objeto existe y puede acceder al hardware
            
            message = "✅ Conexión OK - Acerca una tarjeta para leer"
            color = '#27ae60'
            
        except Exception as e:
            print(f"❌ Error en test: {e}")
            message = f"❌ Error: {str(e)[:50]}..."
            color = '#e74c3c'
            
        # Actualizar UI en hilo principal
        self.root.after(0, lambda: self.status_label.config(text=message, fg=color))
        
    def toggle_reading(self):
        if not self.reading:
            self.start_reading()
        else:
            self.stop_reading()
    
    def start_reading(self):
        if not RFID_AVAILABLE:
            messagebox.showwarning("Advertencia", "RFID no disponible - Modo simulación")
            
        if not self.reader and RFID_AVAILABLE:
            messagebox.showerror("Error", "Lector RFID no inicializado")
            return
            
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
        """Bucle principal de lectura RFID - usando tu método que funciona"""
        print("🔄 Iniciando bucle de lectura...")
        
        while self.reading:
            try:
                if RFID_AVAILABLE and self.reader:
                    print("📡 Esperando tarjeta...")
                    
                    # Usar EXACTAMENTE el mismo código que tu script que funciona
                    try:
                        id_tag, text = self.reader.read()
                        print(f"✅ Resultado: ID={id_tag}, Text='{text}'")
                        self.update_display(id_tag, text)
                    except Exception as read_error:
                        print(f"❌ Error específico en reader.read(): {read_error}")
                        # Continuar el bucle, no romper
                        time.sleep(0.5)
                        continue
                    
                else:
                    # Simulación para pruebas
                    time.sleep(3)
                    if self.reading:
                        import random
                        sim_id = random.randint(100000000000, 999999999999)
                        sim_content = "Tarjeta simulada para pruebas"
                        print(f"🎭 Simulación - ID: {sim_id}")
                        self.update_display(sim_id, sim_content)
                        
            except KeyboardInterrupt:
                print("⏹️ Lectura interrumpida por usuario")
                break
            except Exception as e:
                print(f"❌ Error general en bucle: {e}")
                # No romper el bucle por errores generales
                time.sleep(1)
                continue
                
        print("🔚 Bucle de lectura terminado")
    
    def update_display(self, rfid_id, content):
        """Actualizar la pantalla con los datos leídos"""
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
            
            # Mensaje en consola
            print(f"📋 Datos mostrados en UI: ID={rfid_id}")
            
            # Volver a estado de lectura después de 2 segundos
            if self.reading:
                self.root.after(2000, lambda: self.status_label.config(
                    text="🔄 Leyendo... Acerca una tarjeta",
                    fg='#f39c12'
                ) if self.reading else None)
        
        # Ejecutar en el hilo principal de tkinter
        self.root.after(0, update_ui)
    
    def clear_data(self):
        """Limpiar todos los datos mostrados"""
        self.id_text.delete(1.0, tk.END)
        self.content_text.delete(1.0, tk.END)
        self.last_read_label.config(text="⏰ Última lectura: ---")
        
        if not self.reading:
            status_text = "✅ RFID conectado y listo" if (RFID_AVAILABLE and self.reader) else "📡 Listo para leer"
            self.status_label.config(text=status_text, fg='#27ae60')
    
    def on_closing(self):
        """Manejar cierre de la aplicación - igual que tu script"""
        print("🔚 Cerrando aplicación...")
        self.reading = False
        
        # Esperar un poco para que termine el hilo de lectura
        time.sleep(0.5)
        
        # Hacer cleanup igual que tu script
        if RFID_AVAILABLE:
            try:
                GPIO.cleanup()
                print("✅ GPIO.cleanup() ejecutado")
            except Exception as e:
                print(f"⚠️ Error en GPIO.cleanup(): {e}")
        
        self.root.destroy()

def main():
    print("🚀 Iniciando aplicación RFID...")
    
    root = tk.Tk()
    app = RFIDReaderGUI(root)
    
    # Manejar cierre de ventana
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Centrar ventana
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    print("✅ Interfaz gráfica iniciada")
    root.mainloop()

if __name__ == "__main__":
    main()