import customtkinter as ctk
from tkinter import filedialog
import os
import sys
import subprocess
from docxtpl import DocxTemplate
from funciones_generales import registrar_solicitud, obtener_solicitudes, resolver_ticket_solicitud, registrar_auditoria, obtener_trabajador_por_cedula, obtener_mis_solicitudes, obtener_trabajadores

class VistaDocumentos(ctk.CTkFrame):
    def __init__(self, master, rol_usuario, cedula_actual):
        super().__init__(master, fg_color="transparent")
        self.cedula_actual = cedula_actual
        self.rol_usuario = rol_usuario.lower()
        
        self.grid_columnconfigure(0, weight=1) 
        self.grid_rowconfigure(0, weight=1)

        if self.rol_usuario in ["administrador", "admin", "rrhh"]:
            self.grid_columnconfigure(1, weight=2) 

        # ================= PANEL DE SOLICITUDES (TRABAJADOR) =================
        self.frame_form = ctk.CTkFrame(self)
        self.frame_form.grid(row=0, column=0, sticky="nsew", padx=(0, 10) if self.rol_usuario in ["administrador", "admin", "rrhh"] else 0)

        ctk.CTkLabel(self.frame_form, text="SOLICITUD DE CONSTANCIAS", font=("Arial", 16, "bold")).pack(pady=20)

        ctk.CTkLabel(self.frame_form, text="Tipo de Documento Requerido:", text_color="gray").pack(anchor="w", padx=20)
        
        # Corrección: Bloqueado a modo lectura estricto mediante state="readonly"
        self.combo_doc = ctk.CTkComboBox(self.frame_form, values=["Constancia de Trabajo", "Antecedentes", "Periodo Vacacional"], state="readonly")
        self.combo_doc.pack(fill="x", padx=20, pady=10)
        self.combo_doc.set("Constancia de Trabajo")

        self.btn_enviar = ctk.CTkButton(self.frame_form, text="Emitir Solicitud", fg_color="#D35400", command=self.ejecutar_solicitud)
        self.btn_enviar.pack(pady=25, padx=20, fill="x")
        
        self.lbl_mensaje = ctk.CTkLabel(self.frame_form, text="")
        self.lbl_mensaje.pack(pady=5)
        
        if self.rol_usuario in ["administrador", "admin", "rrhh"]:
            ctk.CTkFrame(self.frame_form, height=2, fg_color="gray").pack(fill="x", padx=20, pady=15)
            
            ctk.CTkLabel(self.frame_form, text="GENERAR DOCUMENTO", font=("Arial", 14, "bold"), text_color="#F39C12").pack(pady=(5, 15))
            
            ctk.CTkLabel(self.frame_form, text="Seleccione el Trabajador:", text_color="gray").pack(anchor="w", padx=20)
            self.combo_trabajadores_directo = ctk.CTkComboBox(self.frame_form)
            self.combo_trabajadores_directo.pack(fill="x", padx=20, pady=5)
            self.mapa_trabajadores_directo = {}
            self.cargar_combo_trabajadores()
            
            ctk.CTkLabel(self.frame_form, text="Tipo de Documento:", text_color="gray").pack(anchor="w", padx=20)
            self.combo_doc_directo = ctk.CTkComboBox(self.frame_form, values=["Constancia de Trabajo", "Antecedentes", "Periodo Vacacional"], state="readonly")
            self.combo_doc_directo.pack(fill="x", padx=20, pady=5)
            self.combo_doc_directo.set("Constancia de Trabajo")
            
            self.btn_generar_directo = ctk.CTkButton(self.frame_form, text="Generar Documento", fg_color="#1F618D", command=self.ejecutar_generacion_directa)
            self.btn_generar_directo.pack(pady=15, padx=20, fill="x")
            
            self.combo_trabajadores_directo.bind("<Return>", self.ejecutar_generacion_directa)
            self.combo_doc_directo.bind("<Return>", self.ejecutar_generacion_directa)

        # ================= BUZÓN DE NOTIFICACIONES (RRHH) O ESTATUS (TRABAJADOR) =================
        self.frame_notificaciones = ctk.CTkFrame(self)
        self.frame_notificaciones.grid(row=0, column=1, sticky="nsew")

        if self.rol_usuario in ["administrador", "admin", "rrhh"]:
            ctk.CTkLabel(self.frame_notificaciones, text="BUZÓN INTERACTIVO DE SOLICITUDES PENDIENTES", font=("Arial", 14, "bold")).pack(pady=15)
            self.scroll_notificaciones = ctk.CTkScrollableFrame(self.frame_notificaciones, fg_color="transparent")
            self.scroll_notificaciones.pack(fill="both", expand=True, padx=10, pady=10)
            self.actualizar_buzon_notificaciones()
        else:
            self.grid_columnconfigure(1, weight=2)
            ctk.CTkLabel(self.frame_notificaciones, text="ESTATUS DE MIS CONSTANCIAS", font=("Arial", 14, "bold")).pack(pady=15)
            self.scroll_notificaciones = ctk.CTkScrollableFrame(self.frame_notificaciones, fg_color="transparent")
            self.scroll_notificaciones.pack(fill="both", expand=True, padx=10, pady=10)
            self.actualizar_mis_solicitudes()

    def ejecutar_solicitud(self, event=None):
        cedula = self.cedula_actual
        tipo = self.combo_doc.get()
        
        exito, msg = registrar_solicitud(cedula, tipo)
        if exito:
            self.lbl_mensaje.configure(text=msg, text_color="green")
            registrar_auditoria(self.cedula_actual, "Solicitud Emitida", cedula, f"Se solicitó: {tipo}")
            if self.rol_usuario in ["administrador", "admin", "rrhh"]:
                self.actualizar_buzon_notificaciones()
            else:
                self.actualizar_mis_solicitudes()
        else:
            self.lbl_mensaje.configure(text=msg, text_color="red")
            
    def cargar_combo_trabajadores(self):
        datos = obtener_trabajadores(limit=999999, offset=0)
        nombres = []
        for reg in datos:
            ced = reg[0]
            nom = reg[1]
            nombres.append(nom)
            self.mapa_trabajadores_directo[nom] = ced
        
        if nombres:
            self.combo_trabajadores_directo.configure(values=nombres)
            self.combo_trabajadores_directo.set("")
        else:
            self.combo_trabajadores_directo.configure(values=["Sin trabajadores"])
            self.combo_trabajadores_directo.set("")

    def ejecutar_generacion_directa(self, event=None):
        nombre_trabajador = getattr(self, 'combo_trabajadores_directo', None)
        if not nombre_trabajador: return
        nombre = nombre_trabajador.get()
        cedula = getattr(self, 'mapa_trabajadores_directo', {}).get(nombre)
        tipo = self.combo_doc_directo.get()
        if not cedula:
            self.lbl_mensaje.configure(text="Seleccione un trabajador válido.", text_color="red")
            return
            
        trab = obtener_trabajador_por_cedula(cedula)
        if not trab:
            self.lbl_mensaje.configure(text="Trabajador no encontrado en el sistema.", text_color="red")
            return
            
        nombre_completo = f"{trab[1]} {trab[3]}"
        cargo = trab[7]
        
        import datetime
        datos_solicitud = (None, nombre_completo, tipo, "Aprobado", datetime.date.today(), cargo, cedula)
        
        self.lbl_mensaje.configure(text="")
        self.combo_trabajadores_directo.set("")
        self.abrir_ventana_impresion(datos_solicitud)

    def actualizar_buzon_notificaciones(self):
        for widget in self.scroll_notificaciones.winfo_children():
            widget.destroy()

        try:
            solicitudes = obtener_solicitudes()
            
            # Filtrar solo los trámites con estado "Pendiente"
            pendientes = [s for s in solicitudes if s[3] == "Pendiente"]

            if not pendientes:
                ctk.CTkLabel(self.scroll_notificaciones, text="No existen solicitudes pendientes por procesar.", text_color="gray").pack(pady=30)
                return

            for registro in pendientes:
                id_sol, nombre, tipo, estado, fecha, cargo, cedula = registro
                
                # Manejo seguro de la fecha
                fecha_segura = str(fecha)[:10] if fecha else "Fecha no registrada"
                
                # CORRECCIÓN: Se retiró 'pady' del constructor CTkFrame.
                card = ctk.CTkFrame(self.scroll_notificaciones, border_width=1, border_color="#F39C12", fg_color="#212F3D")
                card.pack(fill="x", pady=5, padx=5)

                texto_informativo = f"📅 {fecha_segura} - El empleado {nombre} (C.I: {cedula})\nsolicitó un documento de tipo: '{tipo}'"
                
                # El espaciado vertical (pady) se asigna ahora al posicionar los elementos internos
                lbl_info = ctk.CTkLabel(card, text=texto_informativo, justify="left", font=("Arial", 12, "bold"), text_color="#EAECEE")
                lbl_info.pack(side="top", anchor="w", padx=15, pady=(10, 5)) 

                frame_btns = ctk.CTkFrame(card, fg_color="transparent")
                frame_btns.pack(side="top", anchor="e", padx=15, pady=(0, 10))

                btn_rechazar = ctk.CTkButton(frame_btns, text="❌ Rechazar", width=80, fg_color="#C0392B", hover_color="#922B21", 
                                               command=lambda r=registro: self.abrir_dialogo_rechazo(r))
                btn_rechazar.pack(side="left", padx=(0, 10))

                btn_gestionar = ctk.CTkButton(frame_btns, text="✅ Atender", width=80, fg_color="#27AE60", hover_color="#1E8449",
                                               command=lambda r=registro: self.abrir_ventana_impresion(r))
                btn_gestionar.pack(side="left")
                
        except Exception as e:
            ctk.CTkLabel(self.scroll_notificaciones, text=f"Error interno al cargar datos: {e}", text_color="red").pack(pady=30)
            
    def abrir_dialogo_rechazo(self, registro):
        id_sol, nombre, tipo, estado, fecha, cargo_sol, cedula = registro
        dialog = ctk.CTkInputDialog(text=f"Motivo de rechazo para la solicitud de {tipo} de {nombre} (Opcional):", title="Rechazar Solicitud")
        motivo = dialog.get_input()
        if motivo is not None:
            from funciones_generales import rechazar_solicitud
            exito, msg = rechazar_solicitud(id_sol, motivo)
            if exito:
                self.lbl_mensaje.configure(text=f"Solicitud de {nombre} rechazada.", text_color="green")
                self.actualizar_buzon_notificaciones()
            else:
                self.lbl_mensaje.configure(text=msg, text_color="red")
            
    def actualizar_mis_solicitudes(self):
        for widget in self.scroll_notificaciones.winfo_children():
            widget.destroy()

        try:
            mis_solicitudes = obtener_mis_solicitudes(self.cedula_actual)

            if not mis_solicitudes:
                ctk.CTkLabel(self.scroll_notificaciones, text="No has solicitado ninguna constancia todavía.", text_color="gray").pack(pady=30)
                return

            for registro in mis_solicitudes:
                tipo, estado, fecha, ruta, msj_rechazo = registro
                
                fecha_segura = str(fecha)[:10] if fecha else "Fecha no registrada"
                
                if estado == "Pendiente":
                    b_color = "#F39C12"
                    texto_estado = "⏳ En Proceso"
                elif estado == "Aprobado":
                    b_color = "#27AE60"
                    texto_estado = "✅ Aprobada"
                else:
                    b_color = "#C0392B"
                    texto_estado = "❌ Rechazada"
                
                card = ctk.CTkFrame(self.scroll_notificaciones, border_width=1, border_color=b_color, fg_color="#212F3D")
                card.pack(fill="x", pady=5, padx=5)

                texto_informativo = f"📄 {tipo}\nSolicitado el: {fecha_segura}"
                if estado in ["Rechazado", "Rechazada"] and msj_rechazo:
                    texto_informativo += f"\nMotivo: {msj_rechazo}"
                
                lbl_info = ctk.CTkLabel(card, text=texto_informativo, justify="left", font=("Arial", 12, "bold"), text_color="#EAECEE")
                lbl_info.pack(side="left", padx=15, pady=10)
                
                frame_der = ctk.CTkFrame(card, fg_color="transparent")
                frame_der.pack(side="right", padx=15, pady=10)

                lbl_estado = ctk.CTkLabel(frame_der, text=texto_estado, text_color=b_color, font=("Arial", 12, "bold"))
                lbl_estado.pack(side="top", anchor="e", pady=(0, 5))
                
                if estado == "Aprobado" and ruta:
                    btn_abrir = ctk.CTkButton(frame_der, text="📄 Abrir Documento", width=120, fg_color="#2980B9", hover_color="#1A5276",
                                              command=lambda r=ruta: self.abrir_archivo(r))
                    btn_abrir.pack(side="bottom", anchor="e")
                    
        except Exception as e:
            ctk.CTkLabel(self.scroll_notificaciones, text=f"Error interno al cargar datos: {e}", text_color="red").pack(pady=30)
            
    def abrir_archivo(self, ruta):
        import os, sys, subprocess
        if not os.path.exists(ruta):
            self.lbl_mensaje.configure(text="El archivo ya no existe en el servidor.", text_color="red")
            return
        try:
            if sys.platform == "win32":
                os.startfile(ruta)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", ruta])
            else:
                subprocess.Popen(["xdg-open", ruta])
            self.lbl_mensaje.configure(text="")
        except Exception as e:
            self.lbl_mensaje.configure(text=f"No se pudo abrir el archivo: {e}", text_color="red")
    
    def abrir_ventana_impresion(self, datos_solicitud):
        id_sol, nombre, tipo, estado, fecha, cargo_sol, cedula = datos_solicitud
        
        ventana_imprimir = ctk.CTkToplevel(self)
        ventana_imprimir.title(f"Impresión - {tipo}")
        ventana_imprimir.geometry("450x650")
        ventana_imprimir.after(100, ventana_imprimir.grab_set) 

        ctk.CTkLabel(ventana_imprimir, text="FORMULARIO DE IMPRESIÓN", font=("Arial", 14, "bold")).pack(pady=15)

        # Cargar datos de BD
        trabajador = obtener_trabajador_por_cedula(cedula)
        # trab = (cedula, p_nom, s_nom, p_ape, s_ape, f_nac, f_ingreso, cargo_actual, estado)
        p_nom = trabajador[1] if trabajador else ""
        s_nom = trabajador[2] if trabajador else ""
        p_ape = trabajador[3] if trabajador else ""
        s_ape = trabajador[4] if trabajador else ""
        fecha_ingreso_bd = trabajador[6] if trabajador else ""
        cargo_bd = trabajador[7] if trabajador else cargo_sol

        frame_form = ctk.CTkScrollableFrame(ventana_imprimir, fg_color="transparent")
        frame_form.pack(fill="both", expand=True, padx=20, pady=5)

        def crear_campo(padre, texto, valor_defecto="", es_placeholder=False):
            ctk.CTkLabel(padre, text=texto, text_color="gray").pack(anchor="w", pady=(5,0))
            if es_placeholder:
                entry = ctk.CTkEntry(padre, placeholder_text=str(valor_defecto))
            else:
                entry = ctk.CTkEntry(padre)
                entry.insert(0, str(valor_defecto))
            entry.pack(fill="x", pady=2)
            return entry

        entry_pnom = crear_campo(frame_form, "Primer Nombre:", p_nom)
        entry_snom = crear_campo(frame_form, "Segundo Nombre:", s_nom)
        entry_pape = crear_campo(frame_form, "Primer Apellido:", p_ape)
        entry_sape = crear_campo(frame_form, "Segundo Apellido:", s_ape)
        
        entry_ced = crear_campo(frame_form, "Cédula de Identidad:", cedula)
        entry_car = crear_campo(frame_form, "Cargo Actual:", cargo_bd)
        entry_fecha_ing = crear_campo(frame_form, "Fecha de Ingreso:", fecha_ingreso_bd)
        
        # Separador visual opcional
        ctk.CTkFrame(frame_form, height=2, fg_color="gray").pack(fill="x", pady=(15, 5))
        
        entry_ingreso = crear_campo(frame_form, "Ingreso Mensual (Bs):", "0.00", es_placeholder=True)
        entry_cesta = crear_campo(frame_form, "Cesta Ticket (Bs):", "0.00", es_placeholder=True)
        
        ctk.CTkLabel(frame_form, text="Total Ingresos (Auto-calculado):", text_color="gray").pack(anchor="w", pady=(5,0))
        lbl_total = ctk.CTkLabel(frame_form, text="0.00 Bs", font=("Arial", 12, "bold"))
        lbl_total.pack(anchor="w", pady=2)

        def actualizar_total(*args):
            try:
                ing = float(entry_ingreso.get() or 0)
                ces = float(entry_cesta.get() or 0)
                lbl_total.configure(text=f"{ing + ces:.2f} Bs")
            except:
                lbl_total.configure(text="Error de cálculo")

        entry_ingreso.bind("<KeyRelease>", actualizar_total)
        entry_cesta.bind("<KeyRelease>", actualizar_total)
        actualizar_total()

        # Configuración de ruta
        self.ruta_directorio = os.path.expanduser("~")
        lbl_ruta_actual = ctk.CTkLabel(frame_form, text=f"Destino:\n{self.ruta_directorio}", font=("Arial", 10), text_color="yellow", justify="left")
        lbl_ruta_actual.pack(anchor="w", pady=(15,2))

        def examinar_carpeta():
            seleccion = filedialog.askdirectory()
            if seleccion:
                self.ruta_directorio = seleccion
                lbl_ruta_actual.configure(text=f"Destino:\n{self.ruta_directorio}")

        ctk.CTkButton(frame_form, text="Cambiar carpeta", fg_color="#7F8C8D", command=examinar_carpeta).pack(fill="x", pady=5)

        nombre_archivo_sugerido = f"{tipo} {p_nom} {p_ape}".strip()
        entry_filename = crear_campo(frame_form, "Nombre del archivo (.docx):", nombre_archivo_sugerido)

        def ejecutar_impresion_final(event=None):
            nombre1 = entry_pnom.get()
            nombre2 = entry_snom.get()
            apellido1 = entry_pape.get()
            apellido2 = entry_sape.get()
            
            cargo_final = entry_car.get()
            cedula_final = entry_ced.get()
            fecha_ing_final = entry_fecha_ing.get()
            archivo_final = entry_filename.get()
            
            try:
                ingreso_final = float(entry_ingreso.get() or 0)
                cesta_final = float(entry_cesta.get() or 0)
            except:
                ctk.CTkLabel(frame_form, text="Error: Ingreso o Cesta deben ser numéricos.", text_color="red").pack()
                return

            if not archivo_final: return
            
            try:
                # Seleccionar plantilla base
                if tipo == "Constancia de Trabajo":
                    ruta_plantilla = "templates docs/plantilla_constancia.docx"
                elif tipo == "Periodo Vacacional":
                    ruta_plantilla = "templates docs/planilla_vacaciones.docx"
                else:
                    ruta_plantilla = "templates docs/planilla_antecedentes.docx"

                # Llenado de plantilla usando docxtpl
                doc = DocxTemplate(ruta_plantilla)
                
                contexto = {
                    "NOMBRE1": nombre1,
                    "NOMBRE22": nombre2,
                    "NOMBRE2": nombre2,
                    "APELLIDO1": apellido1,
                    "APELLIDO2": apellido2,
                    "CEDULA": cedula_final,
                    "CARGO": cargo_final,
                    "CARGOINICIAL": cargo_final,
                    "CARGOFINAL": cargo_final,
                    "FECHAINGRESO": str(fecha_ing_final),
                    "FECHA_INGRESO": str(fecha_ing_final),
                    "INGRESOMENSUAL": f"{ingreso_final:,.2f}",
                    "CESTATICKET": f"{cesta_final:,.2f}",
                    "TOTALINGRESO": f"{ingreso_final + cesta_final:,.2f}"
                }
                
                doc.render(contexto)
                ruta_completa = os.path.join(self.ruta_directorio, f"{archivo_final}.docx")
                doc.save(ruta_completa)
                
                sistema_operativo = sys.platform
                if sistema_operativo == "win32":
                    os.startfile(ruta_completa)
                elif sistema_operativo == "darwin":
                    subprocess.Popen(["open", ruta_completa])
                else:
                    subprocess.Popen(["xdg-open", ruta_completa])
                
                if id_sol:
                    resolver_ticket_solicitud(id_sol, "Aprobado", ruta_completa)
                registrar_auditoria(self.cedula_actual, "Emisión de Documento", cedula, f"Se generó documento desde plantilla: {tipo}")
                
                ventana_imprimir.destroy()
                self.actualizar_buzon_notificaciones()
            except Exception as err:
                ctk.CTkLabel(frame_form, text=f"Error: {err}", text_color="red").pack()

        entry_pnom.bind("<Return>", ejecutar_impresion_final)
        entry_snom.bind("<Return>", ejecutar_impresion_final)
        entry_pape.bind("<Return>", ejecutar_impresion_final)
        entry_sape.bind("<Return>", ejecutar_impresion_final)
        entry_ced.bind("<Return>", ejecutar_impresion_final)
        entry_car.bind("<Return>", ejecutar_impresion_final)
        entry_fecha_ing.bind("<Return>", ejecutar_impresion_final)
        entry_ingreso.bind("<Return>", ejecutar_impresion_final)
        entry_cesta.bind("<Return>", ejecutar_impresion_final)
        entry_filename.bind("<Return>", ejecutar_impresion_final)
        
        ctk.CTkButton(ventana_imprimir, text="✅ Imprimir Documento", fg_color="#1E8449", hover_color="#145A32", 
                      command=ejecutar_impresion_final).pack(pady=15, padx=20, fill="x")
                      
        import sys
        if sys.platform == "linux":
            def _bind_mouse_scroll(widget):
                widget.bind("<Button-4>", lambda e: frame_form._parent_canvas.yview_scroll(-1, "units"), add="+")
                widget.bind("<Button-5>", lambda e: frame_form._parent_canvas.yview_scroll(1, "units"), add="+")
                for child in widget.winfo_children():
                    _bind_mouse_scroll(child)
            _bind_mouse_scroll(frame_form)
