import customtkinter as ctk
from PIL import Image
import root2, root3
import supervision_client as cli, auth as ath
import threading
import time


# Configuración de apariencia
ctk.set_appearance_mode("light") 

URL_SERVER = "http://localhost:8080"

class AppLogin(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Contractify - Login")
        self.geometry("950x570")
        self.resizable(False, False)
        self.configure(fg_color="#F5F6FA")

        # Grid principal 1x2
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- PANEL IZQUIERDO (Azul) ---
        self.left_frame = ctk.CTkFrame(self, fg_color="#3b37d7", corner_radius=25)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)

        # Logo
        self.logo_label = ctk.CTkLabel(self.left_frame, text="🛡️ Contractify", 
                                       font=("Arial Bold", 24), text_color="white")
        self.logo_label.pack(anchor="nw", padx=50, pady=(50, 0))

        # Título principal
           # Contenedor de texto con el resaltado de color
        text_container = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        text_container.pack(anchor="w", padx=40, pady=(100, 10))

        # Texto Blanco
        part1 = ctk.CTkLabel(text_container, 
                             text="Gestiona tus contratos con", 
                             font=("Arial Bold", 32), 
                             text_color="white", 
                             justify="left")
        part1.pack(anchor="w")

        # Texto Resaltado (#867EBD)
        part2 = ctk.CTkLabel(text_container, 
                             text="precisión quirúrgica.", 
                             font=("Arial Bold", 32), 
                             text_color="#B8A4FF", 
                             justify="left")
        part2.pack(anchor="w")

        # Descripción
        self.desc_label = ctk.CTkLabel(self.left_frame, 
                                       text="Accede a la plataforma de supervisión más avanzada\npara el control de contratos y proyectos.",
                                       font=("Arial", 15), text_color="#D1D1FB", justify="left")
        self.desc_label.pack(anchor="w", padx=50, pady=30)

        # Footer Supervisores (CORREGIDO: Color sólido para evitar error RGBA)
        self.super_frame = ctk.CTkFrame(self.left_frame, fg_color="#4d49e1", corner_radius=15)
        self.super_frame.pack(side="bottom", anchor="w", padx=50, pady=50, ipadx=10, ipady=5)

        for color, name in [("#5dade2","JD"), ("#48c9b0","AM"), ("#f4d03f","NA")]:
            ctk.CTkLabel(self.super_frame, text=name, width=32, height=32, corner_radius=16, 
                         fg_color=color, text_color="white", font=("Arial Bold", 11)).pack(side="left", padx=2)
        
        ctk.CTkLabel(self.super_frame, text="  +15 supervisores activos hoy.", 
                     font=("Arial", 13), text_color="white").pack(side="left")

        # --- PANEL DERECHO (Formulario) ---
        self.right_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        # Bienvenida
        ctk.CTkLabel(self.right_frame, text="Bienvenido de nuevo", 
                     font=("Arial Bold", 30), text_color="#1F1F1F").pack(pady=(80, 5))
        self.lc= ctk.CTkLabel(self.right_frame, text="Ingresa tus credenciales para continuar", 
                     font=("Arial", 15), text_color="gray")
        self.lc.pack(pady=(0,40))

        # Ancho estándar para inputs
        form_width = 340

        # Usuario
        ctk.CTkLabel(self.right_frame, text="Usuario", font=("Arial Bold", 13)).pack(anchor="w", padx=50)
        self.user_entry = ctk.CTkEntry(self.right_frame, placeholder_text="👤   nombre.apellido", 
                                       width=form_width, height=45, fg_color="#F2F2F2", border_width=0)
        self.user_entry.pack(pady=(5, 20))

        # Contraseña con cabecera alineada
        pass_header = ctk.CTkFrame(self.right_frame, fg_color="transparent", width=form_width)
        pass_header.pack(pady=(0, 5))
        ctk.CTkLabel(pass_header, text="Contraseña", font=("Arial Bold", 13)).pack(side="left", padx=40)
        ctk.CTkLabel(pass_header, text="¿Olvidaste tu clave?", font=("Arial", 11), 
                     text_color="#3b37d7", cursor="hand2").pack(side="right", padx=90)

        self.pass_entry = ctk.CTkEntry(self.right_frame, placeholder_text="🔒   ••••••••", 
                                       show="*", width=form_width, height=45, fg_color="#F2F2F2", border_width=0)
        self.pass_entry.pack(pady=(0, 15))

        # Checkbox
        self.check_var = ctk.BooleanVar()
        ctk.CTkCheckBox(self.right_frame, text="Recordar sesión por 30 días", variable=self.check_var,
                        font=("Arial", 12), border_width=2, checkbox_width=18, checkbox_height=18).pack(anchor="w", padx=75)

        # Botón
        self.btn_login = ctk.CTkButton(self.right_frame, text="Entrar al Sistema  →", 
                                       font=("Arial Bold", 15), width=form_width, height=50,
                                       fg_color="#4d44ef", hover_color="#3b37d7", corner_radius=10,
                                       command=self.login_action)
        self.btn_login.pack(pady=40)

        # Link de soporte
        ctk.CTkLabel(self.right_frame, text="¿No tienes acceso? Contacta al Administrador", 
                     font=("Arial", 12), text_color="#3b37d7", cursor="hand2").pack(side="bottom", pady=30)



    def login_action(self):
        usuario = self.user_entry.get()
        password = self.pass_entry.get()

        try:
            respuesta = cli.openSession(URL_SERVER, usuario, password)
            
            if "session updated" in respuesta.lower() or "ok" in respuesta.lower():
                # 1. Mostramos la carga inmediatamente
                self.right_frame.grid_forget()
                self.load_view = LoadingFrame(self, fg_color="white")
                self.load_view.grid(row=0, column=1, sticky="nsew")
                self.update() # Forzamos el dibujo inicial

                # 2. LANZAMOS LA CARGA EN SEGUNDO PLANO (THREADING)
                # Esto permite que la barra se siga moviendo mientras se importa el archivo
                hilo_carga = threading.Thread(target=self.proceso_de_carga, args=(usuario, password))
                hilo_carga.start()
                
            else:
                self.lc.configure(text="❌ Credenciales incorrectas", text_color="#E74C3C")
        
        except Exception as e:
            self.lc.configure(text="⚠️ Error de comunicación", text_color="#E74C3C")

    def proceso_de_carga(self, usuario, password):
        # 1. Registramos el tiempo de inicio
        inicio = time.time()
        
        # 2. Obtenemos el rol y hacemos los imports pesados
        rol = ath.get_user_role(usuario)
        
        if rol == "admin":
            import root2
            ClaseDestino = root2.App
        elif rol == "supervisor":
            import root3
            ClaseDestino = root3.App
        else:
            # Por si tienes un root por defecto
            import root2 
            ClaseDestino = root2.App

        # 3. CRUCIAL: Si los imports fueron muy rápidos, 
        # obligamos a que la animación dure al menos 3 segundos.
        tiempo_transcurrido = time.time() - inicio
        if tiempo_transcurrido < 3:
            time.sleep(3 - tiempo_transcurrido)

        # 4. PASO FINAL: Abrir la nueva ventana
        # Usamos withdraw() primero para que el login desaparezca 
        # JUSTO cuando la otra está por abrirse
        self.after(0, lambda: self.abrir_ventana_final(ClaseDestino, usuario, password))
    
    def abrir_ventana_final(self, ClaseApp, usuario, password):
        # 1. Creamos la nueva ventana pero NO la lanzamos con mainloop aún
        # La guardamos en una variable
        self.nueva_ventana = ClaseApp(usuario, password)
        
        # 2. Truco de oro: Esperamos 100ms para que la nueva ventana cargue sus widgets
        # y luego ocultamos el login.
        self.after(100, self.finalizar_transicion)
        
        # 3. Lanzamos el mainloop de la nueva
        self.nueva_ventana.mainloop()

    def finalizar_transicion(self):
        # Solo ocultamos y destruimos el login cuando sabemos 
        # que la otra ventana ya arrancó su proceso de dibujo
        self.withdraw()
        self.destroy()

    # 3. Nueva función para el paso final
    def final_step(self, usuario, password):
        rol = ath.get_user_role(usuario)
        
        if rol == "admin":
            self.withdraw()
            app_principal = root3.App(usuario, password)
        elif rol == "supervisor":
            self.withdraw()
            app_principal = root2.App(usuario, password)
        
        self.destroy()
        app_principal.mainloop()

class LoadingFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0,1), weight=1)

        # Animación de carga
        self.label = ctk.CTkLabel(self, text="🛡️ Inicializando entorno seguro...", 
                                  font=("Arial Bold", 20), text_color="#3b37d7")
        self.label.grid(row=0, column=0, pady=(100, 10))

        self.progress = ctk.CTkProgressBar(self, orientation="horizontal", 
                                           mode="indeterminate", width=300, 
                                           progress_color="#4d44ef")
        self.progress.grid(row=1, column=0, pady=(0, 100))
        self.progress.start()

if __name__ == "__main__":
    app = AppLogin()
    app.mainloop()