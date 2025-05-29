import tkinter as tk
from tkinter import messagebox, StringVar, Listbox, Scrollbar
import threading
from mfrc522 import SimpleMFRC522

# -----------------------------
# Configuración del lector RFID
# -----------------------------
lector = SimpleMFRC522()

# -----------------------------
# Función para leer RFID en hilo
# -----------------------------
def leer_rfid(entry_var):
    try:
        print("Esperando tarjeta RFID...")
        id, texto = lector.read()
        print(f"ID leído: {id}")
        entry_var.set(str(id))
    except Exception as e:
        print("Error al leer RFID:", e)

# -----------------------------
# Configuración de la ventana principal
# -----------------------------
ventana = tk.Tk()
ventana.title("Registro de Uso de Laboratorio")
ventana.geometry("800x600")

pantalla_actual = None

def cambiar_pantalla(nueva_pantalla):
    global pantalla_actual
    if pantalla_actual:
        pantalla_actual.pack_forget()
    nueva_pantalla.pack(fill="both", expand=True)
    pantalla_actual = nueva_pantalla

# -----------------------------
# Variables compartidas
# -----------------------------
nombre = StringVar()
fecha = StringVar()
hora_entrada = StringVar()
hora_salida = StringVar()
rfid_id_entrada = StringVar()
rfid_id_salida = StringVar()
materia = StringVar()
grupo = StringVar()
carrera = StringVar()
numero_alumnos = StringVar()
tipo_uso_software = StringVar()

# -----------------------------
# PANTALLA 1: Registro de entrada
# -----------------------------
pantalla1_frame = tk.Frame(ventana, bg="#f5e0e0")
tk.Label(pantalla1_frame, text="Bienvenido al Laboratorio CC1", font=("Arial", 24, "bold"), fg="#1d127a", bg="#f5e0e0").pack(pady=40)
tk.Button(pantalla1_frame, text="Registrar Entrada", font=("Arial", 18), bg="#7e6bf2", fg="white", command=lambda: cambiar_pantalla(pantalla2_frame)).pack(pady=20)

# Entrada de RFID
tk.Label(pantalla1_frame, text="Aproxima tu tarjeta RFID", font=("Arial", 14), fg="#1d127a", bg="#f5e0e0").pack()
tk.Entry(pantalla1_frame, textvariable=rfid_id_entrada, font=("Arial", 14), justify='center', width=30).pack(pady=10)
tk.Button(pantalla1_frame, text="Leer Tarjeta", font=("Arial", 14, "bold"), bg="#1d127a", fg="white",
          command=lambda: threading.Thread(target=leer_rfid, args=(rfid_id_entrada,)).start()).pack()

# -----------------------------
# PANTALLA 2: Formulario de datos
# -----------------------------
pantalla2_frame = tk.Frame(ventana, bg="#e0f5ec")
tk.Label(pantalla2_frame, text="Formulario de Registro", font=("Arial", 20, "bold"), bg="#e0f5ec").pack(pady=20)

campos = [
    ("Nombre del docente", nombre),
    ("Fecha", fecha),
    ("Hora de entrada", hora_entrada),
    ("Materia", materia),
    ("Grupo", grupo),
    ("Carrera", carrera),
    ("Número de alumnos", numero_alumnos),
    ("Tipo de uso del software", tipo_uso_software)
]

for texto, variable in campos:
    tk.Label(pantalla2_frame, text=texto, font=("Arial", 14), bg="#e0f5ec").pack()
    tk.Entry(pantalla2_frame, textvariable=variable, font=("Arial", 14), width=30).pack(pady=5)

def registrar_datos():
    datos = {
        "RFID Entrada": rfid_id_entrada.get(),
        "Nombre": nombre.get(),
        "Fecha": fecha.get(),
        "Hora Entrada": hora_entrada.get(),
        "Materia": materia.get(),
        "Grupo": grupo.get(),
        "Carrera": carrera.get(),
        "Alumnos": numero_alumnos.get(),
        "Tipo Uso": tipo_uso_software.get()
    }

    if any(v == "" for v in datos.values()):
        messagebox.showwarning("Campos incompletos", "Por favor completa todos los campos.")
        return

    info = "\n".join([f"{k}: {v}" for k, v in datos.items()])
    messagebox.showinfo("Registro exitoso", f"Datos registrados:\n\n{info}")
    cambiar_pantalla(pantalla3_frame)

tk.Button(pantalla2_frame, text="Registrar", font=("Arial", 16, "bold"), bg="#5cb85c", fg="white", command=registrar_datos).pack(pady=20)

# -----------------------------
# PANTALLA 3: Confirmación y botón de salida
# -----------------------------
pantalla3_frame = tk.Frame(ventana, bg="#e0f5ec")
tk.Label(pantalla3_frame, text="Registro Exitoso", font=("Arial", 24, "bold"), bg="#e0f5ec", fg="#1d127a").pack(pady=40)
tk.Button(pantalla3_frame, text="Registrar Salida", font=("Arial", 18), bg="#f0ad4e", fg="white", command=lambda: cambiar_pantalla(pantalla4_frame)).pack(pady=20)

# -----------------------------
# PANTALLA 4: Registro de salida con RFID
# -----------------------------
pantalla4_frame = tk.Frame(ventana, bg="#e0f0ff")
tk.Label(pantalla4_frame, text="Registrar Salida", font=("Arial", 24, "bold"), bg="#e0f0ff", fg="#1d127a").pack(pady=40)

tk.Label(pantalla4_frame, text="Aproxima tu tarjeta RFID", font=("Arial", 14), fg="#1d127a", bg="#e0f0ff").pack()
tk.Entry(pantalla4_frame, textvariable=rfid_id_salida, font=("Arial", 14), justify='center', width=30).pack(pady=10)
tk.Button(pantalla4_frame, text="Leer Tarjeta", font=("Arial", 14, "bold"), bg="#1d127a", fg="white",
          command=lambda: threading.Thread(target=leer_rfid, args=(rfid_id_salida,)).start()).pack()

tk.Label(pantalla4_frame, text="Hora de salida", font=("Arial", 14), bg="#e0f0ff").pack()
tk.Entry(pantalla4_frame, textvariable=hora_salida, font=("Arial", 14), width=30).pack(pady=5)

def finalizar_registro():
    datos_salida = {
        "RFID Salida": rfid_id_salida.get(),
        "Hora Salida": hora_salida.get()
    }

    if any(v == "" for v in datos_salida.values()):
        messagebox.showwarning("Campos incompletos", "Por favor completa todos los campos.")
        return

    info = "\n".join([f"{k}: {v}" for k, v in datos_salida.items()])
    messagebox.showinfo("Salida registrada", f"Datos:\n\n{info}")
    cambiar_pantalla(pantalla1_frame)

tk.Button(pantalla4_frame, text="Finalizar", font=("Arial", 16, "bold"), bg="#5cb85c", fg="white", command=finalizar_registro).pack(pady=20)

# -----------------------------
# Iniciar la aplicación
# -----------------------------
cambiar_pantalla(pantalla1_frame)
ventana.mainloop()
