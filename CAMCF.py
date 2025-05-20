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

root = Tk()
root.title("Laboratorio de MAC")
root.geometry("900x600")
root.configure(bg='#f5e0e0')

logo = PhotoImage(file="logo.png")

# ------------------- Pantalla 1 -------------------
pantalla1_frame = Frame(root, bg="#f5e0e0")
pantalla1_frame.pack(fill='both', expand=True)

Label(pantalla1_frame, image=logo, bg="#f5e0e0").place(x=10, y=10)
Label(pantalla1_frame, text="Laboratorio de MAC", font=("Arial", 24, "bold"), fg="#1d127a", bg="#f5e0e0").pack(pady=100)
Label(pantalla1_frame, text="Aproximar Tarjeta", font=("Arial", 16), fg="#1d127a", bg="#f5e0e0").pack()
Entry(pantalla1_frame, font=("Arial", 16), justify='center').pack(pady=10)
Button(pantalla1_frame, text="Continuar", font=("Arial", 16, "bold"), fg="white", bg="#1d127a", command=mostrar_pantalla_2).pack(pady=30)

# ------------------- Pantalla 2 -------------------
pantalla2_frame = Frame(root, bg="#f5e0e0")
Label(pantalla2_frame, image=logo, bg="#f5e0e0").place(x=10, y=10)
Label(pantalla2_frame, text="Total de alumnos que hicieron uso del CC1:", font=("Arial", 12, "bold"), fg="white", bg="#1d127a").place(x=160, y=100)
total_entry = Entry(pantalla2_frame, font=("Arial", 12), width=10, justify='center')
total_entry.place(x=520, y=100)

Button(pantalla2_frame, text="Materia", font=("Arial", 12, "bold"), fg="white", bg="#1d127a", width=20).place(x=80, y=180)
materia_combobox = ttk.Combobox(pantalla2_frame, font=("Arial", 12), width=22, state="readonly")
materia_combobox['values'] = ["Ingenieria de Software", "Bases de Datos", "Programacion Web", "Inteligencia Artificial", "Ciencia de Datos"]
materia_combobox.place(x=80, y=230)

Button(pantalla2_frame, text="Grupo y Carrera", font=("Arial", 12, "bold"), fg="white", bg="#1d127a", width=20).place(x=310, y=180)
grupo_combobox = ttk.Combobox(pantalla2_frame, font=("Arial", 12), width=22, state="readonly")
grupo_combobox['values'] = ["1A-ISC", "1A-INF"]
grupo_combobox.place(x=310, y=230)

Button(pantalla2_frame, text="Tipo de uso de software", font=("Arial", 12, "bold"), fg="white", bg="#1d127a", width=20).place(x=540, y=180)
software_combobox = ttk.Combobox(pantalla2_frame, font=("Arial", 12), width=22, state="readonly")
software_combobox['values'] = ["Plataforma", "Office", "Internet", "AUTOCAD", "Teams"]
software_combobox.place(x=540, y=230)

Button(pantalla2_frame, text="Continuar", font=("Arial", 14, "bold"), fg="white", bg="#1d127a", command=mostrar_pantalla_3).place(x=380, y=450)

# ------------------- Pantalla 3 -------------------
pantalla3_frame = Frame(root, bg="#f5e0e0")
Label(pantalla3_frame, image=logo, bg="#f5e0e0").place(x=10, y=10)
Label(pantalla3_frame, text="Laboratorio de MAC", font=("Arial", 24, "bold"), fg="#1d127a", bg="#f5e0e0").pack(pady=50)

entrada_label = Label(pantalla3_frame, font=("Arial", 16), bg="white", width=25)
entrada_label.place(x=150, y=160)

fecha_label = Label(pantalla3_frame, font=("Arial", 16), bg="white", width=25)
fecha_label.place(x=150, y=210)

grupo_label = Label(pantalla3_frame, font=("Arial", 16), bg="white", width=25)
grupo_label.place(x=150, y=260)

nombre_label = Label(pantalla3_frame, text="", font=("Arial", 16), bg="white", width=25)
nombre_label.place(x=500, y=160)

materia_label = Label(pantalla3_frame, font=("Arial", 16), bg="white", width=25)
materia_label.place(x=500, y=210)

total_label = Label(pantalla3_frame, font=("Arial", 16), bg="white", width=25)
total_label.place(x=500, y=260)

software_label = Label(pantalla3_frame, font=("Arial", 16), bg="white", width=25)
software_label.place(x=500, y=310)

Button(pantalla3_frame, text="Atras", font=("Arial", 14), fg="white", bg="#1d127a", width=12, command=lambda: [pantalla3_frame.pack_forget(), pantalla2_frame.pack(fill='both', expand=True)]).place(x=250, y=450)
Button(pantalla3_frame, text="Confirmar", font=("Arial", 14), fg="white", bg="#1d127a", width=12, command=mostrar_pantalla_4).place(x=450, y=450)

# ------------------- Pantalla 4 -------------------
pantalla4_frame = Frame(root, bg="#f5e0e0")
Label(pantalla4_frame, image=logo, bg="#f5e0e0").place(x=10, y=10)
Label(pantalla4_frame, text="Laboratorio de MAC", font=("Arial", 24, "bold"), fg="#1d127a", bg="#f5e0e0").pack(pady=60)
Label(pantalla4_frame, text="Registro Exitoso", font=("Arial", 28, "bold"), fg="black", bg="lime", width=30, height=2).pack(pady=30)
Button(pantalla4_frame, text="Registrar Salida", font=("Arial", 16, "bold"), fg="white", bg="#1d127a", padx=20, pady=5, command=mostrar_pantalla_5).pack(pady=30)

# ------------------- Pantalla 5 (Registro de Salida) -------------------
pantalla5_frame = Frame(root, bg="#f5e0e0")
Label(pantalla5_frame, image=logo, bg="#f5e0e0").place(x=10, y=10)
Label(pantalla5_frame, text="Registrar Salida", font=("Arial", 24, "bold"), fg="#1d127a", bg="#f5e0e0").pack(pady=100)
Label(pantalla5_frame, text="Aproximar Tarjeta para Salida", font=("Arial", 16), fg="#1d127a", bg="#f5e0e0").pack()
Entry(pantalla5_frame, font=("Arial", 16), justify='center').pack(pady=10)
Button(pantalla5_frame, text="Confirmar", font=("Arial", 16, "bold"), fg="white", bg="#1d127a", command=volver_a_inicio).pack(pady=30)

root.mainloop()
