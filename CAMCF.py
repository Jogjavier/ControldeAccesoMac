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
        
        # Base de datos simulada de docentes (RFID: Nombre)
        self.docentes = {
            "123456789": "Prof. Juan Pérez",
            "987654321": "Prof. María García",
            "456123789": "Prof. Carlos López"
        }
        
        try:
            self.logo = tk.PhotoImage(file="logo.png")
        except:
            self.logo = None
            print("Warning: Logo image not found")
            
        self.datos = {}
        self.pantalla_inicial()
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
                    self.rfid_data = str(id)
                    self.root.after(0, self.mostrar_nombre_docente, self.rfid_data)
            except Exception as e:
                print(f"Error leyendo RFID: {e}")
            finally:
                GPIO.cleanup()
                threading.Event().wait(0.1)

    def mostrar_nombre_docente(self, id_rfid):
        """Muestra el nombre del docente después de leer el RFID"""
        if hasattr(self, 'rfid_entry'):
            self.rfid_entry.delete(0, tk.END)
            self.rfid_entry.insert(0, id_rfid)
            
            # Buscar el nombre del docente
            nombre = self.docentes.get(id_rfid, "Docente no registrado")
            
            # Mostrar el nombre en la interfaz
            if hasattr(self, 'nombre_label'):
                self.nombre_label.config(text=f"Docente: {nombre}")
            else:
                self.nombre_label = tk.Label(self.root, text=f"Docente: {nombre}", 
                                           font=("Arial", 14), bg="#f5e0e0")
                self.nombre_label.pack(pady=10)
            
            # Deshabilitar la lectura automática
            self.leyendo_rfid = False

    def limpiar_pantalla(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def pantalla_inicial(self):
        self.limpiar_pantalla()
        if self.logo:
            tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
            
        tk.Label(self.root, text="Laboratorio de MAC", font=("Arial", 24, "bold"), 
                fg="#1d127a", bg="#f5e0e0").pack(pady=50)
        tk.Label(self.root, text="Aproxime su tarjeta RFID", font=("Arial", 18), 
                fg="#1d127a", bg="#f5e0e0").pack(pady=20)
        
        self.rfid_entry = tk.Entry(self.root, font=("Arial", 18), justify='center')
        self.rfid_entry.pack(pady=20)
        
        # Botón de modo manual (opcional)
        tk.Button(self.root, text="Modo Manual", font=("Arial", 12), 
                 fg="white", bg="gray", command=self.modo_manual).pack(pady=10)

    def modo_manual(self):
        """Permite ingresar el RFID manualmente"""
        self.leyendo_rfid = False
        self.rfid_entry.config(state='normal')
        self.rfid_entry.focus()
        
        # Crear campo para nombre si no existe
        if not hasattr(self, 'nombre_label'):
            self.nombre_label = tk.Label(self.root, text="Docente: (Ingrese nombre)", 
                                       font=("Arial", 14), bg="#f5e0e0")
            self.nombre_label.pack(pady=10)
            
            self.nombre_entry = tk.Entry(self.root, font=("Arial", 14))
            self.nombre_entry.pack(pady=10)
        
        # Mostrar botón continuar
        if not hasattr(self, 'btn_continuar'):
            self.btn_continuar = tk.Button(self.root, text="Continuar", 
                                         font=("Arial", 16, "bold"), 
                                         fg="white", bg="#1d127a", 
                                         command=self.validar_rfid)
            self.btn_continuar.pack(pady=20)

    def validar_rfid(self):
        rfid = self.rfid_entry.get().strip()
        if not rfid:
            messagebox.showwarning("Error", "Por favor ingrese o lea el RFID")
            self.iniciar_lectura_rfid()
            return
            
        # Si está en modo manual y no encontró el docente
        if not self.leyendo_rfid and hasattr(self, 'nombre_entry'):
            nombre = self.nombre_entry.get().strip()
            if not nombre:
                messagebox.showwarning("Error", "Por favor ingrese el nombre del docente")
                return
            self.docentes[rfid] = nombre  # Registrar nuevo docente
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
            
        tk.Label(self.root, text="Registro de Laboratorio", font=("Arial", 20, "bold"), 
                fg="#1d127a", bg="#f5e0e0").pack(pady=20)
        
        # Mostrar información del docente
        tk.Label(self.root, text=f"Docente: {self.datos['docente']}", 
                font=("Arial", 14), bg="#f5e0e0").pack(pady=10)
        
        # Campos de datos
        tk.Label(self.root, text="Total de alumnos:", font=("Arial", 12), 
                bg="#f5e0e0").place(x=150, y=150)
        self.total_entry = tk.Entry(self.root, font=("Arial", 12))
        self.total_entry.place(x=300, y=150)
        
        tk.Label(self.root, text="Materia:", font=("Arial", 12), 
                bg="#f5e0e0").place(x=150, y=200)
        self.materia_combobox = ttk.Combobox(self.root, font=("Arial", 12), 
                                           values=["Ingeniería de Software", "Bases de Datos", 
                                                  "Programación Web", "Inteligencia Artificial"])
        self.materia_combobox.place(x=300, y=200)
        
        tk.Label(self.root, text="Grupo:", font=("Arial", 12), 
                bg="#f5e0e0").place(x=150, y=250)
        self.grupo_combobox = ttk.Combobox(self.root, font=("Arial", 12), 
                                         values=["1A-ISC", "1A-INF", "2A-ISC", "2A-INF"])
        self.grupo_combobox.place(x=300, y=250)
        
        tk.Label(self.root, text="Software utilizado:", font=("Arial", 12), 
                bg="#f5e0e0").place(x=150, y=300)
        self.software_combobox = ttk.Combobox(self.root, font=("Arial", 12), 
                                            values=["Plataforma", "Office", "Internet", "AUTOCAD"])
        self.software_combobox.place(x=300, y=300)
        
        # Botones
        tk.Button(self.root, text="Regresar", font=("Arial", 12), 
                 bg="gray", fg="white", command=self.pantalla_inicial).place(x=250, y=400)
        tk.Button(self.root, text="Continuar", font=("Arial", 12, "bold"), 
                 bg="#1d127a", fg="white", command=self.validar_datos).place(x=450, y=400)

    def validar_datos(self):
        # Validar campos
        if not self.total_entry.get().isdigit():
            messagebox.showerror("Error", "Ingrese un número válido de alumnos")
            return
            
        if not all([self.materia_combobox.get(), self.grupo_combobox.get(), 
                   self.software_combobox.get()]):
            messagebox.showerror("Error", "Complete todos los campos")
            return
            
        # Guardar datos
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
            
        tk.Label(self.root, text="Confirmación de Datos", font=("Arial", 20, "bold"), 
                fg="#1d127a", bg="#f5e0e0").pack(pady=20)
        
        # Mostrar datos
        frame = tk.Frame(self.root, bg="white")
        frame.pack(pady=20, padx=50, fill=tk.BOTH, expand=True)
        
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
            tk.Label(frame, text=label, font=("Arial", 12, "bold"), 
                   bg="white").grid(row=i, column=0, sticky="e", padx=10, pady=5)
            tk.Label(frame, text=valor, font=("Arial", 12), 
                   bg="white").grid(row=i, column=1, sticky="w", pady=5)
        
        # Botones
        tk.Button(self.root, text="Corregir", font=("Arial", 12), 
                 bg="gray", fg="white", command=self.pantalla_datos).place(x=250, y=450)
        tk.Button(self.root, text="Confirmar", font=("Arial", 12, "bold"), 
                 bg="#1d127a", fg="white", command=self.pantalla_exito).place(x=450, y=450)

    def pantalla_exito(self):
        self.limpiar_pantalla()
        if self.logo:
            tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
            
        tk.Label(self.root, text="¡Registro Exitoso!", font=("Arial", 24, "bold"), 
                fg="green", bg="#f5e0e0").pack(pady=100)
        
        tk.Label(self.root, text="Los datos se han registrado correctamente", 
                font=("Arial", 14), bg="#f5e0e0").pack()
        
        tk.Button(self.root, text="Registrar Salida", font=("Arial", 16, "bold"), 
                 bg="#1d127a", fg="white", command=self.pantalla_salida).pack(pady=30)

    def pantalla_salida(self):
        self.limpiar_pantalla()
        if self.logo:
            tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
            
        tk.Label(self.root, text="Registro de Salida", font=("Arial", 24, "bold"), 
                fg="#1d127a", bg="#f5e0e0").pack(pady=100)
        
        tk.Label(self.root, text="Aproxime la misma tarjeta para registrar la salida", 
                font=("Arial", 14), bg="#f5e0e0").pack()
        
        # Iniciar lectura de salida
        self.leyendo_salida = True
        self.hilo_salida = threading.Thread(target=self.leer_salida_rfid, daemon=True)
        self.hilo_salida.start()
        
        # Mostrar botón manual por si falla
        tk.Button(self.root, text="Modo Manual", font=("Arial", 12), 
                 bg="gray", fg="white", command=self.modo_manual_salida).pack(pady=20)

    def leer_salida_rfid(self):
        """Lee el RFID para registrar la salida"""
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
        """Registra salida manualmente"""
        self.leyendo_salida = False
        self.datos["hora_salida"] = datetime.now().strftime("%H:%M")
        self.registro_completo()

    def registro_completo(self):
        """Muestra mensaje final y regresa a pantalla inicial"""
        messagebox.showinfo("Salida registrada", f"Salida registrada a las {self.datos['hora_salida']}")
        
        # Aquí podrías guardar los datos en un archivo o base de datos
        print("Datos completos:", self.datos)
        
        # Reiniciar la aplicación
        self.datos = {}
        self.pantalla_inicial()
        self.iniciar_lectura_rfid()

    def __del__(self):
        """Limpiar al cerrar la aplicación"""
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