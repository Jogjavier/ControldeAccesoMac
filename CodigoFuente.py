import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import psycopg2
from psycopg2 import sql, Error
#LABORATORIOMAC
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
            'host': '216.225.200.190',
            'database': 'IDSentinel',
            'user': 'Controlacceso',
            'password': 'u%8*i2ie0iQdVGrg',
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
                        'subjects': [],
                        'career_groups': [],
                        'software_type': []
                    }

                    cursor.execute("""
                        SELECT s.id, s.nombre
                        FROM subjects s
                        JOIN teacher_subject ts ON s.id = ts.subject_id
                        WHERE ts.teacher_id = %s
                    """, (docente[0],))
                    self.asignaciones['subjects'] = cursor.fetchall()

                    cursor.execute("""
                        SELECT cg.id, cg.nombre
                        FROM career_groups cg
                        JOIN teacher_career_group tcg ON cg.id = tcg.career_group_id
                        WHERE tcg.teacher_id = %s
                    """, (docente[0],))
                    self.asignaciones['career_groups'] = cursor.fetchall()

                    cursor.execute("""
                        SELECT st.id, st.nombre
                        FROM software_types st
                        JOIN teacher_software_type tst ON st.id = tst.software_type_id
                        WHERE tst.teacher_id = %s
                    """, (docente[0],))
                    self.asignaciones['software_type'] = cursor.fetchall()

                    return docente_info
                return None
        except Error as e:
            print(f"Error al buscar docente: {e}")
            return None
        finally:
            if conn:
                conn.close()


    def registrar_entrada(self, teacher_id, subject_id, career_group_id, software_type_id, num_alumnos):
        """Registra entrada automáticamente como 'ocupado'"""
        conn = self.conectar_db()
        if conn is None:
            return False

        try:
            with conn.cursor() as cursor:
                # Obtener RFID del docente
                cursor.execute("SELECT rfid FROM teachers WHERE id = %s", (teacher_id,))
                docente_data = cursor.fetchone()

                if not docente_data:
                    print("Docente no encontrado")
                    return False

                rfid = docente_data[0]
                fecha_actual = datetime.now().strftime("%Y-%m-%d")
                hora_entrada_actual = datetime.now().strftime("%H:%M:%S")

                # Insertar con estado 'ocupado'
                cursor.execute("""
                    INSERT INTO access_records
                    (teacher_id, rfid, subject_id, career_group_id,
                     software_type_id, num_alumnos, fecha, hora_entrada, estado)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'ocupado')
                """, (teacher_id, rfid, subject_id, career_group_id,
                     software_type_id, num_alumnos, fecha_actual, hora_entrada_actual))

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
        """Versión corregida para registrar salida con sintaxis válida"""
        conn = self.conectar_db()
        if conn is None:
            return False

        try:
            with conn.cursor() as cursor:
                hora_actual = datetime.now().strftime("%H:%M:%S")

                # Primero obtener el ID del último registro sin salida
                cursor.execute("""
                    SELECT ar.id
                    FROM access_records ar
                    JOIN teachers t ON ar.teacher_id = t.id
                    WHERE t.rfid = %s
                    AND ar.hora_salida IS NULL
                    ORDER BY ar.fecha DESC, ar.hora_entrada DESC
                    LIMIT 1
                """, (rfid,))

                registro = cursor.fetchone()

                if registro:
                    # Luego actualizar ese registro específico
                    registro_id = registro[0]
                    cursor.execute("""
                        UPDATE access_records
                        SET hora_salida = %s, estado = 'libre'
                        WHERE id = %s
                    """, (hora_actual, registro_id))

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
        if (not self.asignaciones['subjects'] or
            not self.asignaciones['career_groups'] or
            not self.asignaciones['software_type']):
            messagebox.showerror("Error", "El docente no tiene asignaciones completas")
            return

        self.pantalla_datos()

    def pantalla_datos(self):
        self.limpiar_pantalla()
        tk.Label(self.root, image=self.logo, bg="#f5e0e0").place(x=10, y=10)
        tk.Label(self.root, text="Laboratorio de MAC", font=("Arial", 20, "bold"), fg="#1d127a", bg="#f5e0e0").place(x=280, y=20)

        # Mostrar docente
        nombre_completo = f"{self.docente_actual['nombre']}"
        tk.Label(self.root, text=f"Docente: {nombre_completo}", font=("Arial", 14), bg="#f5e0e0").place(x=250, y=70)

        # Controles originales con datos de la BD
        tk.Label(self.root, text="Total de alumnos:", font=("Arial", 12, "bold"), fg="white", bg="#1d127a").place(x=160, y=120)
        self.total_entry = tk.Entry(self.root, font=("Arial", 12), width=10)
        self.total_entry.place(x=300, y=120)

        tk.Label(self.root, text="Materia:", font=("Arial", 12, "bold"), fg="white", bg="#1d127a").place(x=160, y=180)
        self.subject_combobox = ttk.Combobox(self.root, font=("Arial", 12), width=25, state="readonly")
        self.subject_combobox['values'] = [m[1] for m in self.asignaciones['subjects']]
        self.subject_combobox.place(x=300, y=180)

        tk.Label(self.root, text="Grupo:", font=("rial", 12, "bold"), fg="white", bg="#1d127a").place(x=160, y=240)
        self.career_group_combobox = ttk.Combobox(self.root, font=("Arial", 12), width=25, state="readonly")
        self.career_group_combobox['values'] = [f"{g[1]}" for g in self.asignaciones['career_groups']]
        self.career_group_combobox.place(x=300, y=240)

        tk.Label(self.root, text="Software:", font=("Arial", 12, "bold"), fg="white", bg="#1d127a").place(x=160, y=300)
        self.software_type_combobox = ttk.Combobox(self.root, font=("Arial", 12), width=25, state="readonly")
        self.software_type_combobox['values'] = [s[1] for s in self.asignaciones['software_type']]
        self.software_type_combobox.place(x=300, y=300)

        tk.Button(self.root, text="Continuar", font=("Arial", 14, "bold"),
                 fg="white", bg="#1d127a", command=self.validar_datos).place(x=350, y=380)

    def validar_datos(self):
        if (not self.total_entry.get().isdigit() or
            not self.subject_combobox.get() or
            not self.career_group_combobox.get() or
            not self.software_type_combobox.get()):
            messagebox.showerror("Error", "Complete todos los campos")
            return

        try:
            subject_idx = self.subject_combobox.current()
            career_group_idx = self.career_group_combobox.current()
            software_type_idx = self.software_type_combobox.current()

            if -1 in [subject_idx, career_group_idx, software_type_idx]:
                messagebox.showerror("Error", "Seleccione opciones válidas")
                return

            subject_id = self.asignaciones['subjects'][subject_idx][0]
            career_group_id = self.asignaciones['career_groups'][career_group_idx][0]
            software_type_id = self.asignaciones['software_type'][software_type_idx][0]

            if self.registrar_entrada(
                self.docente_actual['id'],
                subject_id,
                career_group_id,
                software_type_id,
                int(self.total_entry.get())
            ):
                self.datos = {
                    'docente': f"{self.docente_actual['nombre']}",
                    'materia': self.subject_combobox.get(),
                    'grupo': self.career_group_combobox.get(),
                    'software': self.software_type_combobox.get(),
                    'total': self.total_entry.get(),
                    'fecha': datetime.now().strftime("%d/%m/%Y"),
                    'hora': datetime.now().strftime("%H:%M")
                }
                self.pantalla_confirmacion()

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