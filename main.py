import customtkinter as ctk
from login import PantallaLogin
from dashboard import PantallaDashboard 

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión de Personal")
        
        # Arranca mostrando el login directamente
        self.mostrar_login()

    def mostrar_login(self):
        # Limpiar cualquier vista activa anterior (útil al cerrar sesión)
        for widget in self.winfo_children():
            widget.destroy()
            
        self.geometry("500x600") # Tamaño compacto para Login
        self.vista_actual = PantallaLogin(self, self.abrir_dashboard)
        self.vista_actual.pack(fill="both", expand=True)


    def abrir_dashboard(self, rol_usuario, cedula_usuario):
        self.vista_actual.destroy()
        self.geometry("1280x720") 
        
        # Le inyectamos el rol al Dashboard para que aplique los bloqueos
        self.vista_actual = PantallaDashboard(self, self.mostrar_login, rol_usuario, cedula_usuario)
        self.vista_actual.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()