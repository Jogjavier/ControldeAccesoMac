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
        self.asignaciones = {}
        
        # Configuración de la base de datos
        self.db_config = {
            'host': '192.168.1.40',
            'database': 'IDSentinel',
            'user': 'javier',
            'password': '1234',
            'port': '5432'
        }
        
        self.pantalla_principal()

    def conectar_db(self):
        """Establece conexión con PostgreSQL"""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Error as e:
            print(f"Error al conectar a PostgreSQL: {e}")
            messagebox.showerror("Error", "No se pudo conectar a la base de datos")
            return None

    def buscar_docente_por_rfid(self, rfid):
        """Busca docente por RFID y obtiene sus asignaciones"""
        conn = self.conectar_db()
        if conn is None:
            return None
            
        try:
            with conn.cursor() as cursor:
                # Obtener docente
                cursor.execute("""
                    SELECT id, nombre, rfid 
                    FROM teachers 
                    WHERE rfid = %s
                """, (rfid,))
                docente = cursor.fetchone()
                
                if docente:
                    docente_info = {
                        'id': docente[0],
                        'nombre': docente[1],
                        'rfid': docente[2]
                    }
                    
                    # Obtener asignaciones
                    self.asignaciones = {
                        'materias': [],
                        'grupos': [],
                        'software': []
                    }
                    
                    cursor.execute("""
                        SELECT m.id, m.nombre 
                        FROM materias m
                        JOIN docente_materia dm ON m.id = dm.materia_id
                        WHERE dm.docente_id = %s
                    """, (docente[0],))
                    self.asignaciones['materias'] = cursor.fetchall()
                    
                    cursor.execute("""
                        SELECT g.id, g.nombre, g.carrera 
                        FROM grupos g
                        JOIN docente_grupo dg ON g.id = dg.grupo_id
                        WHERE dg.docente_id = %s
                    """, (docente[0],))
                    self.asignaciones['grupos'] = cursor.fetchall()
                    
                    cursor.execute("""
                        SELECT s.id, s.nombre 
                        FROM software s
                        JOIN docente_software ds ON s.id = ds.software_id
                        WHERE ds.docente_id = %s
                    """, (docente[0],))
                    self.asignaciones['software'] = cursor.fetchall()
                    
                    return docente_info
                return None
        except Error as e:
            print(f"Error al buscar docente: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def registrar_entrada(self, docente_id, materia, grupo, software, total_alumnos):
        """Registra entrada en la tabla prueba con todos los campos"""
        conn = self.conectar_db()
        if conn is None:
            return False
            
        try:
            with conn.cursor() as cursor:
                # Obtener datos del docente
                cursor.execute("""
                    SELECT rfid, nombre  
                    FROM docentes 
                    WHERE id = %s
                """, (docente_id,))
                docente_data = cursor.fetchone()
                
                if not docente_data:
                    print("Docente no encontrado")
                    return False
                    
                rfid = docente_data[0]
                nombre_docente = docente_data[1]
                
                # Insertar en tabla prueba con todos los campos
                cursor.execute("""
                    INSERT INTO prueba 
                    (rfid, docente, totalumnos, materia, grupo, software, entrada) 
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """, (rfid, nombre_docente, total_alumnos, materia, grupo, software))
                
                conn.commit()
                return True
        except Error as e:
            print(f"Error al registrar entrada: {e}")
            conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def registrar_salida(self, rfid):
        """Versión corregida para registrar salida"""
        conn = self.conectar_db()
        if conn is None:
            return False
            
        try:
            with conn.cursor() as cursor:
                # 1. Obtener el último registro sin salida
                cursor.execute("""
                    SELECT id FROM prueba 
                    WHERE rfid = %s AND salida IS NULL 
                    ORDER BY entrada DESC LIMIT 1
                """, (str(rfid),))  # Asegurar que rfid sea string
                
                registro = cursor.fetchone()
                
                if registro:
                    # 2. Actualizar solo ese registro
                    cursor.execute("""
                        UPDATE prueba 
                        SET salida = NOW() 
                        WHERE id = %s
                    """, (registro[0],))
                    conn.commit()
                    return True
                return False
        except Error as e:
            print(f"Error al registrar salida: {e}")
            conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def limpiar_pantalla(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def pantalla_principal(self):
        self.limpiar_pantalla()
        self.docente_actual = None
        
        # Logo y título (posición original)
        tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
        tk.Label(self.root, text="Laboratorio de MAC", font=("Arial", 24, "bold"), 
                fg="#1d127a", bg="#f5e0e0").pack(pady=(50, 10))  # Reducido pady superior
        
        # Etiqueta para "Aproximar Tarjeta"
        tk.Label(self.root, text="Aproximar Tarjeta", font=("Arial", 18), 
                fg="#1d127a", bg="#f5e0e0").pack()
        
        # Etiqueta para estado del RFID (posición ajustada)
        self.rfid_label = tk.Label(self.root, text="Esperando tarjeta...", 
                                font=("Arial", 16), fg="black", bg="#f5e0e0")
        self.rfid_label.pack(pady=(10, 5))  # Espaciado reducido
        
        # Etiqueta para nombre del docente (nueva posición)
        self.docente_label = tk.Label(self.root, text="", font=("Arial", 14, "bold"), 
                                    fg="#1d127a", bg="#f5e0e0")
        self.docente_label.pack(pady=(5, 20))  # Espaciado ajustado
        
        # Botón Continuar (posición más arriba)
        self.btn_continuar = tk.Button(self.root, text="Continuar", 
                                    font=("Arial", 16, "bold"), 
                                    fg="white", bg="#1d127a", 
                                    state=tk.DISABLED,
                                    command=self.validar_rfid)
        self.btn_continuar.pack(pady=(0, 50))  # Movido más arriba
        
        # Iniciar lectura RFID
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
                nombre_completo = f"Docente: {self.docente_actual['nombre']}"
                self.docente_label.config(text=nombre_completo)  # Actualiza la etiqueta
                self.btn_continuar.config(state=tk.NORMAL)
            else:
                self.rfid_label.config(text="Docente no registrado")
                self.docente_label.config(text="")  # Limpia el nombre
                messagebox.showerror("Error", "Docente no encontrado en la base de datos")
                
        except Exception as e:
            print("Error leyendo RFID:", e)
            self.rfid_label.config(text="Error al leer tarjeta")
        finally:
            GPIO.cleanup()
    def validar_rfid(self):
        if not self.docente_actual:
            messagebox.showerror("Error", "No se detectó tarjeta válida")
            return
            
        # Verificar asignaciones mínimas
        if (not self.asignaciones['materias'] or 
            not self.asignaciones['grupos'] or 
            not self.asignaciones['software']):
            messagebox.showerror("Error", "El docente no tiene asignaciones completas")
            return
            
        self.pantalla_datos()

    def pantalla_datos(self):
        self.limpiar_pantalla()
        tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
        tk.Label(self.root, text="Laboratorio de MAC", font=("Arial", 20, "bold"), fg="#1d127a", bg="#f5e0e0").place(x=280, y=20)
        
        # Mostrar docente
        nombre_completo = f"{self.docente_actual['nombre']} {self.docente_actual['apellido']}"
        tk.Label(self.root, text=f"Docente: {nombre_completo}", font=("Arial", 14), bg="#f5e0e0").place(x=250, y=70)

        # Controles originales con datos de la BD
        tk.Label(self.root, text="Total de alumnos:", font=("Arial", 12, "bold"), fg="white", bg="#1d127a").place(x=160, y=120)
        self.total_entry = tk.Entry(self.root, font=("Arial", 12), width=10)
        self.total_entry.place(x=300, y=120)

        tk.Label(self.root, text="Materia:", font=("Arial", 12, "bold"), fg="white", bg="#1d127a").place(x=160, y=180)
        self.materia_combobox = ttk.Combobox(self.root, font=("Arial", 12), width=25, state="readonly")
        self.materia_combobox['values'] = [m[1] for m in self.asignaciones['materias']]
        self.materia_combobox.place(x=300, y=180)

        tk.Label(self.root, text="Grupo:", font=("Arial", 12, "bold"), fg="white", bg="#1d127a").place(x=160, y=240)
        self.grupo_combobox = ttk.Combobox(self.root, font=("Arial", 12), width=25, state="readonly")
        self.grupo_combobox['values'] = [f"{g[1]} ({g[2]})" for g in self.asignaciones['grupos']]
        self.grupo_combobox.place(x=300, y=240)

        tk.Label(self.root, text="Software:", font=("Arial", 12, "bold"), fg="white", bg="#1d127a").place(x=160, y=300)
        self.software_combobox = ttk.Combobox(self.root, font=("Arial", 12), width=25, state="readonly")
        self.software_combobox['values'] = [s[1] for s in self.asignaciones['software']]
        self.software_combobox.place(x=300, y=300)

        tk.Button(self.root, text="Continuar", font=("Arial", 14, "bold"), 
                 fg="white", bg="#1d127a", command=self.validar_datos).place(x=350, y=380)

    def validar_datos(self):
        if (not self.total_entry.get().isdigit() or 
            not self.materia_combobox.get() or 
            not self.grupo_combobox.get() or 
            not self.software_combobox.get()):
            messagebox.showerror("Error", "Complete todos los campos")
            return
            
        try:
            materia_idx = self.materia_combobox.current()
            grupo_idx = self.grupo_combobox.current()
            software_idx = self.software_combobox.current()
            
            if -1 in [materia_idx, grupo_idx, software_idx]:
                messagebox.showerror("Error", "Seleccione opciones válidas")
                return
                
            # Para la Opción 1 (nombres directos):
            if self.registrar_entrada(
                self.docente_actual['id'],
                self.materia_combobox.get(),  # Nombre materia
                self.grupo_combobox.get(),    # Nombre grupo
                self.software_combobox.get(), # Nombre software
                int(self.total_entry.get())   # Total alumnos
            ):
                self.datos = {
                    'docente': f"{self.docente_actual['nombre']} {self.docente_actual['apellido']}",
                    'materia': self.materia_combobox.get(),
                    'grupo': self.grupo_combobox.get(),
                    'software': self.software_combobox.get(),
                    'total': self.total_entry.get(),
                    'fecha': datetime.now().strftime("%d/%m/%Y"),
                    'hora': datetime.now().strftime("%H:%M")
                }
                self.pantalla_confirmacion()
                
            # Para la Opción 2 (usando IDs):
            """
            materia_id = self.asignaciones['materias'][materia_idx][0]
            grupo_id = self.asignaciones['grupos'][grupo_idx][0]
            software_id = self.asignaciones['software'][software_idx][0]
            
            if self.registrar_entrada(
                self.docente_actual['id'],
                materia_id,
                grupo_id,
                software_id,
                int(self.total_entry.get())
            ):
                # ... resto del código
            """
                
        except Exception as e:
            print(f"Error al validar datos: {e}")
            messagebox.showerror("Error", "Ocurrió un error al registrar")

    def pantalla_confirmacion(self):
        self.limpiar_pantalla()
        tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
        tk.Label(self.root, text="Laboratorio de MAC", font=("Arial", 22, "bold"), 
                fg="navy", bg="#f5e0e0").pack(pady=(30, 20))  # Ajuste de espacio
        
        # Mostrar datos con nuevo espaciado
        datos = self.datos
        etiquetas = [
            f"Docente: {datos['docente']}",
            f"Materia: {datos['materia']}",
            f"Grupo: {datos['grupo']}",
            f"Software: {datos['software']}",
            f"Total Alumnos: {datos['total']}",
            f"Fecha: {datos['fecha']}",
            f"Hora Entrada: {datos['hora']}"
        ]

        for i, texto in enumerate(etiquetas):
            tk.Label(self.root, text=texto, font=("Arial", 14), 
                    bg="white", width=30).place(x=250, y=100 + i*35)  # Posición ajustada
        
        # Botones más arriba
        tk.Button(self.root, text="Atrás", font=("Arial", 14), 
                bg="navy", fg="white", width=10,
                command=self.pantalla_datos).place(x=250, y=350)  # Posición ajustada
        tk.Button(self.root, text="Confirmar", font=("Arial", 14), 
                bg="navy", fg="white", width=10,
                command=self.pantalla_exito).place(x=400, y=350)  # Posición ajustada

    def pantalla_exito(self):
        self.limpiar_pantalla()
        tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
        tk.Label(self.root, text="Registro Exitoso", font=("Arial", 20, "bold"), 
                bg="lime", fg="black", width=30).pack(pady=(80, 30))  # Ajuste de posición
    
        # Botón más arriba
        tk.Button(self.root, text="Registrar Salida", font=("Arial", 16), 
                bg="#1d127a", fg="white", command=self.pantalla_salida).pack(pady=10)
    def pantalla_salida(self):
        self.limpiar_pantalla()
        tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
        tk.Label(self.root, text="Registrar Salida", font=("Arial", 24, "bold"), fg="#1d127a", bg="#f5e0e0").pack(pady=100)
        tk.Label(self.root, text="Aproxime su tarjeta", font=("Arial", 18), fg="#1d127a", bg="#f5e0e0").pack()

        self.rfid_label = tk.Label(self.root, text="Esperando tarjeta...", font=("Arial", 18), fg="black", bg="#f5e0e0")
        self.rfid_label.pack(pady=20)

        threading.Thread(target=self.leer_salida_rfid, daemon=True).start()

    def leer_salida_rfid(self):
        reader = SimpleMFRC522()
        try:
            id, text = reader.read()
            rfid = str(id)  # Convertir a string siempre
            
            if self.docente_actual and str(self.docente_actual['rfid']) == rfid:
                if self.registrar_salida(rfid):  # Pasar el RFID como string
                    self.rfid_label.config(text=f"Salida registrada para ID: {rfid}")
                    self.root.after(2000, self.pantalla_principal)
                else:
                    self.rfid_label.config(text="Error al registrar salida")
            else:
                self.rfid_label.config(text="Tarjeta no coincide con entrada")
                messagebox.showerror("Error", "La tarjeta no coincide con el docente registrado")
                
        except Exception as e:
            print("Error leyendo salida:", e)
            self.rfid_label.config(text="Error al leer tarjeta")
        finally:
            GPIO.cleanup()

if __name__ == "__main__":
    root = tk.Tk()
    app = RegistroApp(root)
    root.mainloop()