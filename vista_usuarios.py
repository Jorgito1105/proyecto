import customtkinter as ctk
from tkinter import ttk
from funciones_generales import obtener_usuarios_priorizados, buscar_usuario_por_cedula, actualizar_usuario_completo_admin, registrar_auditoria

class VistaUsuarios(ctk.CTkFrame):
    def __init__(self, master, cedula_actual):
        super().__init__(master, fg_color="transparent")
        self.cedula_actual = cedula_actual
        
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=2) 
        self.grid_rowconfigure(0, weight=1)

        # ================= ZONA IZQUIERDA: BÚSQUEDA Y EDICIÓN =================
        self.frame_form = ctk.CTkFrame(self)
        self.frame_form.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(self.frame_form, text="MÓDULO DE CREDENCIALES", font=("Arial", 16, "bold")).pack(pady=15)

        # Panel de Búsqueda Inicial
        self.frame_busqueda = ctk.CTkFrame(self.frame_form, fg_color="transparent")
        self.frame_busqueda.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(self.frame_busqueda, text="Cédula del Usuario:", text_color="gray").pack(anchor="w")
        self.entry_buscar_cedula = ctk.CTkEntry(self.frame_busqueda, placeholder_text="Ej: 12345678")
        self.entry_buscar_cedula.pack(fill="x", pady=5)
        
        self.btn_buscar = ctk.CTkButton(self.frame_busqueda, text="Buscar Usuario", command=self.ejecutar_busqueda)
        self.btn_buscar.pack(fill="x", pady=5)

        # Contenedor para el formulario dinámico (Inicia vacío)
        self.frame_campos_edicion = ctk.CTkScrollableFrame(self.frame_form, fg_color="transparent")
        self.frame_campos_edicion.pack(fill="both", expand=True, padx=15, pady=10)

        self.lbl_mensaje = ctk.CTkLabel(self.frame_form, text="")
        self.lbl_mensaje.pack(pady=5)

        # ================= ZONA DERECHA: REGISTROS JERÁRQUICOS =================
        self.frame_tabla = ctk.CTkFrame(self)
        self.frame_tabla.grid(row=0, column=1, sticky="nsew")

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2B2B2B", foreground="white", fieldbackground="#2B2B2B", borderwidth=0)
        style.configure("Treeview.Heading", background="#1F1F1F", foreground="white", font=('Arial', 10, 'bold'))
        
        self.tabla = ttk.Treeview(self.frame_tabla, columns=("cedula", "nombre", "rol", "correo"), show="headings")
        self.tabla.heading("cedula", text="Cédula")
        self.tabla.heading("nombre", text="Nombre Completo")
        self.tabla.heading("rol", text="Rango del Sistema")
        self.tabla.heading("correo", text="Correo Electrónico")

        self.tabla.column("cedula", width=100, anchor="center")
        self.tabla.column("nombre", width=180)
        self.tabla.column("rol", width=120, anchor="center")
        self.tabla.column("correo", width=150)

        self.tabla.pack(fill="both", expand=True, padx=10, pady=10)
        self.actualizar_tabla()

    def ejecutar_busqueda(self):
        cedula = self.entry_buscar_cedula.get()
        if not cedula:
            self.lbl_mensaje.configure(text="Ingrese una cédula válida.", text_color="red")
            return
            
        datos = buscar_usuario_por_cedula(cedula)
        
        # Limpiar formulario dinámico previo
        for widget in self.frame_campos_edicion.winfo_children():
            widget.destroy()
            
        if datos:
            self.lbl_mensaje.configure(text="Usuario localizado.", text_color="green")
            self.desplegar_formulario_modificacion(datos)
        else:
            self.lbl_mensaje.configure(text="El usuario no existe en el sistema.", text_color="red")

    def desplegar_formulario_modificacion(self, datos):
        self.datos_usuario_actual = datos
        cedula, nombre, rol, correo, pregunta, respuesta = datos
        
        lbl_frame_nom = ctk.CTkFrame(self.frame_campos_edicion, fg_color="transparent")
        lbl_frame_nom.pack(anchor="w", pady=(5,0))
        ctk.CTkLabel(lbl_frame_nom, text="Nombre Completo:", text_color="gray").pack(side="left")
        ctk.CTkLabel(lbl_frame_nom, text=" *", text_color="red").pack(side="left")
        
        self.entry_nombre = ctk.CTkEntry(self.frame_campos_edicion)
        self.entry_nombre.pack(fill="x", pady=2)
        self.entry_nombre.insert(0, nombre)

        lbl_frame_rol = ctk.CTkFrame(self.frame_campos_edicion, fg_color="transparent")
        lbl_frame_rol.pack(anchor="w", pady=(5,0))
        ctk.CTkLabel(lbl_frame_rol, text="Rango asignado:", text_color="gray").pack(side="left")
        ctk.CTkLabel(lbl_frame_rol, text=" *", text_color="red").pack(side="left")
        
        self.combo_rol = ctk.CTkComboBox(self.frame_campos_edicion, values=["Trabajador", "RRHH", "Administrador"], state="readonly")
        self.combo_rol.pack(fill="x", pady=2)
        self.combo_rol.set(rol)

        ctk.CTkLabel(self.frame_campos_edicion, text="Correo Electrónico:", text_color="gray").pack(anchor="w", pady=(5,0))
        self.entry_correo = ctk.CTkEntry(self.frame_campos_edicion)
        self.entry_correo.pack(fill="x", pady=2)
        self.entry_correo.insert(0, correo)

        ctk.CTkLabel(self.frame_campos_edicion, text="Pregunta de Seguridad:", text_color="gray").pack(anchor="w", pady=(5,0))
        self.entry_pregunta = ctk.CTkEntry(self.frame_campos_edicion)
        self.entry_pregunta.pack(fill="x", pady=2)
        self.entry_pregunta.insert(0, pregunta if pregunta else "")

        ctk.CTkLabel(self.frame_campos_edicion, text="Respuesta de Seguridad:", text_color="gray").pack(anchor="w", pady=(5,0))
        self.entry_respuesta = ctk.CTkEntry(self.frame_campos_edicion)
        self.entry_respuesta.pack(fill="x", pady=2)
        self.entry_respuesta.insert(0, respuesta if respuesta else "")

        ctk.CTkLabel(self.frame_campos_edicion, text="Nueva Contraseña (Opcional):", text_color="gray").pack(anchor="w", pady=(5,0))
        self.entry_pass = ctk.CTkEntry(self.frame_campos_edicion, show="*")
        self.entry_pass.pack(fill="x", pady=2)

        self.btn_guardar = ctk.CTkButton(self.frame_campos_edicion, text="Guardar Cambios", fg_color="#1F618D", command=lambda: self.guardar_cambios(cedula))
        self.btn_guardar.pack(fill="x", pady=15)

    def guardar_cambios(self, cedula):
        nombre = self.entry_nombre.get()
        rol = self.combo_rol.get()
        correo = self.entry_correo.get()
        pregunta = self.entry_pregunta.get()
        respuesta = self.entry_respuesta.get()
        nueva_pass = self.entry_pass.get()

        if not all([nombre, rol]):
            self.lbl_mensaje.configure(text="Complete los campos obligatorios (*).", text_color="red")
            return

        pass_final = nueva_pass if nueva_pass else None
        exito, msg = actualizar_usuario_completo_admin(cedula, nombre, rol, correo, pregunta, respuesta, pass_final)
        
        if exito:
            _, old_nombre, old_rol, old_correo, _, _ = self.datos_usuario_actual
            cambios = []
            if nombre != old_nombre: cambios.append(f"Nombre: '{old_nombre}'->'{nombre}'")
            if rol != old_rol: cambios.append(f"Rol: '{old_rol}'->'{rol}'")
            if correo != old_correo: cambios.append(f"Correo: '{old_correo}'->'{correo}'")
            if nueva_pass: cambios.append("Contraseña actualizada")
            detalle = "Se modificó: " + ", ".join(cambios) if cambios else "Se guardó sin cambios"

            registrar_auditoria(self.cedula_actual, "Modificación de Usuario", cedula, detalle)
            self.lbl_mensaje.configure(text=msg, text_color="green")
            for widget in self.frame_campos_edicion.winfo_children():
                widget.destroy()
            self.actualizar_tabla()
        else:
            self.lbl_mensaje.configure(text=msg, text_color="red")

    def actualizar_tabla(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        datos = obtener_usuarios_priorizados()
        for registro in datos:
            self.tabla.insert("", "end", values=registro)