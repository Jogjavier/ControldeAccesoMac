import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import psycopg2
from psycopg2 import sql, Error

class RegistroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Laboratorio de MAC")
        self.root.geometry("800x600")
        self.root.configure(bg="#f5e0e0")
        self.logo = tk.PhotoImage(file="logo.png")
        self.datos = {}
        self.docente_actual = None
        
        # Configuración de la base de datos
        self.db_config = {
            'host': '192.168.1.40',
            'database': 'Prueba',
            'user': 'javier',
            'password': '1234',
            'port': '5432'
        }
        
        self.pantalla_principal()

    def conectar_db(self):
        """Establece conexión con la base de datos PostgreSQL"""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Error as e:
            print(f"Error al conectar a PostgreSQL: {e}")
            messagebox.showerror("Error de conexión", "No se pudo conectar a la base de datos")
            return None

    def buscar_docente_por_rfid(self, rfid):
        """Busca un docente en la base de datos por su RFID"""
        conn = self.conectar_db()
        if conn is None:
            return None
            
        try:
            with conn.cursor() as cursor:
                # Buscar docente y sus asignaciones en una sola tabla
                query = sql.SQL("""
                    SELECT id, docente, rfid, 
                           materias, grupos, software
                    FROM prueba 
                    WHERE rfid = %s
                """)
                cursor.execute(query, (rfid,))
                docente = cursor.fetchone()
                
                if docente:
                    # Convertir strings separados por comas a listas
                    materias = docente[3].split(',') if docente[3] else []
                    grupos = docente[4].split(',') if docente[4] else []
                    software = docente[5].split(',') if docente[5] else []
                    
                    return {
                        'id': docente[0],
                        'docente': docente[1],
                        'rfid': docente[2],
                        'materias': materias,
                        'grupos': grupos,
                        'software': software
                    }
                return None
        except Error as e:
            print(f"Error al buscar docente: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def registrar_entrada(self, rfid, docente, total_alumnos, materia, grupo, software):
        """Registra una entrada en la base de datos"""
        conn = self.conectar_db()
        if conn is None:
            return False
            
        try:
            with conn.cursor() as cursor:
                query = sql.SQL("""
                    INSERT INTO registro_entradas 
                    (rfid, docente, totalumnos, materia, grupo, software, entrada) 
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """)
                cursor.execute(query, (rfid, docente, total_alumnos, materia, grupo, software))
                conn.commit()
                return True
        except Error as e:
            print(f"Error al registrar entrada: {e}")
            conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def limpiar_pantalla(self):
        """Limpia todos los widgets de la pantalla"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def pantalla_principal(self):
        """Muestra la pantalla principal de la aplicación"""
        self.limpiar_pantalla()
        self.docente_actual = None
        
        tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
        tk.Label(self.root, text="Laboratorio de MAC", font=("Arial", 24, "bold"), fg="#1d127a", bg="#f5e0e0").pack(pady=(100, 20))
        tk.Label(self.root, text="Aproximar Tarjeta", font=("Arial", 18), fg="#1d127a", bg="#f5e0e0").pack()

        # Etiqueta para mostrar información del docente
        self.docente_label = tk.Label(self.root, text="", font=("Arial", 14), fg="black", bg="#f5e0e0")
        self.docente_label.pack(pady=(0, 20))

        self.rfid_label = tk.Label(self.root, text="Esperando tarjeta...", font=("Arial", 16), fg="black", bg="#f5e0e0")
        self.rfid_label.pack(pady=(0, 20))

        self.btn_continuar = tk.Button(self.root, text="Continuar", font=("Arial", 16, "bold"), 
                                     fg="white", bg="#1d127a", state=tk.DISABLED,
                                     command=self.validar_rfid)
        self.btn_continuar.pack(pady=20)

        # Iniciar el hilo de lectura RFID
        threading.Thread(target=self.leer_rfid, daemon=True).start()

    def leer_rfid(self):
        """Lee el RFID del lector"""
        reader = SimpleMFRC522()
        try:
            id, text = reader.read()
            rfid = str(id)
            self.datos["rfid"] = rfid
            self.rfid_label.config(text=f"Tarjeta detectada: {rfid}")
            
            # Buscar docente en la base de datos
            self.docente_actual = self.buscar_docente_por_rfid(rfid)
            
            if self.docente_actual:
                self.docente_label.config(text=f"Docente: {self.docente_actual['docente']}")
                self.btn_continuar.config(state=tk.NORMAL)
            else:
                self.rfid_label.config(text="Docente no registrado")
                self.docente_label.config(text="")
                messagebox.showerror("Error", "Docente no encontrado en la base de datos")
                
        except Exception as e:
            print("Error leyendo RFID:", e)
            self.rfid_label.config(text="Error al leer tarjeta")
        finally:
            GPIO.cleanup()

    def validar_rfid(self):
        """Valida el RFID leído y pasa a la siguiente pantalla"""
        if 'rfid' not in self.datos or not self.docente_actual:
            messagebox.showerror("Error", "No se ha detectado ninguna tarjeta válida")
            return
        self.pantalla_datos()

    def pantalla_datos(self):
        """Muestra la pantalla para seleccionar datos asignados al docente"""
        self.limpiar_pantalla()
        tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
        tk.Label(self.root, text="Laboratorio de MAC", font=("Arial", 20, "bold"), fg="#1d127a", bg="#f5e0e0").place(x=280, y=20)
        
        # Mostrar información del docente
        if self.docente_actual:
            docente_info = f"Docente: {self.docente_actual['docente']}"
            tk.Label(self.root, text=docente_info, font=("Arial", 14), fg="black", bg="#f5e0e0").place(x=250, y=70)

        tk.Label(self.root, text="Total de alumnos que hicieron uso del CC1:", font=("Arial", 12, "bold"), fg="white", bg="#1d127a").place(x=160, y=100)
        self.total_entry = tk.Entry(self.root, font=("Arial", 12), width=10, justify='center')
        self.total_entry.place(x=520, y=100)

        # Materias asignadas
        tk.Button(self.root, text="Materia", font=("Arial", 12, "bold"), fg="white", bg="#1d127a", width=20).place(x=80, y=180)
        self.materia_combobox = ttk.Combobox(self.root, font=("Arial", 12), width=22, state="readonly")
        self.materia_combobox['values'] = self.docente_actual['materias']
        if self.docente_actual['materias']:
            self.materia_combobox.current(0)
        self.materia_combobox.place(x=80, y=230)

        # Grupos asignados
        tk.Button(self.root, text="Grupo y Carrera", font=("Arial", 12, "bold"), fg="white", bg="#1d127a", width=20).place(x=310, y=180)
        self.grupo_combobox = ttk.Combobox(self.root, font=("Arial", 12), width=22, state="readonly")
        self.grupo_combobox['values'] = self.docente_actual['grupos']
        if self.docente_actual['grupos']:
            self.grupo_combobox.current(0)
        self.grupo_combobox.place(x=310, y=230)

        # Software asignado
        tk.Button(self.root, text="Tipo de uso de software", font=("Arial", 12, "bold"), fg="white", bg="#1d127a", width=20).place(x=540, y=180)
        self.software_combobox = ttk.Combobox(self.root, font=("Arial", 12), width=22, state="readonly")
        self.software_combobox['values'] = self.docente_actual['software']
        if self.docente_actual['software']:
            self.software_combobox.current(0)
        self.software_combobox.place(x=540, y=230)

        tk.Button(self.root, text="Continuar", font=("Arial", 14, "bold"), fg="white", bg="#1d127a", padx=20, pady=5, command=self.validar_datos).place(x=330, y=300)

    def validar_datos(self):
        """Valida los datos ingresados antes de registrar"""
        if not self.total_entry.get().isdigit() or not self.materia_combobox.get() or not self.grupo_combobox.get() or not self.software_combobox.get():
            messagebox.showerror("Faltan datos", "Por favor, complete todos los campos correctamente.")
            return

        total_alumnos = self.total_entry.get()
        materia = self.materia_combobox.get()
        grupo = self.grupo_combobox.get()
        software = self.software_combobox.get()

        # Registrar los datos en la base de datos
        if self.docente_actual:
            if self.registrar_entrada(
                self.docente_actual['rfid'],
                self.docente_actual['docente'],
                total_alumnos,
                materia,
                grupo,
                software
            ):
                self.datos["total"] = total_alumnos
                self.datos["materia"] = materia
                self.datos["grupo"] = grupo
                self.datos["software"] = software
                self.datos["fecha"] = datetime.now().strftime("%d/%m/%Y")
                self.datos["hora"] = datetime.now().strftime("%H:%M")
                self.pantalla_confirmacion()
            else:
                messagebox.showerror("Error", "No se pudo registrar la entrada en la base de datos")
        else:
            messagebox.showerror("Error", "No se encontró información del docente")

    def pantalla_confirmacion(self):
        """Muestra la pantalla de confirmación de datos"""
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

        tk.Button(self.root, text="Atras", font=("Arial", 14), bg="navy", fg="white", width=12, command=self.pantalla_datos).place(x=220, y=270)
        tk.Button(self.root, text="Confirmar", font=("Arial", 14), bg="navy", fg="white", width=12, command=self.pantalla_exito).place(x=420, y=270)

    def pantalla_exito(self):
        """Muestra la pantalla de registro exitoso"""
        self.limpiar_pantalla()
        tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
        tk.Label(self.root, text="Laboratorio de MAC", font=("Arial", 22, "bold"), fg="navy", bg="#f5e0e0").pack(pady=30)
        tk.Label(self.root, text="Registro Exitoso", font=("Arial", 20, "bold"), bg="lime", fg="black", width=30).pack(pady=30)
        tk.Button(self.root, text="Registrar Salida", font=("Arial", 16), bg="navy", fg="white", command=self.pantalla_salida).pack(pady=20)

    def pantalla_salida(self):
        """Muestra la pantalla para registrar salida"""
        self.limpiar_pantalla()
        tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
        tk.Label(self.root, text="Laboratorio de MAC", font=("Arial", 24, "bold"), fg="#1d127a", bg="#f5e0e0").pack(pady=100)
        tk.Label(self.root, text="Registrar Salida\nAproxime su tarjeta", font=("Arial", 18), fg="#1d127a", bg="#f5e0e0").pack()

        self.rfid_label = tk.Label(self.root, text="Esperando tarjeta...", font=("Arial", 18), fg="black", bg="#f5e0e0")
        self.rfid_label.pack(pady=20)

        # Reutilizar lector para la salida
        threading.Thread(target=self.leer_salida_rfid, daemon=True).start()

    def leer_salida_rfid(self):
        """Lee el RFID para registrar la salida"""
        reader = SimpleMFRC522()
        try:
            id, text = reader.read()
            rfid = str(id)
            
            # Verificar que sea el mismo docente que registró la entrada
            if self.docente_actual and self.docente_actual['rfid'] == rfid:
                # Registrar salida en la base de datos
                if self.registrar_salida(rfid):
                    self.rfid_label.config(text=f"Salida registrada para ID: {rfid}")
                    self.root.after(2000, self.pantalla_principal)
                else:
                    self.rfid_label.config(text="Error al registrar salida")
            else:
                self.rfid_label.config(text="Tarjeta no coincide con entrada")
                messagebox.showerror("Error", "La tarjeta no coincide con el docente que registró la entrada")
                
        except Exception as e:
            print("Error leyendo salida:", e)
            self.rfid_label.config(text="Error al leer tarjeta")
        finally:
            GPIO.cleanup()

if __name__ == "__main__":
    root = tk.Tk()
    app = RegistroApp(root)
    root.mainloop()