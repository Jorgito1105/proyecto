import customtkinter as ctk
import bcrypt
import random
from conexion_BD import conectar_bd
from funciones_generales import registrar_usuario, verificar_trabajador_registrado, registrar_auditoria, verificar_correo_usuario, enviar_codigo_correo, restablecer_password, buscar_usuario_por_cedula

class PantallaLogin(ctk.CTkFrame):
    def __init__(self, master, comando_acceso):
        super().__init__(master)
        self.comando_acceso = comando_acceso
        self.mostrar_login()

    # ================= 1. INTERFAZ DE LOGIN =================
    def mostrar_login(self):
        self.limpiar_pantalla()
        
        ctk.CTkLabel(self, text="Sistema de RRHH", font=("Arial", 22, "bold")).pack(pady=(60, 30))

        self.entry_cedula = ctk.CTkEntry(self, placeholder_text="Número de Cédula", width=250)
        self.entry_cedula.pack(pady=10)

        self.entry_password = ctk.CTkEntry(self, placeholder_text="Contraseña", width=250, show="*") 
        self.entry_password.pack(pady=10)
        
        self.entry_cedula.bind("<Return>", self.verificar_credenciales)
        self.entry_password.bind("<Return>", self.verificar_credenciales)

        self.btn_ingresar = ctk.CTkButton(self, text="Iniciar Sesión", command=self.verificar_credenciales)
        self.btn_ingresar.pack(pady=20)

        self.lbl_mensaje = ctk.CTkLabel(self, text="", font=("Arial", 12))
        self.lbl_mensaje.pack(pady=5)
        
        ctk.CTkButton(self, text="¿Eres parte del personal? ¡Regístrate aquí!", fg_color="transparent", 
                      hover_color="#2B2B2B", text_color="gray", command=self.mostrar_registro).pack(pady=(20, 0))

        ctk.CTkButton(self, text="¿Olvidaste tu contraseña? Recuperar aquí", fg_color="transparent", 
                      hover_color="#2B2B2B", text_color="#3498DB", command=self.mostrar_recuperacion_fase1).pack(pady=(5, 0))

    # ================= 2. VERIFICACIÓN Y REGISTRO =================
    def mostrar_registro(self):
        self.limpiar_pantalla()
        
        ctk.CTkLabel(self, text="REGISTRO DE PERSONAL", font=("Arial", 22, "bold")).pack(pady=(30, 10))
        
        # Primer paso: Solo pedir la cédula para cruzar con RRHH
        self.reg_cedula = ctk.CTkEntry(self, placeholder_text="Ingrese su Cédula", width=250)
        self.reg_cedula.pack(pady=10)
        self.reg_cedula.bind("<Return>", self.desplegar_formulario)
        
        self.btn_verificar = ctk.CTkButton(self, text="Verificar Identidad", command=self.desplegar_formulario)
        self.btn_verificar.pack(pady=10)
        
        # Contenedor dinámico donde aparecerá el resto del formulario
        self.frame_dinamico = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_dinamico.pack(fill="both", expand=True)

        self.lbl_mensaje = ctk.CTkLabel(self, text="", font=("Arial", 12))
        self.lbl_mensaje.pack(pady=5)
        
        ctk.CTkButton(self, text="Volver al inicio", fg_color="transparent", 
                      hover_color="#2B2B2B", text_color="gray", command=self.mostrar_login).pack(pady=(10, 0))

    def desplegar_formulario(self, event=None):
        cedula = self.reg_cedula.get()
        if not cedula:
            self.lbl_mensaje.configure(text="Ingrese un número de cédula.", text_color="red")
            return
            
        es_trabajador, nombre = verificar_trabajador_registrado(cedula)
        
        for widget in self.frame_dinamico.winfo_children():
            widget.destroy()
            
        def crear_campo(padre, texto, is_pass=False, mandatory=True):
            frame = ctk.CTkFrame(padre, fg_color="transparent")
            frame.pack(pady=5)
            entry = ctk.CTkEntry(frame, placeholder_text=texto, width=230, show="*" if is_pass else "")
            entry.pack(side="left")
            if mandatory:
                ctk.CTkLabel(frame, text=" *", text_color="red", font=("Arial", 16, "bold")).pack(side="left", padx=(5,0))
            else:
                ctk.CTkLabel(frame, text="  ", font=("Arial", 16)).pack(side="left", padx=(5,0))
                
            entry.bind("<Return>", self.ejecutar_registro)
            return entry

        self.reg_nombre = crear_campo(self.frame_dinamico, "Nombre Completo", mandatory=True)
        
        if es_trabajador:
            self.lbl_mensaje.configure(text="Personal verificado. Complete sus datos.", text_color="green")
            self.reg_nombre.insert(0, nombre)
            self.reg_nombre.configure(state="disabled") 
        else:
            self.lbl_mensaje.configure(text="Cédula no encontrada en RRHH. Ingrese datos manuales.", text_color="orange")

        self.reg_pass = crear_campo(self.frame_dinamico, "Crear Contraseña", is_pass=True, mandatory=True)
        self.reg_correo = crear_campo(self.frame_dinamico, "Correo Corporativo o Personal", mandatory=True)
        self.reg_pregunta = crear_campo(self.frame_dinamico, "Pregunta de Seguridad", mandatory=True)
        self.reg_respuesta = crear_campo(self.frame_dinamico, "Respuesta", mandatory=True)

        ctk.CTkButton(self.frame_dinamico, text="Finalizar Registro", fg_color="green", command=self.ejecutar_registro).pack(pady=15)

    # ================= 3. LÓGICA DE OPERACIONES =================
    def limpiar_pantalla(self):
        for widget in self.winfo_children():
            widget.destroy()

    def verificar_credenciales(self, event=None):
        cedula_txt = self.entry_cedula.get()
        password_txt = self.entry_password.get()

        if not cedula_txt or not password_txt:
            self.lbl_mensaje.configure(text="Campos requeridos vacíos", text_color="red")
            return

        db = conectar_bd()
        if db:
            cursor = db.cursor()
            sql = "SELECT rol, password_hash FROM usuarios WHERE cedula = %s"
            cursor.execute(sql, (cedula_txt,))
            resultado = cursor.fetchone()
            
            if resultado:
                nivel_acceso = resultado[0]
                stored_hash = resultado[1]
                
                es_valido = False
                try:
                    if bcrypt.checkpw(password_txt.encode('utf-8'), stored_hash.encode('utf-8')):
                        es_valido = True
                except ValueError:
                    if password_txt == stored_hash:
                        es_valido = True
                        
                if es_valido:
                    if nivel_acceso.lower() in ["pendiente", "externo"]:
                        self.lbl_mensaje.configure(text="Cuenta en espera de autorización administrativa.", text_color="orange")
                    else:
                        self.lbl_mensaje.configure(text=f"Acceso Autorizado. Rol: {nivel_acceso}", text_color="green")
                        registrar_auditoria(cedula_txt, "Inicio de Sesión", cedula_txt, f"El usuario inició sesión en el sistema con rol {nivel_acceso}.")
                        self.comando_acceso(nivel_acceso, cedula_txt) 
                else:
                    self.lbl_mensaje.configure(text="Credenciales incorrectas", text_color="red")
            else:
                self.lbl_mensaje.configure(text="Credenciales incorrectas", text_color="red")
            
            cursor.close()
            db.close()
        else:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Error de Conexión", "No se pudo conectar a la base de datos.\nVerifique que el servidor MySQL esté activo.")
            self.lbl_mensaje.configure(text="Error de conexión al servidor", text_color="red")

    def ejecutar_registro(self, event=None):
        cedula = self.reg_cedula.get()
        nombre = self.reg_nombre.get()
        password = self.reg_pass.get()
        correo = self.reg_correo.get()
        pregunta = self.reg_pregunta.get()
        respuesta = self.reg_respuesta.get()
        
        if not password or not correo or not nombre or not pregunta or not respuesta:
            self.lbl_mensaje.configure(text="Por favor, complete todos los campos obligatorios (*).", text_color="red")
            return
            
        es_trabajador, _ = verificar_trabajador_registrado(cedula)
        rango_asignado = "Trabajador" if es_trabajador else "Externo"
            
        exito, mensaje = registrar_usuario(cedula, nombre, password, rango_asignado, correo, pregunta, respuesta)
        
        if exito:
            registrar_auditoria(cedula, "Registro de Usuario", cedula, f"Usuario registrado exitosamente con rol {rango_asignado}.")
            self.lbl_mensaje.configure(text="Registro exitoso. Proceda a iniciar sesión.", text_color="green")
            self.mostrar_login() 
        else:
            self.lbl_mensaje.configure(text=mensaje, text_color="red")

    # ================= 4. RECUPERACIÓN DE CONTRASEÑA =================
    def mostrar_recuperacion_fase1(self):
        self.limpiar_pantalla()
        
        ctk.CTkLabel(self, text="RECUPERAR CONTRASEÑA", font=("Arial", 22, "bold")).pack(pady=(60, 30))
        
        self.rec_cedula = ctk.CTkEntry(self, placeholder_text="Número de Cédula", width=250)
        self.rec_cedula.pack(pady=10)
        
        self.rec_correo = ctk.CTkEntry(self, placeholder_text="Correo Electrónico Registrado", width=250)
        self.rec_correo.pack(pady=10)
        
        self.rec_cedula.bind("<Return>", self.procesar_fase1)
        self.rec_correo.bind("<Return>", self.procesar_fase1)
        
        ctk.CTkButton(self, text="Enviar Código", command=self.procesar_fase1).pack(pady=20)
        
        self.lbl_mensaje = ctk.CTkLabel(self, text="", font=("Arial", 12))
        self.lbl_mensaje.pack(pady=5)
        
        ctk.CTkButton(self, text="¿Recuperar por Pregunta de Seguridad?", fg_color="transparent", 
                      hover_color="#2B2B2B", text_color="#F39C12", command=self.mostrar_recuperacion_pregunta).pack(pady=(10, 0))
        
        ctk.CTkButton(self, text="Volver al inicio", fg_color="transparent", 
                      hover_color="#2B2B2B", text_color="gray", command=self.mostrar_login).pack(pady=(15, 0))

    def mostrar_recuperacion_pregunta(self):
        self.limpiar_pantalla()
        
        ctk.CTkLabel(self, text="PREGUNTA DE SEGURIDAD", font=("Arial", 22, "bold")).pack(pady=(60, 30))
        
        self.rec_cedula = ctk.CTkEntry(self, placeholder_text="Número de Cédula", width=250)
        self.rec_cedula.pack(pady=10)
        self.rec_cedula.bind("<Return>", self.procesar_pregunta)
        
        ctk.CTkButton(self, text="Buscar Usuario", command=self.procesar_pregunta).pack(pady=20)
        
        self.lbl_mensaje = ctk.CTkLabel(self, text="", font=("Arial", 12))
        self.lbl_mensaje.pack(pady=5)
        
        ctk.CTkButton(self, text="Volver", fg_color="transparent", 
                      hover_color="#2B2B2B", text_color="gray", command=self.mostrar_recuperacion_fase1).pack(pady=(30, 0))

    def procesar_pregunta(self, event=None):
        self.cedula_rec = self.rec_cedula.get()
        if not self.cedula_rec:
            self.lbl_mensaje.configure(text="Ingrese su cédula.", text_color="red")
            return
            
        usuario = buscar_usuario_por_cedula(self.cedula_rec)
        if usuario:
            self.cedula_recuperacion = self.cedula_rec
            self.pregunta_seguridad_bd = usuario[4]
            self.respuesta_seguridad_bd = usuario[5]
            
            if not self.pregunta_seguridad_bd or self.pregunta_seguridad_bd == "N/A":
                self.lbl_mensaje.configure(text="Este usuario no configuró pregunta de seguridad.", text_color="red")
                return
                
            self.limpiar_pantalla()
            ctk.CTkLabel(self, text="PREGUNTA DE SEGURIDAD", font=("Arial", 22, "bold")).pack(pady=(60, 15))
            ctk.CTkLabel(self, text=f"Pregunta: {self.pregunta_seguridad_bd}", text_color="white", font=("Arial", 14)).pack(pady=(0, 20))
            
            self.rec_respuesta = ctk.CTkEntry(self, placeholder_text="Su Respuesta", width=250)
            self.rec_respuesta.pack(pady=10)
            self.rec_respuesta.bind("<Return>", self.procesar_validar_respuesta)
            
            ctk.CTkButton(self, text="Validar", command=self.procesar_validar_respuesta).pack(pady=20)
            
            self.lbl_mensaje = ctk.CTkLabel(self, text="", font=("Arial", 12))
            self.lbl_mensaje.pack(pady=5)
            
            ctk.CTkButton(self, text="Cancelar", fg_color="transparent", 
                          hover_color="#2B2B2B", text_color="gray", command=self.mostrar_login).pack(pady=(30, 0))
        else:
            self.lbl_mensaje.configure(text="Cédula no encontrada.", text_color="red")

    def procesar_validar_respuesta(self, event=None):
        respuesta = self.rec_respuesta.get()
        if respuesta.strip().lower() == self.respuesta_seguridad_bd.strip().lower():
            self.mostrar_recuperacion_fase3()
        else:
            self.lbl_mensaje.configure(text="Respuesta incorrecta.", text_color="red")

    def procesar_fase1(self, event=None):
        self.cedula_rec = self.rec_cedula.get()
        correo = self.rec_correo.get()
        
        if not self.cedula_rec or not correo:
            self.lbl_mensaje.configure(text="Por favor, complete ambos campos.", text_color="red")
            return
            
        if verificar_correo_usuario(self.cedula_rec, correo):
            self.lbl_mensaje.configure(text="Enviando código... Por favor espere.", text_color="orange")
            self.update() 
            
            self.codigo_generado = str(random.randint(100000, 999999))
            exito, msj = enviar_codigo_correo(correo, self.codigo_generado)
            
            if exito:
                self.cedula_recuperacion = self.cedula_rec
                self.mostrar_recuperacion_fase2()
            else:
                self.lbl_mensaje.configure(text=msj, text_color="red")
        else:
            self.lbl_mensaje.configure(text="La cédula y el correo no coinciden o no existen.", text_color="red")

    def mostrar_recuperacion_fase2(self):
        self.limpiar_pantalla()
        
        ctk.CTkLabel(self, text="CÓDIGO DE VERIFICACIÓN", font=("Arial", 22, "bold")).pack(pady=(60, 15))
        ctk.CTkLabel(self, text="Se ha enviado un código de 6 dígitos a su correo.", text_color="gray").pack(pady=(0, 20))
        
        self.rec_codigo = ctk.CTkEntry(self, placeholder_text="Código de Verificación", width=250)
        self.rec_codigo.pack(pady=10)
        self.rec_codigo.bind("<Return>", self.procesar_fase2)
        
        ctk.CTkButton(self, text="Verificar Código", command=self.procesar_fase2).pack(pady=20)
        
        self.lbl_mensaje = ctk.CTkLabel(self, text="", font=("Arial", 12))
        self.lbl_mensaje.pack(pady=5)
        
        ctk.CTkButton(self, text="Cancelar", fg_color="transparent", 
                      hover_color="#2B2B2B", text_color="gray", command=self.mostrar_login).pack(pady=(30, 0))

    def procesar_fase2(self, event=None):
        codigo = self.rec_codigo.get()
        if codigo == self.codigo_generado:
            self.mostrar_recuperacion_fase3()
        else:
            self.lbl_mensaje.configure(text="Código incorrecto.", text_color="red")

    def mostrar_recuperacion_fase3(self):
        self.limpiar_pantalla()
        
        ctk.CTkLabel(self, text="NUEVA CONTRASEÑA", font=("Arial", 22, "bold")).pack(pady=(60, 30))
        
        self.rec_pass1 = ctk.CTkEntry(self, placeholder_text="Nueva Contraseña", width=250, show="*")
        self.rec_pass1.pack(pady=10)
        
        self.rec_pass2 = ctk.CTkEntry(self, placeholder_text="Repetir Contraseña", width=250, show="*")
        self.rec_pass2.pack(pady=10)
        
        self.rec_pass1.bind("<Return>", self.procesar_nueva_pass)
        self.rec_pass2.bind("<Return>", self.procesar_nueva_pass)
        
        ctk.CTkButton(self, text="Guardar Nueva Contraseña", fg_color="green", command=self.procesar_nueva_pass).pack(pady=20)
        
        self.lbl_mensaje = ctk.CTkLabel(self, text="", font=("Arial", 12))
        self.lbl_mensaje.pack(pady=5)

    def procesar_nueva_pass(self, event=None):
        p1 = self.rec_pass1.get()
        p2 = self.rec_pass2.get()
        
        if not p1 or not p2:
            self.lbl_mensaje.configure(text="Complete ambos campos.", text_color="red")
            return
            
        if p1 != p2:
            self.lbl_mensaje.configure(text="Las contraseñas no coinciden.", text_color="red")
            return
            
        exito, msj = restablecer_password(self.cedula_recuperacion, p1)
        if exito:
            registrar_auditoria(self.cedula_recuperacion, "Recuperación de Contraseña", self.cedula_recuperacion, "El usuario restableció su contraseña mediante código de correo electrónico.")
            self.mostrar_login()
            self.lbl_mensaje.configure(text="Contraseña restablecida con éxito.", text_color="green")
        else:
            self.lbl_mensaje.configure(text=msj, text_color="red")