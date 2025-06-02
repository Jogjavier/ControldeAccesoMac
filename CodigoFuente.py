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
        self.root.geometry("1000x700")
        self.root.configure(bg="#f5e0e0")
        self.logo = tk.PhotoImage(file="logo.png")
        self.datos = {}
        self.docente_actual = None
        self.asignaciones = {}
        
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
                # Obtener información básica del docente
                query = sql.SQL("""
                    SELECT id, nombre, apellido, rfid 
                    FROM docentes 
                    WHERE rfid = %s
                """)
                cursor.execute(query, (rfid,))
                docente = cursor.fetchone()
                
                if docente:
                    docente_info = {
                        'id': docente[0],
                        'nombre': docente[1],
                        'apellido': docente[2],
                        'rfid': docente[3]
                    }
                    
                    # Obtener asignaciones del docente
                    self.asignaciones = self.obtener_asignaciones_docente(docente[0])
                    
                    return docente_info
                return None
        except Error as e:
            print(f"Error al buscar docente: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def obtener_asignaciones_docente(self, docente_id):
        """Obtiene todas las asignaciones del docente"""
        conn = self.conectar_db()
        if conn is None:
            return {}
            
        try:
            asignaciones = {
                'materias': [],
                'grupos': [],
                'software': []
            }
            
            with conn.cursor() as cursor:
                # Obtener materias asignadas
                cursor.execute("""
                    SELECT m.id, m.nombre 
                    FROM materias m
                    JOIN docente_materia dm ON m.id = dm.materia_id
                    WHERE dm.docente_id = %s
                """, (docente_id,))
                asignaciones['materias'] = cursor.fetchall()
                
                # Obtener grupos asignados
                cursor.execute("""
                    SELECT g.id, g.nombre, g.carrera 
                    FROM grupos g
                    JOIN docente_grupo dg ON g.id = dg.grupo_id
                    WHERE dg.docente_id = %s
                """, (docente_id,))
                asignaciones['grupos'] = cursor.fetchall()
                
                # Obtener software asignado
                cursor.execute("""
                    SELECT s.id, s.nombre 
                    FROM software s
                    JOIN docente_software ds ON s.id = ds.software_id
                    WHERE ds.docente_id = %s
                """, (docente_id,))
                asignaciones['software'] = cursor.fetchall()
                
            return asignaciones
        except Error as e:
            print(f"Error al obtener asignaciones: {e}")
            return {}
        finally:
            if conn:
                conn.close()

    def registrar_entrada(self, docente_id, materia_id, grupo_id, software_id, total_alumnos):
        """Registra una entrada en la base de datos"""
        conn = self.conectar_db()
        if conn is None:
            return False
            
        try:
            with conn.cursor() as cursor:
                query = sql.SQL("""
                    INSERT INTO registros_acceso 
                    (docente_id, materia_id, grupo_id, software_id, total_alumnos, entrada) 
                    VALUES (%s, %s, %s, %s, %s, NOW())
                """)
                cursor.execute(query, (docente_id, materia_id, grupo_id, software_id, total_alumnos))
                conn.commit()
                return True
        except Error as e:
            print(f"Error al registrar entrada: {e}")
            conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def registrar_salida(self, docente_id):
        """Registra la salida en la base de datos"""
        conn = self.conectar_db()
        if conn is None:
            return False
            
        try:
            with conn.cursor() as cursor:
                query = sql.SQL("""
                    UPDATE registros_acceso 
                    SET salida = NOW() 
                    WHERE docente_id = %s AND salida IS NULL
                    ORDER BY entrada DESC
                    LIMIT 1
                """)
                cursor.execute(query, (docente_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Error as e:
            print(f"Error al registrar salida: {e}")
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
        self.asignaciones = {}
        
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
                nombre_completo = f"{self.docente_actual['nombre']} {self.docente_actual['apellido']}"
                self.docente_label.config(text=f"Docente: {nombre_completo}")
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
        if not self.docente_actual:
            messagebox.showerror("Error", "No se ha detectado ninguna tarjeta válida")
            return
        
        # Verificar que el docente tenga asignaciones
        if not self.asignaciones['materias'] or not self.asignaciones['grupos'] or not self.asignaciones['software']:
            messagebox.showerror("Error", "El docente no tiene asignaciones completas (materias, grupos o software)")
            return
            
        self.pantalla_seleccion_datos()

    def pantalla_seleccion_datos(self):
        """Muestra la pantalla para seleccionar datos de las asignaciones"""
        self.limpiar_pantalla()
        tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
        
        # Mostrar información del docente
        nombre_completo = f"{self.docente_actual['nombre']} {self.docente_actual['apellido']}"
        tk.Label(self.root, text=f"Docente: {nombre_completo}", font=("Arial", 16), bg="#f5e0e0").pack(pady=10)
        
        # Frame principal para los combobox
        frame_principal = tk.Frame(self.root, bg="#f5e0e0")
        frame_principal.pack(pady=20, fill=tk.BOTH, expand=True)
        
        # Materias
        frame_materias = tk.LabelFrame(frame_principal, text="Materias Asignadas", font=("Arial", 12, "bold"), bg="#f5e0e0")
        frame_materias.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self.materia_combobox = ttk.Combobox(frame_materias, font=("Arial", 12), state="readonly")
        self.materia_combobox['values'] = [m[1] for m in self.asignaciones['materias']]
        self.materia_combobox.pack(padx=10, pady=10, fill=tk.X)
        
        # Grupos
        frame_grupos = tk.LabelFrame(frame_principal, text="Grupos Asignados", font=("Arial", 12, "bold"), bg="#f5e0e0")
        frame_grupos.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self.grupo_combobox = ttk.Combobox(frame_grupos, font=("Arial", 12), state="readonly")
        self.grupo_combobox['values'] = [f"{g[1]} - {g[2]}" for g in self.asignaciones['grupos']]
        self.grupo_combobox.pack(padx=10, pady=10, fill=tk.X)
        
        # Software
        frame_software = tk.LabelFrame(frame_principal, text="Software Asignado", font=("Arial", 12, "bold"), bg="#f5e0e0")
        frame_software.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self.software_combobox = ttk.Combobox(frame_software, font=("Arial", 12), state="readonly")
        self.software_combobox['values'] = [s[1] for s in self.asignaciones['software']]
        self.software_combobox.pack(padx=10, pady=10, fill=tk.X)
        
        # Total de alumnos
        frame_alumnos = tk.Frame(self.root, bg="#f5e0e0")
        frame_alumnos.pack(pady=20)
        
        tk.Label(frame_alumnos, text="Total de alumnos:", font=("Arial", 12), bg="#f5e0e0").pack(side=tk.LEFT)
        self.total_entry = tk.Entry(frame_alumnos, font=("Arial", 12), width=10)
        self.total_entry.pack(side=tk.LEFT, padx=10)
        
        # Botones
        frame_botones = tk.Frame(self.root, bg="#f5e0e0")
        frame_botones.pack(pady=20)
        
        tk.Button(frame_botones, text="Atrás", font=("Arial", 14), bg="gray", fg="white", 
                 command=self.pantalla_principal).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_botones, text="Registrar", font=("Arial", 14), bg="#1d127a", fg="white",
                 command=self.registrar_datos).pack(side=tk.LEFT, padx=10)

    def registrar_datos(self):
        """Registra los datos seleccionados en la base de datos"""
        # Validar selecciones
        if (not self.materia_combobox.get() or not self.grupo_combobox.get() or 
            not self.software_combobox.get() or not self.total_entry.get().isdigit()):
            messagebox.showerror("Error", "Por favor complete todos los campos correctamente")
            return
            
        try:
            # Obtener IDs de las selecciones
            materia_idx = self.materia_combobox.current()
            grupo_idx = self.grupo_combobox.current()
            software_idx = self.software_combobox.current()
            
            if materia_idx == -1 or grupo_idx == -1 or software_idx == -1:
                messagebox.showerror("Error", "Seleccione todas las opciones")
                return
                
            materia_id = self.asignaciones['materias'][materia_idx][0]
            grupo_id = self.asignaciones['grupos'][grupo_idx][0]
            software_id = self.asignaciones['software'][software_idx][0]
            total_alumnos = int(self.total_entry.get())
            
            # Registrar en la base de datos
            if self.registrar_entrada(
                self.docente_actual['id'],
                materia_id,
                grupo_id,
                software_id,
                total_alumnos
            ):
                self.datos = {
                    'docente': f"{self.docente_actual['nombre']} {self.docente_actual['apellido']}",
                    'materia': self.materia_combobox.get(),
                    'grupo': self.grupo_combobox.get(),
                    'software': self.software_combobox.get(),
                    'total_alumnos': total_alumnos,
                    'fecha': datetime.now().strftime("%d/%m/%Y"),
                    'hora': datetime.now().strftime("%H:%M")
                }
                self.pantalla_confirmacion()
            else:
                messagebox.showerror("Error", "No se pudo registrar el acceso")
                
        except Exception as e:
            print(f"Error al registrar datos: {e}")
            messagebox.showerror("Error", "Ocurrió un error al registrar los datos")

    def pantalla_confirmacion(self):
        """Muestra la pantalla de confirmación de registro"""
        self.limpiar_pantalla()
        tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
        tk.Label(self.root, text="Registro Exitoso", font=("Arial", 20, "bold"), bg="#f5e0e0").pack(pady=20)
        
        # Frame para los datos
        frame_datos = tk.Frame(self.root, bg="#f5e0e0")
        frame_datos.pack(pady=20)
        
        # Mostrar datos del registro
        tk.Label(frame_datos, text=f"Docente: {self.datos['docente']}", font=("Arial", 14), bg="#f5e0e0").grid(row=0, column=0, sticky="w", pady=5)
        tk.Label(frame_datos, text=f"Materia: {self.datos['materia']}", font=("Arial", 14), bg="#f5e0e0").grid(row=1, column=0, sticky="w", pady=5)
        tk.Label(frame_datos, text=f"Grupo: {self.datos['grupo']}", font=("Arial", 14), bg="#f5e0e0").grid(row=2, column=0, sticky="w", pady=5)
        tk.Label(frame_datos, text=f"Software: {self.datos['software']}", font=("Arial", 14), bg="#f5e0e0").grid(row=3, column=0, sticky="w", pady=5)
        tk.Label(frame_datos, text=f"Total alumnos: {self.datos['total_alumnos']}", font=("Arial", 14), bg="#f5e0e0").grid(row=4, column=0, sticky="w", pady=5)
        tk.Label(frame_datos, text=f"Hora de entrada: {self.datos['hora']}", font=("Arial", 14), bg="#f5e0e0").grid(row=5, column=0, sticky="w", pady=5)
        tk.Label(frame_datos, text=f"Fecha: {self.datos['fecha']}", font=("Arial", 14), bg="#f5e0e0").grid(row=6, column=0, sticky="w", pady=5)
        
        # Botones
        frame_botones = tk.Frame(self.root, bg="#f5e0e0")
        frame_botones.pack(pady=20)
        
        tk.Button(frame_botones, text="Registrar Salida", font=("Arial", 14), bg="#1d127a", fg="white",
                 command=self.pantalla_salida).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_botones, text="Finalizar", font=("Arial", 14), bg="gray", fg="white",
                 command=self.pantalla_principal).pack(side=tk.LEFT, padx=10)

    def pantalla_salida(self):
        """Muestra la pantalla para registrar salida"""
        self.limpiar_pantalla()
        tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
        tk.Label(self.root, text="Registrar Salida", font=("Arial", 20, "bold"), bg="#f5e0e0").pack(pady=20)
        tk.Label(self.root, text="Aproxime su tarjeta para registrar la salida", font=("Arial", 14), bg="#f5e0e0").pack(pady=10)
        
        self.rfid_label = tk.Label(self.root, text="Esperando tarjeta...", font=("Arial", 14), bg="#f5e0e0")
        self.rfid_label.pack(pady=20)
        
        tk.Button(self.root, text="Cancelar", font=("Arial", 14), bg="gray", fg="white",
                 command=self.pantalla_principal).pack(pady=10)

        # Iniciar lectura de RFID para salida
        threading.Thread(target=self.leer_salida_rfid, daemon=True).start()

    def leer_salida_rfid(self):
        """Lee el RFID para registrar la salida"""
        reader = SimpleMFRC522()
        try:
            id, text = reader.read()
            rfid = str(id)
            
            # Verificar que sea el mismo docente
            if self.docente_actual and self.docente_actual['rfid'] == rfid:
                if self.registrar_salida(self.docente_actual['id']):
                    self.rfid_label.config(text=f"Salida registrada a las {datetime.now().strftime('%H:%M')}")
                    self.root.after(3000, self.pantalla_principal)
                else:
                    self.rfid_label.config(text="Error al registrar salida")
            else:
                self.rfid_label.config(text="Tarjeta no coincide")
                messagebox.showerror("Error", "La tarjeta no coincide con el docente registrado")
                
        except Exception as e:
            print(f"Error al leer salida: {e}")
            self.rfid_label.config(text="Error al leer tarjeta")
        finally:
            GPIO.cleanup()

if __name__ == "__main__":
    root = tk.Tk()
    app = RegistroApp(root)
    root.mainloop()