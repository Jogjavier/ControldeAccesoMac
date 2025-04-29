import tkinter as tk
from tkinter import Label, Button, Entry

def on_continue():
    print("Botón Continuar presionado")

# Crear ventana
root = tk.Tk()
root.title("Laboratorio de MAC")
root.geometry("600x400")
root.configure(bg='#f5e0e0')

# Logo 
logo = tk.PhotoImage(file="logo.png")
logo_label = tk.Label(root, image=logo, bg='#f5e0e0')
logo_label.place(x=10, y=10)

# Título
title_label = Label(root, text="Laboratorio de MAC", font=("Arial", 20, "bold"), fg="#1d127a", bg="#f5e0e0")
title_label.pack(pady=50)

# Instrucción
instruction_label = Label(root, text="Aproximar Tarjeta", font=("Arial", 14), fg="#1d127a", bg="#f5e0e0")
instruction_label.pack()

# Campo de texto
entry = Entry(root, font=("Arial", 16), justify='center')
entry.pack(pady=10)
entry.insert(0, "")

# Botón
continue_button = Button(root, text="Continuar", font=("Arial", 16, "bold"), fg="white", bg="#1d127a", padx=20, pady=5, command=on_continue)
continue_button.pack(pady=20)

# Ejecutar ventana
root.mainloop()
