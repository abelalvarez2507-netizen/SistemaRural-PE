import tkinter as tk
from tkinter import messagebox


def abrir_sistema():
    messagebox.showinfo('Sistema Rural-PE', 'Sistema iniciado correctamente.')


def salir():
    root.destroy()


root = tk.Tk()
root.title('Sistema Rural-PE')
root.geometry('260x180')
root.resizable(False, False)

frame = tk.Frame(root)
frame.pack(expand=True)

tk.Button(frame, text='Iniciar sistema', width=18, command=abrir_sistema).pack(pady=5)
tk.Button(frame, text='Información', width=18,
          command=lambda: messagebox.showinfo('Información', 'Interfaz')).pack(pady=5)
tk.Button(frame, text='Salir', width=18, command=salir).pack(pady=5)

root.mainloop()
