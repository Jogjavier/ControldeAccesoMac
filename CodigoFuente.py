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
            'host': 'tu_host_remoto',
            'database': 'Prueba',
            'user': 'tu_usuario',
            'password': 'tu_contraseña',
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
                query = sql.SQL("""
                    SELECT id, docente, rfid, materia, grupo, software 
                    FROM prueba 
                    WHERE rfid = %s
                """)
                cursor.execute(query, (rfid,))
                docente = cursor.fetchone()
                
                if docente:
                    return {
                        'id': docente[0],
                        'docente': docente[1],
                        'rfid': docente[2],
                        'materia': docente[3],
                        'grupo': docente[4],
                        'software': docente[5]
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
                    INSERT INTO registros 
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

    def registrar_salida(self, rfid):
        """Registra la salida en la base de datos"""
        conn = self.conectar_db()
        if conn is None:
            return False
            
        try:
            with conn.cursor() as cursor:
                query = sql.SQL("""
                    UPDATE registros 
                    SET salida = NOW() 
                    WHERE rfid = %s AND salida IS NULL
                    ORDER BY entrada DESC
                    LIMIT 1
                """)
                cursor.execute(query, (rfid,))
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
        self.docente_actual = None  # Resetear docente al volver a la pantalla principal
        
        tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
        tk.Label(self.root, text="Laboratorio de MAC", font=("Arial", 24, "bold"), fg="#1d127a", bg="#f5e0e0").pack(pady=(100, 20))
        tk.Label(self.root, text="Aproximar Tarjeta", font=("Arial", 18), fg="#1d127a", bg="#f5e0e0").pack()

        # Etiqueta para mostrar información del docente
        self.docente_label = tk.Label(self.root, text="", font=("Arial", 14), fg="black", bg="#f5e0e0")
        self.docente_label.pack(pady=(0, 10))

        self.rfid_label = tk.Label(self.root, text="Esperando tarjeta...", font=("Arial", 16), fg="black", bg="#f5e0e0")
        self.rfid_label.pack(pady=(0, 20))

        # Etiqueta para mostrar datos asignados
        self.datos_asignados_label = tk.Label(self.root, text="", font=("Arial", 12), fg="black", bg="#f5e0e0", wraplength=600)
        self.datos_asignados_label.pack(pady=(0, 20))

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
                
                # Mostrar datos asignados
                datos_text = f"Materia: {self.docente_actual['materia']}\n"
                datos_text += f"Grupo: {self.docente_actual['grupo']}\n"
                datos_text += f"Software: {self.docente_actual['software']}"
                self.datos_asignados_label.config(text=datos_text)
                
                self.btn_continuar.config(state=tk.NORMAL)
            else:
                self.rfid_label.config(text="Docente no registrado")
                self.docente_label.config(text="")
                self.datos_asignados_label.config(text="")
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
        
        # Pasar directamente a la pantalla de confirmación con los datos del docente
        self.datos["materia"] = self.docente_actual['materia']
        self.datos["grupo"] = self.docente_actual['grupo']
        self.datos["software"] = self.docente_actual['software']
        self.datos["fecha"] = datetime.now().strftime("%d/%m/%Y")
        self.datos["hora"] = datetime.now().strftime("%H:%M")
        
        self.pantalla_confirmacion()

    def pantalla_confirmacion(self):
        """Muestra la pantalla de confirmación de datos"""
        self.limpiar_pantalla()
        tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
        tk.Label(self.root, text="Laboratorio de MAC", font=("Arial", 22, "bold"), fg="navy", bg="#f5e0e0").pack(pady=20)

        datos = self.datos
        
        # Mostrar información del docente
        tk.Label(self.root, text=f"Docente: {self.docente_actual['docente']}", 
                font=("Arial", 16), bg="white", width=40).place(x=200, y=70)

        etiquetas = [
            f"Entrada: {datos['hora']}", 
            datos["fecha"], 
            f"Grupo: {datos['grupo']}",
            f"Materia: {datos['materia']}", 
            f"Software: {datos['software']}"
        ]

        for i, txt in enumerate(etiquetas):
            y = 120 + i * 40
            tk.Label(self.root, text=txt, font=("Arial", 14), bg="white", width=40).place(x=200, y=y)

        tk.Label(self.root, text="Total de alumnos:", font=("Arial", 14), bg="#f5e0e0").place(x=200, y=320)
        self.total_entry = tk.Entry(self.root, font=("Arial", 14), width=10, justify='center')
        self.total_entry.place(x=400, y=320)

        tk.Button(self.root, text="Atras", font=("Arial", 14), bg="navy", fg="white", width=12, command=self.pantalla_principal).place(x=220, y=380)
        tk.Button(self.root, text="Confirmar", font=("Arial", 14), bg="navy", fg="white", width=12, command=self.confirmar_registro).place(x=420, y=380)

    def confirmar_registro(self):
        """Confirma el registro en la base de datos"""
        if not self.total_entry.get().isdigit():
            messagebox.showerror("Error", "Por favor ingrese un número válido de alumnos")
            return

        total_alumnos = self.total_entry.get()
        
        if self.registrar_entrada(
            self.docente_actual['rfid'],
            self.docente_actual['docente'],
            total_alumnos,
            self.docente_actual['materia'],
            self.docente_actual['grupo'],
            self.docente_actual['software']
        ):
            self.datos["total"] = total_alumnos
            self.pantalla_exito()
        else:
            messagebox.showerror("Error", "No se pudo registrar la entrada en la base de datos")

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