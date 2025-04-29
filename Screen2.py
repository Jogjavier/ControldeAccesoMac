import tkinter as tk
from tkinter import Label, Button, Entry
from tkinter import ttk

def on_continue():
    print("Total alumnos:", total_entry.get())
    print("Materia:", materia_combobox.get())
    print("Grupo y Carrera:", grupo_combobox.get())
    print("Tipo de software:", software_combobox.get())

# Crear ventana
root = tk.Tk()
root.title("Laboratorio de MAC")
root.geometry("800x550")
root.configure(bg='#f5e0e0')

# Logo
logo = tk.PhotoImage(file="logo.png")
logo_label = tk.Label(root, image=logo, bg='#f5e0e0')
logo_label.place(x=10, y=10)

# Total alumnos (MÁS ABAJO)
Label(root, text="Total de alumnos que hicieron uso del CC1:", font=("Arial", 12, "bold"), fg="white", bg="#1d127a").place(x=160, y=100)
total_entry = Entry(root, font=("Arial", 12), width=10, justify='center')
total_entry.place(x=520, y=100)
total_entry.insert(0, "18")

# Materia
Button(root, text="Materia", font=("Arial", 12, "bold"), fg="white", bg="#1d127a", width=20).place(x=80, y=180)
materia_combobox = ttk.Combobox(root, font=("Arial", 12), width=22, state="readonly")
materia_combobox['values'] = ["Ingenieria de Software", "Bases de Datos", "Programacion Web", "Inteligencia Artificial", "Ciencia de Datos"]
materia_combobox.place(x=80, y=230)

# Grupo y carrera
Button(root, text="Grupo y Carrera", font=("Arial", 12, "bold"), fg="white", bg="#1d127a", width=20).place(x=310, y=180)
grupo_combobox = ttk.Combobox(root, font=("Arial", 12), width=22, state="readonly")
grupo_combobox['values'] = ["1A-ISC", "1A-INF"]
grupo_combobox.place(x=310, y=230)

# Tipo de uso de software
Button(root, text="Tipo de uso de software", font=("Arial", 12, "bold"), fg="white", bg="#1d127a", width=20).place(x=540, y=180)
software_combobox = ttk.Combobox(root, font=("Arial", 12), width=22, state="readonly")
software_combobox['values'] = ["Plataforma", "Office", "Internet", "AUTOCAD", "Teams"]
software_combobox.place(x=540, y=230)

# Botón continuar
continue_button = Button(root, text="Continuar", font=("Arial", 14, "bold"), fg="white", bg="#1d127a", padx=20, pady=5, command=on_continue)
continue_button.place(x=350, y=450)

# Ejecutar
root.mainloop()
