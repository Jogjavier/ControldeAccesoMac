from tkinter import *
from tkinter import ttk
from datetime import datetime
from tkinter import messagebox

def mostrar_pantalla_2():
    pantalla1_frame.pack_forget()
    pantalla2_frame.pack(fill='both', expand=True)

def mostrar_pantalla_3():
    if not total_entry.get().isdigit():
        messagebox.showwarning("Dato faltante", "Por favor, ingresa el total de alumnos (solo números).")
        return
    if not materia_combobox.get():
        messagebox.showwarning("Dato faltante", "Por favor, selecciona una materia.")
        return
    if not grupo_combobox.get():
        messagebox.showwarning("Dato faltante", "Por favor, selecciona un grupo y carrera.")
        return
    if not software_combobox.get():
        messagebox.showwarning("Dato faltante", "Por favor, selecciona el tipo de uso de software.")
        return

    entrada_label.config(text=f"Entrada: {datetime.now().strftime('%H:%M')}")
    fecha_label.config(text=datetime.now().strftime('%d/%m/%Y'))
    grupo_label.config(text=grupo_combobox.get())
    nombre_label.config(text="Eduardo Orozco Ortega")
    materia_label.config(text=materia_combobox.get())
    total_label.config(text=f"Total de Alumnos: {total_entry.get()}")
    software_label.config(text=f"Software: {software_combobox.get()}")

    pantalla2_frame.pack_forget()
    pantalla3_frame.pack(fill='both', expand=True)

def mostrar_pantalla_4():
    pantalla3_frame.pack_forget()
    pantalla4_frame.pack(fill='both', expand=True)

def mostrar_pantalla_5():  # Nueva pantalla de salida
    pantalla4_frame.pack_forget()
    pantalla5_frame.pack(fill='both', expand=True)

def volver_a_inicio():
    pantalla5_frame.pack_forget()
    pantalla1_frame.pack(fill='both', expand=True)

# Configuración de la ventana principal
root = Tk()
root.title("Laboratorio de MAC")
# Ajustamos el tamaño para Raspberry Pi
root.geometry("800x480")  # Resolución común en Raspberry Pi
root.configure(bg='#f5e0e0')

# Intentar cargar la imagen, con manejo de errores
try:
    logo = PhotoImage(file="logo.png")
    logo_widget = Label(root, image=logo, bg="#f5e0e0")
    has_logo = True
except:
    print("No se pudo cargar el logo. Usando texto en su lugar.")
    logo_widget = Label(root, text="LAB MAC", font=("Arial", 14, "bold"), bg="#f5e0e0", fg="#1d127a")
    has_logo = False

# ------------------- Pantalla 1 -------------------
pantalla1_frame = Frame(root, bg="#f5e0e0")
pantalla1_frame.pack(fill='both', expand=True)

# Grid para mejor organización
pantalla1_frame.grid_columnconfigure(0, weight=1)
for i in range(6):
    pantalla1_frame.grid_rowconfigure(i, weight=1)

if has_logo:
    logo_widget.place(x=10, y=10)
else:
    logo_widget.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

Label(pantalla1_frame, text="Laboratorio de MAC", font=("Arial", 20, "bold"), fg="#1d127a", bg="#f5e0e0").grid(row=1, column=0, pady=10)
Label(pantalla1_frame, text="Aproximar Tarjeta", font=("Arial", 14), fg="#1d127a", bg="#f5e0e0").grid(row=2, column=0, pady=5)
Entry(pantalla1_frame, font=("Arial", 14), justify='center', width=15).grid(row=3, column=0, pady=5)

# Contenedor para el botón para asegurar que sea visible
button_frame1 = Frame(pantalla1_frame, bg="#f5e0e0")
button_frame1.grid(row=4, column=0, pady=20)
Button(button_frame1, text="Continuar", font=("Arial", 14, "bold"), fg="white", bg="#1d127a", 
       command=mostrar_pantalla_2, width=12, height=1).pack()

# ------------------- Pantalla 2 -------------------
pantalla2_frame = Frame(root, bg="#f5e0e0")

# Logo en la parte superior
if has_logo:
    Label(pantalla2_frame, image=logo, bg="#f5e0e0").place(x=10, y=10)
else:
    Label(pantalla2_frame, text="LAB MAC", font=("Arial", 14, "bold"), bg="#f5e0e0", fg="#1d127a").place(x=10, y=10)

# Utilizamos grid para esta pantalla también
pantalla2_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)  # Añadimos una columna más
for i in range(7):
    pantalla2_frame.grid_rowconfigure(i, weight=1)

# Movemos el "Total de alumnos" más a la derecha para no tapar el logo
Label(pantalla2_frame, text="Total de alumnos:", font=("Arial", 12, "bold"), fg="black", bg="#f5e0e0").grid(row=0, column=1, pady=10, padx=5, sticky="e")
total_entry = Entry(pantalla2_frame, font=("Arial", 12), width=8, justify='center')
total_entry.grid(row=0, column=2, sticky="w", pady=10)

# Sección de materias
Label(pantalla2_frame, text="Materia:", font=("Arial", 12, "bold"), fg="black", bg="#f5e0e0").grid(row=1, column=0, pady=5, sticky="w", padx=20)
materia_combobox = ttk.Combobox(pantalla2_frame, font=("Arial", 11), width=20, state="readonly")
materia_combobox['values'] = ["Ingenieria de Software", "Bases de Datos", "Programacion Web", "Inteligencia Artificial", "Ciencia de Datos"]
materia_combobox.grid(row=2, column=0, padx=20, pady=5, sticky="w")

# Sección de grupo
Label(pantalla2_frame, text="Grupo y Carrera:", font=("Arial", 12, "bold"), fg="black", bg="#f5e0e0").grid(row=1, column=1, pady=5, sticky="w", padx=10)
grupo_combobox = ttk.Combobox(pantalla2_frame, font=("Arial", 11), width=15, state="readonly")
grupo_combobox['values'] = ["1A-ISC", "1A-INF"]
grupo_combobox.grid(row=2, column=1, padx=10, pady=5, sticky="w")

# Sección de software
Label(pantalla2_frame, text="Software:", font=("Arial", 12, "bold"), fg="black", bg="#f5e0e0").grid(row=1, column=2, pady=5, sticky="w", padx=10)
software_combobox = ttk.Combobox(pantalla2_frame, font=("Arial", 11), width=15, state="readonly")
software_combobox['values'] = ["Plataforma", "Office", "Internet", "AUTOCAD", "Teams"]
software_combobox.grid(row=2, column=2, padx=10, pady=5, sticky="w")

# Contenedor para el botón para asegurar que sea visible
button_frame2 = Frame(pantalla2_frame, bg="#f5e0e0")
button_frame2.grid(row=6, column=0, columnspan=3, pady=20)
Button(button_frame2, text="Continuar", font=("Arial", 14, "bold"), fg="white", bg="#1d127a", 
       command=mostrar_pantalla_3, width=12).pack()

# ------------------- Pantalla 3 -------------------
pantalla3_frame = Frame(root, bg="#f5e0e0")

# Logo en la parte superior
if has_logo:
    Label(pantalla3_frame, image=logo, bg="#f5e0e0").place(x=10, y=10)
else:
    Label(pantalla3_frame, text="LAB MAC", font=("Arial", 14, "bold"), bg="#f5e0e0", fg="#1d127a").place(x=10, y=10)

# Grid para mejor organización
pantalla3_frame.grid_columnconfigure((0, 1), weight=1)
for i in range(8):
    pantalla3_frame.grid_rowconfigure(i, weight=1)

Label(pantalla3_frame, text="Laboratorio de MAC", font=("Arial", 18, "bold"), fg="#1d127a", bg="#f5e0e0").grid(row=0, column=0, columnspan=2, pady=10)

# Primera columna de etiquetas
Label(pantalla3_frame, text="Entrada:", font=("Arial", 12, "bold"), fg="black", bg="#f5e0e0").grid(row=1, column=0, sticky="e", pady=5)
Label(pantalla3_frame, text="Fecha:", font=("Arial", 12, "bold"), fg="black", bg="#f5e0e0").grid(row=2, column=0, sticky="e", pady=5)
Label(pantalla3_frame, text="Grupo:", font=("Arial", 12, "bold"), fg="black", bg="#f5e0e0").grid(row=3, column=0, sticky="e", pady=5)

# Segunda columna de etiquetas
Label(pantalla3_frame, text="Nombre:", font=("Arial", 12, "bold"), fg="black", bg="#f5e0e0").grid(row=1, column=1, sticky="w", padx=10, pady=5)
Label(pantalla3_frame, text="Materia:", font=("Arial", 12, "bold"), fg="black", bg="#f5e0e0").grid(row=2, column=1, sticky="w", padx=10, pady=5)
Label(pantalla3_frame, text="Total:", font=("Arial", 12, "bold"), fg="black", bg="#f5e0e0").grid(row=3, column=1, sticky="w", padx=10, pady=5)
Label(pantalla3_frame, text="Software:", font=("Arial", 12, "bold"), fg="black", bg="#f5e0e0").grid(row=4, column=1, sticky="w", padx=10, pady=5)

# Valores que se actualizan
entrada_label = Label(pantalla3_frame, text="", font=("Arial", 12), bg="white", width=20)
entrada_label.grid(row=1, column=0, sticky="w", padx=(200, 10), pady=5)

fecha_label = Label(pantalla3_frame, text="", font=("Arial", 12), bg="white", width=20)
fecha_label.grid(row=2, column=0, sticky="w", padx=(200, 10), pady=5)

grupo_label = Label(pantalla3_frame, text="", font=("Arial", 12), bg="white", width=20)
grupo_label.grid(row=3, column=0, sticky="w", padx=(200, 10), pady=5)

nombre_label = Label(pantalla3_frame, text="", font=("Arial", 12), bg="white", width=20)
nombre_label.grid(row=1, column=1, sticky="w", padx=(100, 10), pady=5)

materia_label = Label(pantalla3_frame, text="", font=("Arial", 12), bg="white", width=20)
materia_label.grid(row=2, column=1, sticky="w", padx=(100, 10), pady=5)

total_label = Label(pantalla3_frame, text="", font=("Arial", 12), bg="white", width=20)
total_label.grid(row=3, column=1, sticky="w", padx=(100, 10), pady=5)

software_label = Label(pantalla3_frame, text="", font=("Arial", 12), bg="white", width=20)
software_label.grid(row=4, column=1, sticky="w", padx=(100, 10), pady=5)

# Contenedor para los botones
button_frame3 = Frame(pantalla3_frame, bg="#f5e0e0")
button_frame3.grid(row=7, column=0, columnspan=2, pady=10)
Button(button_frame3, text="Atrás", font=("Arial", 12), fg="white", bg="#1d127a", width=10, 
       command=lambda: [pantalla3_frame.pack_forget(), pantalla2_frame.pack(fill='both', expand=True)]).pack(side=LEFT, padx=10)
Button(button_frame3, text="Confirmar", font=("Arial", 12), fg="white", bg="#1d127a", width=10, 
       command=mostrar_pantalla_4).pack(side=LEFT, padx=10)

# ------------------- Pantalla 4 -------------------
pantalla4_frame = Frame(root, bg="#f5e0e0")

# Logo en la parte superior
if has_logo:
    Label(pantalla4_frame, image=logo, bg="#f5e0e0").place(x=10, y=10)
else:
    Label(pantalla4_frame, text="LAB MAC", font=("Arial", 14, "bold"), bg="#f5e0e0", fg="#1d127a").place(x=10, y=10)

# Grid para mejor organización
pantalla4_frame.grid_columnconfigure(0, weight=1)
for i in range(5):
    pantalla4_frame.grid_rowconfigure(i, weight=1)

Label(pantalla4_frame, text="Laboratorio de MAC", font=("Arial", 18, "bold"), fg="#1d127a", bg="#f5e0e0").grid(row=0, column=0, pady=10)
Label(pantalla4_frame, text="Registro Exitoso", font=("Arial", 22, "bold"), fg="black", bg="lime").grid(row=1, column=0, pady=20)

# Contenedor para el botón
button_frame4 = Frame(pantalla4_frame, bg="#f5e0e0")
button_frame4.grid(row=3, column=0, pady=20)
Button(button_frame4, text="Registrar Salida", font=("Arial", 14, "bold"), fg="white", bg="#1d127a", 
       command=mostrar_pantalla_5, width=15).pack()

# ------------------- Pantalla 5 (Registro de Salida) -------------------
pantalla5_frame = Frame(root, bg="#f5e0e0")

# Logo en la parte superior
if has_logo:
    Label(pantalla5_frame, image=logo, bg="#f5e0e0").place(x=10, y=10)
else:
    Label(pantalla5_frame, text="LAB MAC", font=("Arial", 14, "bold"), bg="#f5e0e0", fg="#1d127a").place(x=10, y=10)

# Grid para mejor organización
pantalla5_frame.grid_columnconfigure(0, weight=1)
for i in range(6):
    pantalla5_frame.grid_rowconfigure(i, weight=1)

Label(pantalla5_frame, text="Registrar Salida", font=("Arial", 18, "bold"), fg="#1d127a", bg="#f5e0e0").grid(row=1, column=0, pady=10)
Label(pantalla5_frame, text="Aproximar Tarjeta para Salida", font=("Arial", 14), fg="#1d127a", bg="#f5e0e0").grid(row=2, column=0, pady=5)
Entry(pantalla5_frame, font=("Arial", 14), justify='center', width=15).grid(row=3, column=0, pady=5)

# Contenedor para el botón
button_frame5 = Frame(pantalla5_frame, bg="#f5e0e0")
button_frame5.grid(row=4, column=0, pady=20)
Button(button_frame5, text="Confirmar", font=("Arial", 14, "bold"), fg="white", bg="#1d127a", 
       command=volver_a_inicio, width=12).pack()

root.mainloop()