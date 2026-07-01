import customtkinter as ctk
from tkinter import ttk
from funciones_generales import obtener_auditorias

class VistaAuditoria(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        frame_tabla = ctk.CTkFrame(self)
        frame_tabla.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(frame_tabla, text="REGISTRO DE AUDITORÍA DEL SISTEMA", font=("Arial", 16, "bold")).pack(pady=15)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2B2B2B", foreground="white", fieldbackground="#2B2B2B", borderwidth=0)
        style.configure("Treeview.Heading", background="#1F1F1F", foreground="white", font=('Arial', 10, 'bold'))

        self.tabla = ttk.Treeview(frame_tabla, columns=("cedula", "accion", "registro_af", "detalles", "fecha_hora"), show="headings")
        self.tabla.heading("cedula", text="Cédula Usuario")
        self.tabla.heading("accion", text="Acción")
        self.tabla.heading("registro_af", text="Afectado")
        self.tabla.heading("detalles", text="Detalles")
        self.tabla.heading("fecha_hora", text="Fecha y Hora")

        self.tabla.column("cedula", width=100, anchor="center")
        self.tabla.column("accion", width=150, anchor="center")
        self.tabla.column("registro_af", width=100, anchor="center")
        self.tabla.column("detalles", width=350, anchor="w")
        self.tabla.column("fecha_hora", width=150, anchor="center")

        self.tabla.pack(fill="both", expand=True, padx=10, pady=10)
        self.actualizar_tabla()

    def actualizar_tabla(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        datos = obtener_auditorias()
        for registro in datos:
            self.tabla.insert("", "end", values=registro)
