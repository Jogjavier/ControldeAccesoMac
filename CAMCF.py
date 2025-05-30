import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
import time

# Importaciones para RFID
try:
    from mfrc522 import SimpleMFRC522
    import RPi.GPIO as GPIO
    RFID_AVAILABLE = True
except ImportError:
    RFID_AVAILABLE = False
    print("Advertencia: No se pudo importar la librería RFID. Funcionará en modo simulación.")

class RegistroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Laboratorio de MAC")
        self.root.geometry("800x600")
        self.root.configure(bg="#f5e0e0")
        self.logo = tk.PhotoImage(file="logo.png")
        self.datos = {}
        
        # Inicializar RFID
        if RFID_AVAILABLE:
            try:
                self.reader = SimpleMFRC522()
                self.rfid_active = True
            except Exception as e:
                print(f"Error inicializando RFID: {e}")
                self.rfid_active = False
        else:
            self.rfid_active = False
        
        self.reading_rfid = False
        self.pantalla_principal()

    def limpiar_pantalla(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def pantalla_principal(self):
        self.limpiar_pantalla()
        tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
        tk.Label(self.root, text="Laboratorio de MAC", font=("Arial", 24, "bold"), fg="#1d127a", bg="#f5e0e0").pack(pady=100)
        tk.Label(self.root, text="Aproximar Tarjeta", font=("Arial", 18), fg="#1d127a", bg="#f5e0e0").pack()
        self.rfid_entry = tk.Entry(self.root, font=("Arial", 18), justify='center')
        self.rfid_entry.pack(pady=20)
        tk.Button(self.root, text="Continuar", font=("Arial", 16, "bold"), fg="white", bg="#1d127a", command=self.validar_rfid).pack(pady=20)
        
        # Iniciar lectura automática de RFID
        if self.rfid_active:
            self.start_rfid_reading()

    def start_rfid_reading(self):
        """Inicia la lectura automática de RFID en un hilo separado"""
        if not self.reading_rfid and self.rfid_active:
            self.reading_rfid = True
            threading.Thread(target=self.read_rfid_continuously, daemon=True).start()

    def stop_rfid_reading(self):
        """Detiene la lectura automática de RFID"""
        self.reading_rfid = False

    def read_rfid_continuously(self):
        """Lee continuamente las tarjetas RFID"""
        while self.reading_rfid:
            try:
                if self.rfid_active:
                    # Leer RFID con timeout
                    id, text = self.reader.read_no_block()
                    if id:
                        # Actualizar la entrada de RFID en el hilo principal
                        self.root.after(0, self.update_rfid_entry, str(id))
                        time.sleep(1)  # Evitar lecturas múltiples rápidas
                time.sleep(0.1)  # Pequeña pausa para no sobrecargar el CPU
            except Exception as e:
                print(f"Error leyendo RFID: {e}")
                time.sleep(1)

    def update_rfid_entry(self, rfid_id):
        """Actualiza el campo de entrada RFID en el hilo principal"""
        if hasattr(self, 'rfid_entry') and self.rfid_entry.winfo_exists():
            self.rfid_entry.delete(0, tk.END)
            self.rfid_entry.insert(0, rfid_id)

    def validar_rfid(self):
        rfid = self.rfid_entry.get().strip()
        if rfid:
            self.datos["rfid"] = rfid
            self.stop_rfid_reading()  # Detener lectura RFID
            self.pantalla_datos()
        else:
            messagebox.showwarning("Campo vacío", "Por favor, ingrese el código RFID.")

    def pantalla_datos(self):
        self.limpiar_pantalla()
        tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
        tk.Label(self.root, text="Laboratorio de MAC", font=("Arial", 20, "bold"), fg="#1d127a", bg="#f5e0e0").place(x=280, y=20)

        tk.Label(self.root, text="Total de alumnos que hicieron uso del CC1:", font=("Arial", 12, "bold"), fg="white", bg="#1d127a").place(x=160, y=100)
        self.total_entry = tk.Entry(self.root, font=("Arial", 12), width=10, justify='center')
        self.total_entry.place(x=520, y=100)

        tk.Button(self.root, text="Materia", font=("Arial", 12, "bold"), fg="white", bg="#1d127a", width=20).place(x=80, y=180)
        self.materia_combobox = ttk.Combobox(self.root, font=("Arial", 12), width=22, state="readonly")
        self.materia_combobox['values'] = ["Ingenieria de Software", "Bases de Datos", "Programacion Web", "Inteligencia Artificial", "Ciencia de Datos"]
        self.materia_combobox.place(x=80, y=230)

        tk.Button(self.root, text="Grupo y Carrera", font=("Arial", 12, "bold"), fg="white", bg="#1d127a", width=20).place(x=310, y=180)
        self.grupo_combobox = ttk.Combobox(self.root, font=("Arial", 12), width=22, state="readonly")
        self.grupo_combobox['values'] = ["1A-ISC", "1A-INF"]
        self.grupo_combobox.place(x=310, y=230)

        tk.Button(self.root, text="Tipo de uso de software", font=("Arial", 12, "bold"), fg="white", bg="#1d127a", width=20).place(x=540, y=180)
        self.software_combobox = ttk.Combobox(self.root, font=("Arial", 12), width=22, state="readonly")
        self.software_combobox['values'] = ["Plataforma", "Office", "Internet", "AUTOCAD", "Teams"]
        self.software_combobox.place(x=540, y=230)

        tk.Button(self.root, text="Continuar", font=("Arial", 14, "bold"), fg="white", bg="#1d127a", padx=20, pady=5, command=self.validar_datos).place(x=350, y=450)

    def validar_datos(self):
        if not self.total_entry.get().isdigit() or not self.materia_combobox.get() or not self.grupo_combobox.get() or not self.software_combobox.get():
            messagebox.showerror("Faltan datos", "Por favor, complete todos los campos correctamente.")
            return

        self.datos["total"] = self.total_entry.get()
        self.datos["materia"] = self.materia_combobox.get()
        self.datos["grupo"] = self.grupo_combobox.get()
        self.datos["software"] = self.software_combobox.get()
        self.datos["fecha"] = datetime.now().strftime("%d/%m/%Y")
        self.datos["hora"] = datetime.now().strftime("%H:%M")
        self.pantalla_confirmacion()

    def pantalla_confirmacion(self):
        self.limpiar_pantalla()
        tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
        tk.Label(self.root, text="Laboratorio de MAC", font=("Arial", 22, "bold"), fg="navy", bg="#f5e0e0").pack(pady=20)

        datos = self.datos
        etiquetas = [
            f"Entrada: {datos['hora']}", datos["fecha"], datos["grupo"],
            datos["rfid"], datos["materia"],
            f"Total de Alumnos: {datos['total']}", f"Software: {datos['software']}"
        ]

        for i, txt in enumerate(etiquetas):
            x = 120 if i < 3 else 450
            y = 100 + (i % 3) * 50
            tk.Label(self.root, text=txt, font=("Arial", 14), bg="white", width=25).place(x=x, y=y)

        tk.Button(self.root, text="Atras", font=("Arial", 14), bg="navy", fg="white", width=12, command=self.pantalla_datos).place(x=220, y=400)
        tk.Button(self.root, text="Confirmar", font=("Arial", 14), bg="navy", fg="white", width=12, command=self.pantalla_exito).place(x=420, y=400)

    def pantalla_exito(self):
        self.limpiar_pantalla()
        tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
        tk.Label(self.root, text="Laboratorio de MAC", font=("Arial", 22, "bold"), fg="navy", bg="#f5e0e0").pack(pady=30)
        tk.Label(self.root, text="Registro Exitoso", font=("Arial", 20, "bold"), bg="lime", fg="black", width=30).pack(pady=30)
        tk.Button(self.root, text="Registrar Salida", font=("Arial", 16), bg="navy", fg="white", command=self.pantalla_salida).pack(pady=20)

    def pantalla_salida(self):
        self.limpiar_pantalla()
        tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
        tk.Label(self.root, text="Laboratorio de MAC", font=("Arial", 24, "bold"), fg="#1d127a", bg="#f5e0e0").pack(pady=100)
        tk.Label(self.root, text="Registrar Salida", font=("Arial", 18), fg="#1d127a", bg="#f5e0e0").pack()
        self.salida_entry = tk.Entry(self.root, font=("Arial", 18), justify='center')
        self.salida_entry.pack(pady=20)
        tk.Button(self.root, text="Finalizar", font=("Arial", 16, "bold"), fg="white", bg="#1d127a", command=self.finalizar_salida).pack(pady=20)
        
        # Iniciar lectura RFID para salida
        if self.rfid_active:
            self.start_rfid_reading_salida()

    def start_rfid_reading_salida(self):
        """Inicia la lectura automática de RFID para salida"""
        if not self.reading_rfid and self.rfid_active:
            self.reading_rfid = True
            threading.Thread(target=self.read_rfid_salida_continuously, daemon=True).start()

    def read_rfid_salida_continuously(self):
        """Lee continuamente las tarjetas RFID para salida"""
        while self.reading_rfid:
            try:
                if self.rfid_active:
                    id, text = self.reader.read_no_block()
                    if id:
                        self.root.after(0, self.update_salida_entry, str(id))
                        time.sleep(1)
                time.sleep(0.1)
            except Exception as e:
                print(f"Error leyendo RFID en salida: {e}")
                time.sleep(1)

    def update_salida_entry(self, rfid_id):
        """Actualiza el campo de salida RFID en el hilo principal"""
        if hasattr(self, 'salida_entry') and self.salida_entry.winfo_exists():
            self.salida_entry.delete(0, tk.END)
            self.salida_entry.insert(0, rfid_id)

    def finalizar_salida(self):
        self.stop_rfid_reading()
        self.pantalla_principal()

    def __del__(self):
        """Limpieza al cerrar la aplicación"""
        self.stop_rfid_reading()
        if self.rfid_active and RFID_AVAILABLE:
            try:
                GPIO.cleanup()
            except:
                pass

if __name__ == "__main__":
    root = tk.Tk()
    app = RegistroApp(root)
    
    # Manejar el cierre de la ventana
    def on_closing():
        app.stop_rfid_reading()
        if RFID_AVAILABLE:
            try:
                GPIO.cleanup()
            except:
                pass
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()