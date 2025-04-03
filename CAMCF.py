import tkinter as tk
from tkinter import Label, Button, Entry

root = tk.Tk()
root.title("Laboratorio de MAC")
root.geometry("600x400")
root.configure(bg='#f5e0e0')

logo = tk.PhotoImage(file="logo.png")
logo_label = tk.Label(root, image=logo, bg='#f5e0e0')
logo_label.pack(pady=10)

title_label = Label(root, text="Laboratorio de MAC", font=("Arial", 20, "bold"), fg="#1d127a", bg="#f5e0e0")
title_label.pack(pady=50)

root.mainloop()