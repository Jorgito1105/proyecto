import customtkinter as ctk
from tkinter import ttk
from tkcalendar import Calendar
from funciones_generales import registrar_trabajador_completo, obtener_trabajadores, consultar_linea_tiempo_cargos, promover_o_cambiar_cargo, registrar_auditoria, registrar_usuario, obtener_total_trabajadores
from tkinter import filedialog
import csv

class VistaTrabajadores(ctk.CTkFrame):
    def __init__(self, master, cedula_actual):
        super().__init__(master, fg_color="transparent")
        self.cedula_actual = cedula_actual
        self.pagina_actual = 1
        self.items_por_pagina = 50

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
        self.reg_cedula.pack(fill="x", padx=20, pady=4)

        self.reg_pnombre = ctk.CTkEntry(frame_form, placeholder_text="Primer Nombre")
        self.reg_pnombre.pack(fill="x", padx=20, pady=4)
        
        self.reg_snombre = ctk.CTkEntry(frame_form, placeholder_text="Segundo Nombre")
        self.reg_snombre.pack(fill="x", padx=20, pady=4)
        
        self.reg_papellido = ctk.CTkEntry(frame_form, placeholder_text="Primer Apellido")
        self.reg_papellido.pack(fill="x", padx=20, pady=4)
        
        self.reg_sapellido = ctk.CTkEntry(frame_form, placeholder_text="Segundo Apellido")
        self.reg_sapellido.pack(fill="x", padx=20, pady=4)

        def abrir_calendario(entry_widget, titulo):
            import datetime
            top = ctk.CTkToplevel(self)
            top.title(titulo)
            top.geometry("260x180")
            top.grab_set()
            
            ctk.CTkLabel(top, text="Seleccione la Fecha", font=("Arial", 14, "bold")).pack(pady=10)
            
            frame_sel = ctk.CTkFrame(top, fg_color="transparent")
            frame_sel.pack(pady=10)
            
            hoy = datetime.date.today()
            
            dias = [f"{i:02d}" for i in range(1, 32)]
            meses = [f"{i:02d}" for i in range(1, 13)]
            anios = [str(i) for i in range(hoy.year, 1900, -1)]
            
            cb_dia = ctk.CTkComboBox(frame_sel, values=dias, width=60, state="readonly")
            cb_dia.pack(side="left", padx=2)
            cb_dia.set(f"{hoy.day:02d}")
            
            cb_mes = ctk.CTkComboBox(frame_sel, values=meses, width=60, state="readonly")
            cb_mes.pack(side="left", padx=2)
            cb_mes.set(f"{hoy.month:02d}")
            
            cb_anio = ctk.CTkComboBox(frame_sel, values=anios, width=70, state="readonly")
            cb_anio.pack(side="left", padx=2)
            cb_anio.set(str(hoy.year))
            
            def seleccionar():
                fecha_str = f"{cb_anio.get()}-{cb_mes.get()}-{cb_dia.get()}"
                entry_widget.delete(0, 'end')
                entry_widget.insert(0, fecha_str)
                top.destroy()
                
            ctk.CTkButton(top, text="Confirmar Fecha", command=seleccionar).pack(pady=10)

        ctk.CTkLabel(frame_form, text="Fecha de Nacimiento:", text_color="gray").pack(anchor="w", padx=20)
        frame_nac = ctk.CTkFrame(frame_form, fg_color="transparent")
        frame_nac.pack(fill="x", padx=20, pady=5)
        self.reg_nacimiento = ctk.CTkEntry(frame_nac, placeholder_text="YYYY-MM-DD")
        self.reg_nacimiento.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(frame_nac, text="📅", width=30, command=lambda: abrir_calendario(self.reg_nacimiento, "Nacimiento")).pack(side="right")

        ctk.CTkLabel(frame_form, text="Fecha de Ingreso:", text_color="gray").pack(anchor="w", padx=20)
        frame_ing = ctk.CTkFrame(frame_form, fg_color="transparent")
        frame_ing.pack(fill="x", padx=20, pady=5)
        self.reg_ingreso = ctk.CTkEntry(frame_ing, placeholder_text="YYYY-MM-DD")
        self.reg_ingreso.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(frame_ing, text="📅", width=30, command=lambda: abrir_calendario(self.reg_ingreso, "Ingreso")).pack(side="right")

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
        
        # --- NUEVO CÓDIGO: PAGINACIÓN Y EXPORTACIÓN ---
        frame_controles_tabla = ctk.CTkFrame(frame_tabla, fg_color="transparent")
        frame_controles_tabla.pack(fill="x", padx=10, pady=(0, 10))
        
        self.btn_anterior = ctk.CTkButton(frame_controles_tabla, text="◀ Anterior", width=80, command=self.pagina_anterior)
        self.btn_anterior.pack(side="left", padx=5)
        
        self.lbl_pagina = ctk.CTkLabel(frame_controles_tabla, text="Página 1")
        self.lbl_pagina.pack(side="left", padx=15)
        
        self.btn_siguiente = ctk.CTkButton(frame_controles_tabla, text="Siguiente ▶", width=80, command=self.pagina_siguiente)
        self.btn_siguiente.pack(side="left", padx=5)
        
        self.btn_exportar = ctk.CTkButton(frame_controles_tabla, text="📥 Exportar a CSV", width=120, fg_color="#1E8449", hover_color="#145A32", command=self.exportar_csv)
        self.btn_exportar.pack(side="right", padx=5)
        # -----------------------------------------------

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
        pn = self.reg_pnombre.get()
        sn = self.reg_snombre.get()
        pa = self.reg_papellido.get()
        sa = self.reg_sapellido.get()
        nac = self.reg_nacimiento.get()
        ing = self.reg_ingreso.get()
        car = self.reg_cargo.get()

        if not (ced and pn and pa and nac and ing and car):
            self.lbl_mensaje_reg.configure(text="Complete campos requeridos.", text_color="red")
            return

        exito, msg = registrar_trabajador_completo(ced, pn, sn, pa, sa, nac, ing, car)
        if exito:
            if self.check_crear_usuario.get():
                registrar_usuario(ced, f"{pn} {pa}", ced, "Trabajador", "", "", "")
            
            self.lbl_mensaje_reg.configure(text="¡Registrado exitosamente!", text_color="green")
            registrar_auditoria(self.cedula_actual, "Ingreso de Personal", ced, f"Asignado al cargo: {car}")
            
            self.reg_cedula.delete(0, 'end')
            self.reg_pnombre.delete(0, 'end')
            self.reg_snombre.delete(0, 'end')
            self.reg_papellido.delete(0, 'end')
            self.reg_sapellido.delete(0, 'end')
            self.reg_cargo.delete(0, 'end')
            self.actualizar_tabla_trabajadores()
        else:
            self.lbl_mensaje_reg.configure(text=msg, text_color="red")

    def actualizar_tabla_trabajadores(self):
        for fila in self.tabla_trabajadores.get_children():
            self.tabla_trabajadores.delete(fila)
            
        offset = (self.pagina_actual - 1) * self.items_por_pagina
        datos = obtener_trabajadores(limit=self.items_por_pagina, offset=offset)
        
        for reg in datos:
            self.tabla_trabajadores.insert("", "end", values=reg)
            
        self.lbl_pagina.configure(text=f"Página {self.pagina_actual}")
        
        self.btn_anterior.configure(state="normal" if self.pagina_actual > 1 else "disabled")
        total_items = obtener_total_trabajadores()
        max_paginas = max(1, (total_items + self.items_por_pagina - 1) // self.items_por_pagina)
        self.btn_siguiente.configure(state="normal" if self.pagina_actual < max_paginas else "disabled")

    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.actualizar_tabla_trabajadores()

    def pagina_siguiente(self):
        total_items = obtener_total_trabajadores()
        max_paginas = max(1, (total_items + self.items_por_pagina - 1) // self.items_por_pagina)
        if self.pagina_actual < max_paginas:
            self.pagina_actual += 1
            self.actualizar_tabla_trabajadores()

    def exportar_csv(self):
        datos = obtener_trabajadores(limit=999999, offset=0) 
        archivo = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Archivos CSV", "*.csv")], initialfile="Lista_Trabajadores.csv")
        if archivo:
            try:
                with open(archivo, mode='w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Cédula", "Nombre Completo", "Cargo", "Fecha Ingreso", "Estado"])
                    writer.writerows(datos)
                import tkinter.messagebox as messagebox
                messagebox.showinfo("Éxito", "Los datos fueron exportados a CSV correctamente.\nPuede abrir el archivo con Excel.")
            except Exception as e:
                import tkinter.messagebox as messagebox
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

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