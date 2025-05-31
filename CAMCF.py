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
        self.root.geometry("800x600")
        self.root.configure(bg="#f5e0e0")
        
        # Configuración del lector RFID
        self.lector_rfid = SimpleMFRC522()
        self.rfid_data = None
        self.leyendo_rfid = False
        
        try:
            self.logo = tk.PhotoImage(file="logo.png")
        except:
            self.logo = None
            print("Warning: Logo image not found")
            
        self.datos = {}
        self.pantalla_principal()
        self.iniciar_lectura_rfid()

    def iniciar_lectura_rfid(self):
        """Inicia un hilo para leer continuamente el RFID"""
        if not self.leyendo_rfid:
            self.leyendo_rfid = True
            self.hilo_rfid = threading.Thread(target=self.leer_rfid_continuo, daemon=True)
            self.hilo_rfid.start()

    def leer_rfid_continuo(self):
        """Lee continuamente el RFID y actualiza la interfaz"""
        while self.leyendo_rfid:
            try:
                id, texto = self.lector_rfid.read_no_block()
                if id and id != self.rfid_data:
                    self.rfid_data = id
                    self.root.after(0, self.actualizar_rfid_ui, id)
            except Exception as e:
                print(f"Error leyendo RFID: {e}")
            finally:
                GPIO.cleanup()
                threading.Event().wait(0.1)

    def actualizar_rfid_ui(self, id_rfid):
        """Actualiza la interfaz con el RFID leído"""
        if hasattr(self, 'rfid_entry'):
            self.rfid_entry.delete(0, tk.END)
            self.rfid_entry.insert(0, str(id_rfid))
            self.validar_rfid()

    def limpiar_pantalla(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def pantalla_principal(self):
        self.limpiar_pantalla()
        if self.logo:
            tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
            
        tk.Label(self.root, text="Laboratorio de MAC", font=("Arial", 24, "bold"), fg="#1d127a", bg="#f5e0e0").pack(pady=100)
        tk.Label(self.root, text="Aproximar Tarjeta", font=("Arial", 18), fg="#1d127a", bg="#f5e0e0").pack()
        
        self.rfid_entry = tk.Entry(self.root, font=("Arial", 18), justify='center')
        self.rfid_entry.pack(pady=20)
        
        tk.Button(self.root, text="Continuar", font=("Arial", 16, "bold"), fg="white", bg="#1d127a", command=self.validar_rfid).pack(pady=20)
        tk.Button(self.root, text="Modo Manual", font=("Arial", 12), fg="white", bg="gray", command=self.modo_manual).pack(pady=10)

    def modo_manual(self):
        """Permite ingresar el RFID manualmente"""
        self.leyendo_rfid = False
        self.rfid_entry.config(state='normal')
        self.rfid_entry.focus()

    def validar_rfid(self):
        rfid = self.rfid_entry.get().strip()
        if rfid:
            self.datos["rfid"] = rfid
            self.leyendo_rfid = False
            self.pantalla_datos()
        else:
            messagebox.showwarning("Campo vacío", "Por favor, ingrese el código RFID o acerque la tarjeta.")
            self.iniciar_lectura_rfid()

    def pantalla_datos(self):
        self.limpiar_pantalla()
        if self.logo:
            tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
            
        tk.Label(self.root, text="Laboratorio de MAC", font=("Arial", 20, "bold"), fg="#1d127a", bg="#f5e0e0").place(x=280, y=20)

        # Sección de datos
        tk.Label(self.root, text="Total de alumnos que hicieron uso del CC1:", 
                font=("Arial", 12, "bold"), fg="white", bg="#1d127a").place(x=160, y=100)
        self.total_entry = tk.Entry(self.root, font=("Arial", 12), width=10, justify='center')
        self.total_entry.place(x=520, y=100)

        # Comboboxes
        tk.Label(self.root, text="Materia", font=("Arial", 12, "bold"), fg="white", bg="#1d127a", width=20).place(x=80, y=180)
        self.materia_combobox = ttk.Combobox(self.root, font=("Arial", 12), width=22, state="readonly")
        self.materia_combobox['values'] = ["Ingenieria de Software", "Bases de Datos", "Programacion Web", 
                                          "Inteligencia Artificial", "Ciencia de Datos"]
        self.materia_combobox.place(x=80, y=210)

        tk.Label(self.root, text="Grupo y Carrera", font=("Arial", 12, "bold"), fg="white", bg="#1d127a", width=20).place(x=310, y=180)
        self.grupo_combobox = ttk.Combobox(self.root, font=("Arial", 12), width=22, state="readonly")
        self.grupo_combobox['values'] = ["1A-ISC", "1A-INF", "2A-ISC", "2A-INF", "3A-ISC", "3A-INF"]
        self.grupo_combobox.place(x=310, y=210)

        tk.Label(self.root, text="Software utilizado", font=("Arial", 12, "bold"), fg="white", bg="#1d127a", width=20).place(x=540, y=180)
        self.software_combobox = ttk.Combobox(self.root, font=("Arial", 12), width=22, state="readonly")
        self.software_combobox['values'] = ["Plataforma", "Office", "Internet", "AUTOCAD", "Teams", "Visual Studio", "Otro"]
        self.software_combobox.place(x=540, y=210)

        # Botones
        tk.Button(self.root, text="Regresar", font=("Arial", 12), bg="gray", fg="white", 
                 command=lambda: [self.iniciar_lectura_rfid(), self.pantalla_principal()]).place(x=200, y=300)
        tk.Button(self.root, text="Continuar", font=("Arial", 12, "bold"), bg="#1d127a", fg="white", 
                 command=self.validar_datos).place(x=400, y=300)

    def validar_datos(self):
        if not self.total_entry.get().isdigit():
            messagebox.showerror("Error", "El total de alumnos debe ser un número")
            return
            
        if not all([self.materia_combobox.get(), self.grupo_combobox.get(), self.software_combobox.get()]):
            messagebox.showerror("Error", "Por favor complete todos los campos")
            return

        self.datos.update({
            "total": self.total_entry.get(),
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
            
        tk.Label(self.root, text="Confirmación de Datos", font=("Arial", 22, "bold"), fg="#1d127a", bg="#f5e0e0").pack(pady=20)

        # Marco para los datos
        frame = tk.Frame(self.root, bg="white", bd=2, relief=tk.GROOVE)
        frame.pack(pady=20, padx=40, fill=tk.BOTH, expand=True)

        datos = [
            ("ID Tarjeta:", self.datos["rfid"]),
            ("Fecha:", self.datos["fecha"]),
            ("Hora Entrada:", self.datos["hora_entrada"]),
            ("Materia:", self.datos["materia"]),
            ("Grupo:", self.datos["grupo"]),
            ("Alumnos:", self.datos["total"]),
            ("Software:", self.datos["software"])
        ]

        for i, (label, value) in enumerate(datos):
            tk.Label(frame, text=label, font=("Arial", 12, "bold"), bg="white").grid(row=i, column=0, sticky="e", padx=10, pady=5)
            tk.Label(frame, text=value, font=("Arial", 12), bg="white").grid(row=i, column=1, sticky="w", pady=5)

        # Botones
        tk.Button(self.root, text="Corregir", font=("Arial", 12), bg="gray", fg="white", 
                 command=self.pantalla_datos).place(x=250, y=450)
        tk.Button(self.root, text="Confirmar", font=("Arial", 12, "bold"), bg="#1d127a", fg="white", 
                 command=self.pantalla_exito).place(x=450, y=450)

    def pantalla_exito(self):
        self.limpiar_pantalla()
        if self.logo:
            tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
            
        tk.Label(self.root, text="Registro Exitoso", font=("Arial", 24, "bold"), fg="green", bg="#f5e0e0").pack(pady=100)
        tk.Label(self.root, text="Los datos han sido registrados correctamente", 
                font=("Arial", 14), bg="#f5e0e0").pack()
        
        tk.Button(self.root, text="Registrar Salida", font=("Arial", 14, "bold"), bg="#1d127a", fg="white", 
                 command=self.pantalla_salida).pack(pady=30)
        tk.Button(self.root, text="Nuevo Registro", font=("Arial", 12), bg="gray", fg="white", 
                 command=lambda: [self.iniciar_lectura_rfid(), self.pantalla_principal()]).pack()

    def pantalla_salida(self):
        self.limpiar_pantalla()
        if self.logo:
            tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
            
        tk.Label(self.root, text="Registro de Salida", font=("Arial", 24, "bold"), fg="#1d127a", bg="#f5e0e0").pack(pady=100)
        tk.Label(self.root, text="Aproxime la tarjeta para registrar la salida", 
                font=("Arial", 14), bg="#f5e0e0").pack()
        
        self.salida_entry = tk.Entry(self.root, font=("Arial", 18), justify='center')
        self.salida_entry.pack(pady=20)
        
        tk.Button(self.root, text="Leer Tarjeta", font=("Arial", 14), bg="#1d127a", fg="white", 
                 command=self.leer_salida).pack(pady=10)
        tk.Button(self.root, text="Ingresar Manualmente", font=("Arial", 12), bg="gray", fg="white", 
                 command=self.modo_manual_salida).pack()

    def leer_salida(self):
        """Lee el RFID para la salida"""
        try:
            id, _ = self.lector_rfid.read()
            self.salida_entry.delete(0, tk.END)
            self.salida_entry.insert(0, str(id))
            self.validar_salida()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer la tarjeta: {e}")

    def modo_manual_salida(self):
        """Permite ingresar el ID manualmente para salida"""
        self.salida_entry.config(state='normal')
        self.salida_entry.focus()

    def validar_salida(self):
        id_salida = self.salida_entry.get().strip()
        if not id_salida:
            messagebox.showwarning("Error", "Por favor ingrese o lea el ID de la tarjeta")
            return
            
        if 'rfid' in self.datos and id_salida == str(self.datos['rfid']):
            self.datos['hora_salida'] = datetime.now().strftime("%H:%M")
            self.pantalla_resumen()
        else:
            messagebox.showerror("Error", "El ID de salida no coincide con el de entrada")

    def pantalla_resumen(self):
        self.limpiar_pantalla()
        if self.logo:
            tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
            
        tk.Label(self.root, text="Resumen de Registro", font=("Arial", 24, "bold"), fg="#1d127a", bg="#f5e0e0").pack(pady=20)

        frame = tk.Frame(self.root, bg="white", bd=2, relief=tk.GROOVE)
        frame.pack(pady=20, padx=40, fill=tk.BOTH, expand=True)

        datos = [
            ("ID Tarjeta:", self.datos["rfid"]),
            ("Fecha:", self.datos["fecha"]),
            ("Hora Entrada:", self.datos["hora_entrada"]),
            ("Hora Salida:", self.datos.get("hora_salida", "No registrada")),
            ("Materia:", self.datos["materia"]),
            ("Grupo:", self.datos["grupo"]),
            ("Total Alumnos:", self.datos["total"]),
            ("Software:", self.datos["software"])
        ]

        for i, (label, value) in enumerate(datos):
            tk.Label(frame, text=label, font=("Arial", 12, "bold"), bg="white").grid(row=i, column=0, sticky="e", padx=10, pady=5)
            tk.Label(frame, text=value, font=("Arial", 12), bg="white").grid(row=i, column=1, sticky="w", pady=5)

        tk.Button(self.root, text="Finalizar", font=("Arial", 14, "bold"), bg="#1d127a", fg="white", 
                 command=self.finalizar_aplicacion).pack(pady=30)

    def finalizar_aplicacion(self):
        """Guarda los datos y cierra la aplicación"""
        # Aquí podrías agregar código para guardar en archivo/BD
        print("Datos registrados:", self.datos)
        self.root.destroy()

    def __del__(self):
        """Limpiar al cerrar la aplicación"""
        self.leyendo_rfid = False
        if hasattr(self, 'hilo_rfid'):
            self.hilo_rfid.join()
        GPIO.cleanup()

if __name__ == "__main__":
    root = tk.Tk()
    app = RegistroApp(root)
    try:
        root.mainloop()
    finally:
        del app