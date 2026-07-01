import customtkinter as ctk
from tkinter import filedialog
import os
from docx import Document
from funciones_generales import registrar_solicitud, obtener_solicitudes, resolver_ticket_solicitud, registrar_auditoria

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

        ctk.CTkLabel(self.frame_form, text="Cédula de Identidad:", text_color="gray").pack(anchor="w", padx=20)
        self.entry_cedula = ctk.CTkEntry(self.frame_form, placeholder_text="Ingrese su identificación")
        self.entry_cedula.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(self.frame_form, text="Tipo de Documento Requerido:", text_color="gray").pack(anchor="w", padx=20)
        
        # Corrección: Bloqueado a modo lectura estricto mediante state="readonly"
        self.combo_doc = ctk.CTkComboBox(self.frame_form, values=["Constancia de Trabajo", "Permiso Sabático", "Periodo Vacacional"], state="readonly")
        self.combo_doc.pack(fill="x", padx=20, pady=10)

        self.btn_enviar = ctk.CTkButton(self.frame_form, text="Emitir Solicitud", fg_color="#D35400", command=self.ejecutar_solicitud)
        self.btn_enviar.pack(pady=25, padx=20, fill="x")
        
        self.lbl_mensaje = ctk.CTkLabel(self.frame_form, text="")
        self.lbl_mensaje.pack(pady=5)

        # ================= BUZÓN DE NOTIFICACIONES DINÁMICAS (ADMIN / RRHH) =================
        if self.rol_usuario in ["administrador", "admin", "rrhh"]:
            self.frame_notificaciones = ctk.CTkFrame(self)
            self.frame_notificaciones.grid(row=0, column=1, sticky="nsew")

            ctk.CTkLabel(self.frame_notificaciones, text="BUZÓN INTERACTIVO DE SOLICITUDES PENDIENTES", font=("Arial", 14, "bold")).pack(pady=15)
            
            # Contenedor con barra de desplazamiento para los mensajes informativos
            self.scroll_notificaciones = ctk.CTkScrollableFrame(self.frame_notificaciones, fg_color="transparent")
            self.scroll_notificaciones.pack(fill="both", expand=True, padx=10, pady=10)
            
            self.actualizar_buzon_notificaciones()

    def ejecutar_solicitud(self):
        cedula = self.entry_cedula.get()
        tipo = self.combo_doc.get()
        if not cedula: return
            
        exito, mensaje = registrar_solicitud(cedula, tipo)
        if exito:
            registrar_auditoria(self.cedula_actual, "Solicitud de Documento", cedula, f"Se solicitó el documento: {tipo}")
            self.lbl_mensaje.configure(text=mensaje, text_color="green")
            self.entry_cedula.delete(0, 'end')
            if self.rol_usuario in ["administrador", "admin", "rrhh"]:
                self.actualizar_buzon_notificaciones()
        else:
            self.lbl_mensaje.configure(text=mensaje, text_color="red")

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
                card = ctk.CTkFrame(self.scroll_notificaciones, border_width=1, border_color="#5D6D7E")
                card.pack(fill="x", pady=5, padx=5)

                texto_informativo = f"📅 {fecha_segura} - El empleado {nombre} (C.I: {cedula})\nsolicitó un documento de tipo: '{tipo}'"
                
                # El espaciado vertical (pady) se asigna ahora al posicionar los elementos internos
                lbl_info = ctk.CTkLabel(card, text=texto_informativo, justify="left", font=("Arial", 11))
                lbl_info.pack(side="left", padx=15, pady=10) 

                btn_gestionar = ctk.CTkButton(card, text="Atender", width=80, fg_color="#2E4053", 
                                               command=lambda r=registro: self.abrir_ventana_impresion(r))
                btn_gestionar.pack(side="right", padx=15, pady=10)
                
        except Exception as e:
            ctk.CTkLabel(self.scroll_notificaciones, text=f"Error interno al cargar datos: {e}", text_color="red").pack(pady=30)
    
    def abrir_ventana_impresion(self, datos_solicitud):
        """Abre una nueva ventana modal dentro del sistema para procesar y descargar el archivo."""
        id_sol, nombre, tipo, estado, fecha, cargo, cedula = datos_solicitud
        
        ventana_imprimir = ctk.CTkToplevel(self)
        ventana_imprimir.title("Procesamiento e Impresión de Documento")
        ventana_imprimir.geometry("450x500")
        ventana_imprimir.grab_set() # Bloquea la ventana de fondo para enfoque prioritario

        ctk.CTkLabel(ventana_imprimir, text="PROCESADOR DE FORMATO CORPORATIVO", font=("Arial", 14, "bold")).pack(pady=15)

        # Campos editables requeridos para la personalización final previa impresión
        frame_edicion = ctk.CTkFrame(ventana_imprimir, fg_color="transparent")
        frame_edicion.pack(fill="x", padx=30, pady=5)

        ctk.CTkLabel(frame_edicion, text="Nombre completo del destinatario:", text_color="gray").pack(anchor="w")
        entry_nom = ctk.CTkEntry(frame_edicion)
        entry_nom.pack(fill="x", pady=2)
        entry_nom.insert(0, nombre)

        ctk.CTkLabel(frame_edicion, text="Cargo a certificar:", text_color="gray").pack(anchor="w", pady=(10,0))
        entry_car = ctk.CTkEntry(frame_edicion)
        entry_car.pack(fill="x", pady=2)
        entry_car.insert(0, cargo if cargo else "Empleado General")

        # Configuración de ruta local de almacenamiento
        frame_ruta = ctk.CTkFrame(ventana_imprimir, fg_color="transparent")
        frame_ruta.pack(fill="x", padx=30, pady=10)
        
        self.ruta_directorio = os.path.expanduser("~") # Ruta inicial por defecto del sistema operativo
        
        lbl_ruta_actual = ctk.CTkLabel(frame_ruta, text=f"Carpeta de destino:\n{self.ruta_directorio}", font=("Arial", 10), text_color="yellow", justify="left")
        lbl_ruta_actual.pack(anchor="w", pady=2)

        def examinar_carpeta():
            seleccion = filedialog.askdirectory()
            if seleccion:
                self.ruta_directorio = seleccion
                lbl_ruta_actual.configure(text=f"Carpeta de destino:\n{self.ruta_directorio}")

        ctk.CTkButton(frame_ruta, text="Cambiar carpeta de guardado", fg_color="#7F8C8D", command=examinar_carpeta).pack(fill="x", pady=5)

        ctk.CTkLabel(ventana_imprimir, text="Nombre asignado al archivo (.docx):", text_color="gray").pack(anchor="w", padx=30)
        entry_filename = ctk.CTkEntry(ventana_imprimir)
        entry_filename.pack(fill="x", padx=30, pady=2)
        entry_filename.insert(0, f"Constancia_{cedula}")

        # Acción de impresión y generación del archivo de Word final mediante python-docx
        def ejecutar_impresion_final():
            nombre_final = entry_nom.get()
            cargo_final = entry_car.get()
            archivo_final = entry_filename.get()
            
            if not archivo_final: return
            
            try:
                # Inicialización del formateador Word corporativo
                doc = Document()
                doc.add_heading('CERTIFICACIÓN LABORAL CORPORATIVA', 0)
                
                p = doc.add_paragraph('Por medio del presente documento oficial del Departamento de Recursos Humanos, se certifica que el ciudadano ')
                p.add_run(f'{nombre_final}').bold = True
                p.add_run(', titular de la Cédula de Identidad ')
                p.add_run(f'{cedula}').bold = True
                p.add_run(f', desempeña actualmente funciones bajo el cargo formal de ')
                p.add_run(f'{cargo_final}').bold = True
                p.add_run(' en los registros internos de la empresa.')
                
                doc.add_paragraph('\nConstancia legítima expedida para los fines pertinentes de la parte interesada.')
                
                ruta_completa = os.path.join(self.ruta_directorio, f"{archivo_final}.docx")
                doc.save(ruta_completa)
                
                # Actualizar estatus y guardar trazabilidad de la ubicación física en la BD
                resolver_ticket_solicitud(id_sol, "Aprobado", ruta_completa)
                registrar_auditoria(self.cedula_actual, "Emisión de Documento", cedula, f"Se generó e imprimió el documento tipo: {tipo}")
                
                ventana_imprimir.destroy()
                self.actualizar_buzon_notificaciones()
            except Exception as err:
                ctk.CTkLabel(ventana_imprimir, text=f"Error de exportación: {err}", text_color="red").pack()

        ctk.CTkButton(ventana_imprimir, text="Generar e Imprimir Documento", fg_color="#27AE60", command=ejecutar_impresion_final).pack(pady=20, padx=30, fill="x")
