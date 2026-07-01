import customtkinter as ctk
from vista_trabajadores import VistaTrabajadores 
from vista_usuarios import VistaUsuarios
from vista_documentos import VistaDocumentos
from vista_auditoria import VistaAuditoria

class PantallaDashboard(ctk.CTkFrame):
    def __init__(self, master, comando_salir, rol_usuario, cedula_usuario):
        super().__init__(master)
        self.comando_salir = comando_salir
        self.cedula_actual = cedula_usuario
        # Normalizamos el rol a minúsculas desde el inicio para evitar fallos de sintaxis
        self.rol_actual = rol_usuario.lower() 

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ================= BARRA LATERAL (SIDEBAR) =================
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        self.lbl_empresa = ctk.CTkLabel(self.sidebar, text=f"PANEL:\n{rol_usuario.upper()}", font=("Arial", 16, "bold"))
        self.lbl_empresa.pack(pady=30, padx=10)

        # ================= REGLAS DE ACCESO (ACLs) =================
        
        # 1. Módulo de Usuarios & Auditoría (Nivel 15: Exclusivo Admin)
        if self.rol_actual in ["admin", "administrador"]:
            self.btn_usuarios = ctk.CTkButton(self.sidebar, text="🔐 Usuarios (Admin)", anchor="w", command=self.abrir_modulo_usuarios)
            self.btn_usuarios.pack(pady=10, padx=15, fill="x")
            
            self.btn_auditoria = ctk.CTkButton(self.sidebar, text="📜 Auditoría", anchor="w", command=self.abrir_modulo_auditoria)
            self.btn_auditoria.pack(pady=10, padx=15, fill="x")

        # 2. Módulo de Personal (Niveles 7 y 15: Admin y RRHH)
        if self.rol_actual in ["admin", "administrador", "rrhh", "recursos humanos"]:
            self.btn_trabajadores = ctk.CTkButton(self.sidebar, text="📋 Fichas de Personal", anchor="w", command=self.abrir_modulo_trabajadores)
            self.btn_trabajadores.pack(pady=10, padx=15, fill="x")

        # 3. Módulo de Documentos (Nivel 1+: Todos los rangos)
        self.btn_docs = ctk.CTkButton(self.sidebar, text="📄 Documentos", anchor="w", command=self.abrir_modulo_documentos)
        self.btn_docs.pack(pady=10, padx=15, fill="x")
        
        self.btn_salir = ctk.CTkButton(self.sidebar, text="❌ Cerrar Sesión", fg_color="#C0392B", hover_color="#922B21", command=self.comando_salir)
        self.btn_salir.pack(side="bottom", pady=30, padx=15, fill="x")

        # ================= ÁREA CENTRAL (ZONA DE DESPLIEGUE) =================
        self.area_central = ctk.CTkFrame(self, fg_color="transparent")
        self.area_central.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Enrutamiento de inicio según el rango
        if self.rol_actual == "trabajador":
            self.abrir_modulo_documentos() # Carga directa a su interfaz de tickets
        else:
            self.abrir_modulo_trabajadores() # Carga al radar de personal

    # ================= MÉTODOS DE ENRUTAMIENTO VISUAL =================
    def abrir_modulo_trabajadores(self):
        self.limpiar_area_central()
        vista = VistaTrabajadores(self.area_central, self.cedula_actual)
        vista.pack(fill="both", expand=True)

    def abrir_modulo_usuarios(self):
        self.limpiar_area_central()
        vista = VistaUsuarios(self.area_central, self.cedula_actual)
        vista.pack(fill="both", expand=True)

    def abrir_modulo_auditoria(self):
        self.limpiar_area_central()
        vista = VistaAuditoria(self.area_central)
        vista.pack(fill="both", expand=True)

    def abrir_modulo_documentos(self):
        self.limpiar_area_central()
        vista = VistaDocumentos(self.area_central, self.rol_actual, self.cedula_actual) 
        vista.pack(fill="both", expand=True)
        
    def limpiar_area_central(self):
        # Función auxiliar para vaciar la pantalla antes de dibujar el nuevo módulo
        for widget in self.area_central.winfo_children():
            widget.destroy()