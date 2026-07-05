import customtkinter as ctk
from tkinter import ttk
from funciones_generales import obtener_auditorias, obtener_total_auditorias

class VistaAuditoria(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.pagina_actual = 1
        self.items_por_pagina = 50
        
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
        
        # --- NUEVO CÓDIGO: PAGINACIÓN ---
        frame_controles_tabla = ctk.CTkFrame(frame_tabla, fg_color="transparent")
        frame_controles_tabla.pack(fill="x", padx=10, pady=(0, 10))
        
        self.btn_anterior = ctk.CTkButton(frame_controles_tabla, text="◀ Anterior", width=80, command=self.pagina_anterior)
        self.btn_anterior.pack(side="left", padx=5)
        
        self.lbl_pagina = ctk.CTkLabel(frame_controles_tabla, text="Página 1")
        self.lbl_pagina.pack(side="left", padx=15)
        
        self.btn_siguiente = ctk.CTkButton(frame_controles_tabla, text="Siguiente ▶", width=80, command=self.pagina_siguiente)
        self.btn_siguiente.pack(side="left", padx=5)
        # -----------------------------------------------

        self.actualizar_tabla()

    def actualizar_tabla(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
            
        offset = (self.pagina_actual - 1) * self.items_por_pagina
        datos = obtener_auditorias(limit=self.items_por_pagina, offset=offset)
        
        for registro in datos:
            self.tabla.insert("", "end", values=registro)
            
        self.lbl_pagina.configure(text=f"Página {self.pagina_actual}")
        
        self.btn_anterior.configure(state="normal" if self.pagina_actual > 1 else "disabled")
        total_items = obtener_total_auditorias()
        max_paginas = max(1, (total_items + self.items_por_pagina - 1) // self.items_por_pagina)
        self.btn_siguiente.configure(state="normal" if self.pagina_actual < max_paginas else "disabled")

    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.actualizar_tabla()

    def pagina_siguiente(self):
        total_items = obtener_total_auditorias()
        max_paginas = max(1, (total_items + self.items_por_pagina - 1) // self.items_por_pagina)
        if self.pagina_actual < max_paginas:
            self.pagina_actual += 1
            self.actualizar_tabla()
