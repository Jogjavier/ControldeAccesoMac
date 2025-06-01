import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import threading

class RegistroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Laboratorio de MAC")
        self.root.geometry("800x480")  # Adjusted for Raspberry Pi screen
        self.root.configure(bg="#f5e0e0")
        
        # RFID Reader Configuration
        self.lector_rfid = SimpleMFRC522()
        self.rfid_data = None
        self.leyendo_rfid = False
        
        # Teacher database (RFID: Name)
        self.docentes = {
            "123456789": "Prof. Juan Pérez",
            "987654321": "Prof. María García",
            "456123789": "Prof. Carlos López"
        }
        
        try:
            self.logo = tk.PhotoImage(file="logo.png")
            self.logo = self.logo.subsample(2, 2)  # Reduce logo size
        except:
            self.logo = None
            
        self.datos = {}
        self.pantalla_inicial()
        self.iniciar_lectura_rfid()

    def iniciar_lectura_rfid(self):
        """Starts continuous RFID reading thread"""
        if not self.leyendo_rfid:
            self.leyendo_rfid = True
            self.hilo_rfid = threading.Thread(target=self.leer_rfid_continuo, daemon=True)
            self.hilo_rfid.start()

    def leer_rfid_continuo(self):
        """Continuously reads RFID and updates UI"""
        while self.leyendo_rfid:
            try:
                id, texto = self.lector_rfid.read_no_block()
                if id and id != self.rfid_data:
                    self.rfid_data = str(id)
                    self.root.after(0, self.mostrar_nombre_docente, self.rfid_data)
            except Exception as e:
                print(f"RFID reading error: {e}")
            finally:
                GPIO.cleanup()
                threading.Event().wait(0.1)

    def mostrar_nombre_docente(self, id_rfid):
        """Shows teacher name and activates Continue button"""
        if hasattr(self, 'rfid_entry'):
            self.rfid_entry.delete(0, tk.END)
            self.rfid_entry.insert(0, id_rfid)
            
            nombre = self.docentes.get(id_rfid, "Docente no registrado")
            
            # Teacher info frame
            if not hasattr(self, 'marco_docente'):
                self.marco_docente = tk.Frame(self.root, bg="white", bd=2, relief=tk.GROOVE)
                self.marco_docente.place(x=100, y=180, width=600, height=80)
                
                self.nombre_label = tk.Label(self.marco_docente, text=f"Docente: {nombre}", 
                                          font=("Arial", 14, "bold"), bg="white")
                self.nombre_label.pack(pady=20)
            else:
                self.nombre_label.config(text=f"Docente: {nombre}")
            
            # Continue button - fixed visible position
            if not hasattr(self, 'btn_continuar'):
                self.btn_continuar = tk.Button(
                    self.root, 
                    text="CONTINUAR", 
                    font=("Arial", 20, "bold"), 
                    fg="white", 
                    bg="#1d127a", 
                    padx=40, 
                    pady=10,
                    command=self.validar_rfid
                )
                self.btn_continuar.place(x=250, y=350, width=300, height=60)
            
            self.leyendo_rfid = False

    def limpiar_pantalla(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def pantalla_inicial(self):
        self.limpiar_pantalla()
        
        if self.logo:
            tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
            
        # Main title
        tk.Label(
            self.root, 
            text="Laboratorio de MAC", 
            font=("Arial", 22, "bold"),
            fg="#1d127a", 
            bg="#f5e0e0"
        ).place(x=200, y=30)
        
        # User instruction
        tk.Label(
            self.root, 
            text="Aproxime su tarjeta RFID", 
            font=("Arial", 16),
            fg="#1d127a", 
            bg="#f5e0e0"
        ).place(x=250, y=90)
        
        # RFID frame
        marco_rfid = tk.Frame(self.root, bg="white", bd=2, relief=tk.GROOVE)
        marco_rfid.place(x=150, y=130, width=500, height=60)
        
        tk.Label(
            marco_rfid, 
            text="ID:", 
            font=("Arial", 12), 
            bg="white"
        ).pack(side=tk.LEFT, padx=10)
        
        self.rfid_entry = tk.Entry(
            marco_rfid, 
            font=("Arial", 14), 
            justify='center'
        )
        self.rfid_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)
        
        # Manual mode button
        self.btn_manual = tk.Button(
            self.root, 
            text="Modo Manual", 
            font=("Arial", 12), 
            fg="white", 
            bg="gray", 
            command=self.modo_manual
        )
        self.btn_manual.place(x=650, y=400, width=120, height=40)

    def modo_manual(self):
        """Manual RFID and name input"""
        self.leyendo_rfid = False
        self.rfid_entry.config(state='normal')
        self.rfid_entry.focus()
        
        self.btn_manual.place_forget()
        
        # Name input frame
        marco_nombre = tk.Frame(self.root, bg="white", bd=2, relief=tk.GROOVE)
        marco_nombre.place(x=100, y=180, width=600, height=80)
        
        tk.Label(
            marco_nombre, 
            text="Nombre Docente:", 
            font=("Arial", 12), 
            bg="white"
        ).pack(side=tk.LEFT, padx=10)
        
        self.nombre_entry = tk.Entry(marco_nombre, font=("Arial", 14))
        self.nombre_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)
        
        # Continue button
        self.btn_continuar = tk.Button(
            self.root, 
            text="CONTINUAR", 
            font=("Arial", 20, "bold"), 
            fg="white", 
            bg="#1d127a", 
            padx=40, 
            pady=10,
            command=self.validar_rfid
        )
        self.btn_continuar.place(x=250, y=350, width=300, height=60)

    def validar_rfid(self):
        rfid = self.rfid_entry.get().strip()
        if not rfid:
            messagebox.showwarning("Error", "Por favor ingrese o lea el RFID")
            self.iniciar_lectura_rfid()
            return
            
        # Manual mode handling
        if not self.leyendo_rfid and hasattr(self, 'nombre_entry'):
            nombre = self.nombre_entry.get().strip()
            if not nombre:
                messagebox.showwarning("Error", "Por favor ingrese el nombre del docente")
                return
            self.docentes[rfid] = nombre
            self.datos["docente"] = nombre
        else:
            nombre = self.docentes.get(rfid, "")
            if not nombre:
                messagebox.showwarning("Error", "Docente no registrado")
                return
            self.datos["docente"] = nombre
        
        self.datos["rfid"] = rfid
        self.pantalla_datos()

    def pantalla_datos(self):
        self.limpiar_pantalla()
        if self.logo:
            tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
            
        tk.Label(
            self.root, 
            text="Registro de Laboratorio", 
            font=("Arial", 20, "bold"), 
            fg="#1d127a", 
            bg="#f5e0e0"
        ).place(x=200, y=20)
        
        # Teacher info
        tk.Label(
            self.root, 
            text=f"Docente: {self.datos['docente']}", 
            font=("Arial", 14), 
            bg="#f5e0e0"
        ).place(x=200, y=70)
        
        # Data fields
        campos = [
            ("Total de alumnos:", 150, 120),
            ("Materia:", 150, 170),
            ("Grupo:", 150, 220),
            ("Software utilizado:", 150, 270)
        ]
        
        for i, (texto, x_pos, y_pos) in enumerate(campos):
            tk.Label(
                self.root, 
                text=texto, 
                font=("Arial", 12), 
                bg="#f5e0e0"
            ).place(x=x_pos, y=y_pos)
        
        # Entries and comboboxes
        self.total_entry = tk.Entry(self.root, font=("Arial", 12))
        self.total_entry.place(x=350, y=120, width=200)
        
        self.materia_combobox = ttk.Combobox(
            self.root, 
            font=("Arial", 12), 
            values=["Ingeniería de Software", "Bases de Datos", "Programación Web"]
        )
        self.materia_combobox.place(x=350, y=170, width=200)
        
        self.grupo_combobox = ttk.Combobox(
            self.root, 
            font=("Arial", 12), 
            values=["1A-ISC", "1A-INF", "2A-ISC", "2A-INF"]
        )
        self.grupo_combobox.place(x=350, y=220, width=200)
        
        self.software_combobox = ttk.Combobox(
            self.root, 
            font=("Arial", 12), 
            values=["Plataforma", "Office", "Internet", "AUTOCAD"]
        )
        self.software_combobox.place(x=350, y=270, width=200)
        
        # Buttons
        tk.Button(
            self.root, 
            text="Regresar", 
            font=("Arial", 12), 
            bg="gray", 
            fg="white", 
            command=self.pantalla_inicial
        ).place(x=200, y=350, width=150, height=50)
        
        tk.Button(
            self.root, 
            text="Continuar", 
            font=("Arial", 12, "bold"), 
            bg="#1d127a", 
            fg="white", 
            command=self.validar_datos
        ).place(x=450, y=350, width=150, height=50)

    def validar_datos(self):
        if not self.total_entry.get().isdigit():
            messagebox.showerror("Error", "Ingrese un número válido de alumnos")
            return
            
        if not all([self.materia_combobox.get(), self.grupo_combobox.get(), 
                   self.software_combobox.get()]):
            messagebox.showerror("Error", "Complete todos los campos")
            return
            
        self.datos.update({
            "total_alumnos": self.total_entry.get(),
            "materia": self.materia_combobox.get(),
            "grupo": self.grupo_combobox.get(),
            "software": self.software_combobox.get(),
            "fecha": datetime.now().strftime("%d/%m/%Y"),
            "hora_entrada": datetime.now().strftime("%H:%M")
        })
        
        self.pantalla_confirmacion()

    def pantalla_confirmacion(self):
        self.limpiar_pantalla()
        if self.logo:
            tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
            
        tk.Label(
            self.root, 
            text="Confirmación de Datos", 
            font=("Arial", 20, "bold"), 
            fg="#1d127a", 
            bg="#f5e0e0"
        ).place(x=200, y=20)
        
        # Data display
        frame = tk.Frame(self.root, bg="white")
        frame.place(x=100, y=80, width=600, height=250)
        
        datos = [
            ("Docente:", self.datos["docente"]),
            ("Fecha:", self.datos["fecha"]),
            ("Hora entrada:", self.datos["hora_entrada"]),
            ("Materia:", self.datos["materia"]),
            ("Grupo:", self.datos["grupo"]),
            ("Alumnos:", self.datos["total_alumnos"]),
            ("Software:", self.datos["software"])
        ]
        
        for i, (label, valor) in enumerate(datos):
            tk.Label(
                frame, 
                text=label, 
                font=("Arial", 12, "bold"), 
                bg="white"
            ).grid(row=i, column=0, sticky="e", padx=10, pady=5)
            
            tk.Label(
                frame, 
                text=valor, 
                font=("Arial", 12), 
                bg="white"
            ).grid(row=i, column=1, sticky="w", pady=5)
        
        # Buttons
        tk.Button(
            self.root, 
            text="Corregir", 
            font=("Arial", 12), 
            bg="gray", 
            fg="white", 
            command=self.pantalla_datos
        ).place(x=200, y=350, width=150, height=50)
        
        tk.Button(
            self.root, 
            text="Confirmar", 
            font=("Arial", 12, "bold"), 
            bg="#1d127a", 
            fg="white", 
            command=self.pantalla_exito
        ).place(x=450, y=350, width=150, height=50)

    def pantalla_exito(self):
        self.limpiar_pantalla()
        if self.logo:
            tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
            
        tk.Label(
            self.root, 
            text="¡Registro Exitoso!", 
            font=("Arial", 24, "bold"), 
            fg="green", 
            bg="#f5e0e0"
        ).place(x=250, y=100)
        
        tk.Label(
            self.root, 
            text="Los datos se han registrado correctamente", 
            font=("Arial", 14), 
            bg="#f5e0e0"
        ).place(x=150, y=180)
        
        tk.Button(
            self.root, 
            text="Registrar Salida", 
            font=("Arial", 16, "bold"), 
            bg="#1d127a", 
            fg="white", 
            command=self.pantalla_salida
        ).place(x=250, y=250, width=300, height=60)

    def pantalla_salida(self):
        self.limpiar_pantalla()
        if self.logo:
            tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
            
        tk.Label(
            self.root, 
            text="Registro de Salida", 
            font=("Arial", 24, "bold"), 
            fg="#1d127a", 
            bg="#f5e0e0"
        ).place(x=200, y=100)
        
        tk.Label(
            self.root, 
            text="Aproxime la misma tarjeta para registrar la salida", 
            font=("Arial", 14), 
            bg="#f5e0e0"
        ).place(x=150, y=180)
        
        # Start exit RFID reading
        self.leyendo_salida = True
        self.hilo_salida = threading.Thread(target=self.leer_salida_rfid, daemon=True)
        self.hilo_salida.start()
        
        # Manual mode button
        tk.Button(
            self.root, 
            text="Modo Manual", 
            font=("Arial", 12), 
            bg="gray", 
            fg="white", 
            command=self.modo_manual_salida
        ).place(x=300, y=250, width=200, height=40)

    def leer_salida_rfid(self):
        """Reads RFID for exit registration"""
        try:
            id, _ = self.lector_rfid.read()
            id_str = str(id)
            if id_str == self.datos["rfid"]:
                self.datos["hora_salida"] = datetime.now().strftime("%H:%M")
                self.root.after(0, self.registro_completo)
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", "Tarjeta no coincide con la de entrada"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"No se pudo leer la tarjeta: {e}"))
        finally:
            GPIO.cleanup()
            self.leyendo_salida = False

    def modo_manual_salida(self):
        """Manual exit registration"""
        self.leyendo_salida = False
        self.datos["hora_salida"] = datetime.now().strftime("%H:%M")
        self.registro_completo()

    def registro_completo(self):
        """Shows final message and returns to initial screen"""
        messagebox.showinfo("Salida registrada", f"Salida registrada a las {self.datos['hora_salida']}")
        
        # Here you could save the data to a file or database
        print("Datos completos:", self.datos)
        
        # Restart the application
        self.datos = {}
        self.pantalla_inicial()
        self.iniciar_lectura_rfid()

    def __del__(self):
        """Cleanup when closing the application"""
        self.leyendo_rfid = False
        if hasattr(self, 'hilo_rfid'):
            self.hilo_rfid.join()
        if hasattr(self, 'leyendo_salida') and self.leyendo_salida:
            self.leyendo_salida = False
            if hasattr(self, 'hilo_salida'):
                self.hilo_salida.join()
        GPIO.cleanup()

if __name__ == "__main__":
    root = tk.Tk()
    app = RegistroApp(root)
    try:
        root.mainloop()
    finally:
        del app