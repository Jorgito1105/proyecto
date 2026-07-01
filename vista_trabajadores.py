import customtkinter as ctk
from tkinter import ttk
from tkcalendar import DateEntry
from funciones_generales import registrar_trabajador_completo, obtener_trabajadores, consultar_linea_tiempo_cargos, promover_o_cambiar_cargo, registrar_auditoria, registrar_usuario

class VistaTrabajadores(ctk.CTkFrame):
    def __init__(self, master, cedula_actual):
        super().__init__(master, fg_color="transparent")
        self.cedula_actual = cedula_actual

        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_registro = self.tabs.add("Gestión de Ingresos")
        self.tab_historial = self.tabs.add("Historial de Cargos")

        self.construir_tab_registro()
        self.construir_tab_historial()

    def construir_tab_registro(self):
        self.tab_registro.grid_columnconfigure(0, weight=1)
        self.tab_registro.grid_columnconfigure(1, weight=2)
        self.tab_registro.grid_rowconfigure(0, weight=1)

        frame_form = ctk.CTkFrame(self.tab_registro)
        frame_form.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(frame_form, text="REGISTRO DE NUEVO PERSONAL", font=("Arial", 16, "bold")).pack(pady=15)

        self.reg_cedula = ctk.CTkEntry(frame_form, placeholder_text="Cédula de Identidad")
        self.reg_cedula.pack(fill="x", padx=20, pady=8)

        self.reg_nombres = ctk.CTkEntry(frame_form, placeholder_text="Apellidos y Nombres")
        self.reg_nombres.pack(fill="x", padx=20, pady=8)

        ctk.CTkLabel(frame_form, text="Fecha de Nacimiento:", text_color="gray").pack(anchor="w", padx=20)
        self.reg_nacimiento = DateEntry(frame_form, date_pattern='yyyy-mm-dd', background='#2B2B2B', foreground='white', headersbackground='#1F1F1F')
        self.reg_nacimiento.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(frame_form, text="Fecha de Ingreso:", text_color="gray").pack(anchor="w", padx=20)
        self.reg_ingreso = DateEntry(frame_form, date_pattern='yyyy-mm-dd', background='#2B2B2B', foreground='white', headersbackground='#1F1F1F')
        self.reg_ingreso.pack(fill="x", padx=20, pady=5)

        self.reg_cargo = ctk.CTkEntry(frame_form, placeholder_text="Cargo Inicial Asignado")
        self.reg_cargo.pack(fill="x", padx=20, pady=8)

        self.check_crear_usuario = ctk.CTkCheckBox(frame_form, text="Generar acceso al sistema (Pass: Cédula)")
        self.check_crear_usuario.pack(anchor="w", padx=20, pady=10)

        ctk.CTkButton(frame_form, text="Registrar Empleado", fg_color="#27AE60", command=self.ejecutar_registro).pack(pady=10, padx=20, fill="x")
        self.lbl_mensaje_reg = ctk.CTkLabel(frame_form, text="")
        self.lbl_mensaje_reg.pack(pady=5)

        # Tabla Principal
        frame_tabla = ctk.CTkFrame(self.tab_registro)
        frame_tabla.grid(row=0, column=1, sticky="nsew")

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2B2B2B", foreground="white", fieldbackground="#2B2B2B", borderwidth=0)
        style.configure("Treeview.Heading", background="#1F1F1F", foreground="white", font=('Arial', 10, 'bold'))

        self.tabla_trabajadores = ttk.Treeview(frame_tabla, columns=("cedula", "nombre", "cargo", "ingreso", "estado"), show="headings")
        self.tabla_trabajadores.heading("cedula", text="Cédula")
        self.tabla_trabajadores.heading("nombre", text="Nombre Completo")
        self.tabla_trabajadores.heading("cargo", text="Cargo Actual")
        self.tabla_trabajadores.heading("ingreso", text="Fecha Ingreso")
        self.tabla_trabajadores.heading("estado", text="Estado Laboral")

        self.tabla_trabajadores.column("cedula", width=80, anchor="center")
        self.tabla_trabajadores.column("nombre", width=150)
        self.tabla_trabajadores.column("cargo", width=120, anchor="center")
        self.tabla_trabajadores.column("ingreso", width=90, anchor="center")
        self.tabla_trabajadores.column("estado", width=80, anchor="center")

        self.tabla_trabajadores.pack(fill="both", expand=True, padx=10, pady=10)
        self.actualizar_tabla_trabajadores()

    def construir_tab_historial(self):
        self.tab_historial.grid_columnconfigure(0, weight=1)
        self.tab_historial.grid_columnconfigure(1, weight=2)
        self.tab_historial.grid_rowconfigure(0, weight=1)

        frame_form = ctk.CTkFrame(self.tab_historial)
        frame_form.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(frame_form, text="SEGUIMIENTO DE CARGOS", font=("Arial", 16, "bold")).pack(pady=15)

        self.busq_cedula = ctk.CTkEntry(frame_form, placeholder_text="Cédula del Trabajador")
        self.busq_cedula.pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(frame_form, text="Consultar Historial", command=self.buscar_historial).pack(pady=5, padx=20, fill="x")

        ctk.CTkLabel(frame_form, text="Registrar Promoción o Cambio:", font=("Arial", 12, "bold"), text_color="gray").pack(anchor="w", padx=20, pady=(25, 5))
        self.nuevo_cargo = ctk.CTkEntry(frame_form, placeholder_text="Nuevo Cargo Destinado")
        self.nuevo_cargo.pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(frame_form, text="Aplicar Cambio", fg_color="#2980B9", command=self.ejecutar_ascenso).pack(pady=10, padx=20, fill="x")
        self.lbl_mensaje_hist = ctk.CTkLabel(frame_form, text="")
        self.lbl_mensaje_hist.pack(pady=5)

        frame_tabla = ctk.CTkFrame(self.tab_historial)
        frame_tabla.grid(row=0, column=1, sticky="nsew")

        self.tabla_historial = ttk.Treeview(frame_tabla, columns=("cargo", "inicio", "fin"), show="headings")
        self.tabla_historial.heading("cargo", text="Cargo Ocupado")
        self.tabla_historial.heading("inicio", text="Fecha de Asignación")
        self.tabla_historial.heading("fin", text="Fecha de Finalización")

        self.tabla_historial.column("cargo", width=200)
        self.tabla_historial.column("inicio", width=120, anchor="center")
        self.tabla_historial.column("fin", width=120, anchor="center")
        
        self.tabla_historial.pack(fill="both", expand=True, padx=10, pady=10)

    def ejecutar_registro(self):
        ced = self.reg_cedula.get()
        nom = self.reg_nombres.get()
        nac = self.reg_nacimiento.get_date().strftime('%Y-%m-%d')
        ing = self.reg_ingreso.get_date().strftime('%Y-%m-%d')
        car = self.reg_cargo.get()

        if not ced or not nom or not car:
            self.lbl_mensaje_reg.configure(text="Existen campos requeridos vacíos.", text_color="red")
            return

        exito, msj = registrar_trabajador_completo(ced, nom, nac, ing, car)
        if exito:
            if self.check_crear_usuario.get() == 1:
                rango = "Trabajador"
                if "admin" in car.lower(): rango = "Administrador"
                elif "recursos" in car.lower() or "rrhh" in car.lower(): rango = "RRHH"
                registrar_usuario(ced, nom, ced, rango, f"{ced}@empresa.com", "Sistema", "N/A")
                msj += " (Cuenta creada)"

            registrar_auditoria(self.cedula_actual, "Registro de Trabajador", ced, f"Se registró al trabajador {nom} con cargo: {car}")
            self.lbl_mensaje_reg.configure(text=msj, text_color="green")
            self.reg_cedula.delete(0, 'end')
            self.reg_nombres.delete(0, 'end')
            self.reg_cargo.delete(0, 'end')
            self.actualizar_tabla_trabajadores()
        else:
            self.lbl_mensaje_reg.configure(text=msj, text_color="red")

    def actualizar_tabla_trabajadores(self):
        for fila in self.tabla_trabajadores.get_children():
            self.tabla_trabajadores.delete(fila)
        datos = obtener_trabajadores()
        for reg in datos:
            self.tabla_trabajadores.insert("", "end", values=reg)

    def buscar_historial(self):
        cedula = self.busq_cedula.get()
        if not cedula: return
        for fila in self.tabla_historial.get_children():
            self.tabla_historial.delete(fila)
        historial = consultar_linea_tiempo_cargos(cedula)
        for reg in historial:
            cargo, inicio, fin = reg
            fin_str = fin if fin else "VIGENTE"
            self.tabla_historial.insert("", "end", values=(cargo, inicio, fin_str))

    def ejecutar_ascenso(self):
        cedula = self.busq_cedula.get()
        cargo = self.nuevo_cargo.get()
        if not cedula or not cargo: return
        exito, msj = promover_o_cambiar_cargo(cedula, cargo)
        if exito:
            registrar_auditoria(self.cedula_actual, "Cambio de Cargo", cedula, f"Se asignó el nuevo cargo: {cargo}")
            self.lbl_mensaje_hist.configure(text=msj, text_color="green")
            self.nuevo_cargo.delete(0, 'end')
            self.buscar_historial()
            self.actualizar_tabla_trabajadores()
        else:
            self.lbl_mensaje_hist.configure(text=msj, text_color="red")