import customtkinter as ctk
from tkinter import messagebox, simpledialog, Toplevel, Text, Scrollbar
import supervision_client as cli
import json, root1
import threading

# Configuración de colores
COLOR_BG_SIDEBAR = "#121726"
COLOR_BG_MAIN = "#f3f4f6"
COLOR_CARD = "white"
COLOR_ACCENT = "#4f46e5"
COLOR_ACCENT_HOVER = "#6366f1"
COLOR_TEXT_MAIN = "#111827"
COLOR_TEXT_SECONDARY = "#6b7280"

URL = "http://localhost:8080"

class App(ctk.CTk):
    def __init__(self, usuario, password):
        super().__init__()

        self.usuario = usuario
        self.password = password

        self.title("Contractify - Administrador")
        self.geometry("1200x750")
        self.configure(fg_color=COLOR_BG_MAIN)

        self.submenu_visible = False

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- BARRA LATERAL ---
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=COLOR_BG_SIDEBAR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # Logo
        self.logo = ctk.CTkLabel(self.sidebar, text="🛡️ Contractify", font=ctk.CTkFont(size=22, weight="bold"), text_color="white")
        self.logo.pack(pady=(30, 20), padx=20, anchor="w")
        
        # Panel Principal
        self.btn_panel = self.crear_boton_menu("📊 Panel Principal", "transparent", self.cargar_panel)
        
        # Contratos (desplegable)
        self.btn_contratos = ctk.CTkButton(
            self.sidebar, text="📄 Contratos  ▼", fg_color="transparent", 
            anchor="w", font=ctk.CTkFont(size=14), height=40,
            command=self.toggle_submenu
        )
        self.btn_contratos.pack(fill="x", padx=15, pady=5)

        # Submenú Contratos
        self.submenu_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.sub_list_contracts = self.crear_sub_boton("Listar Contratos", self.listar_contratos)
        self.sub_search = self.crear_sub_boton("Buscar Contrato", self.buscar_contrato)
        self.sub_add_track = self.crear_sub_boton("Añadir Seguimiento", self.anadir_seguimiento)
        self.sub_list_track = self.crear_sub_boton("Ver Seguimientos", self.ver_seguimientos)
        
        # Usuarios y Configuración
        self.btn_usuarios = self.crear_boton_menu("👥 Usuarios", "transparent", self.ver_mis_datos)
        self.btn_config = self.crear_boton_menu("⚙️ Configuración", "transparent", self.ver_configuracion)
        
        # Separador
        ctk.CTkFrame(self.sidebar, height=1, fg_color="#2c344d").pack(fill="x", padx=15, pady=20)
        
        # Usuario actual
        self.user_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.user_frame.pack(fill="x", padx=15, pady=(20, 10))
        
        self.avatar = ctk.CTkLabel(self.user_frame, text="👤", font=ctk.CTkFont(size=24), text_color="white")
        self.avatar.pack(side="left", padx=(0, 10))
        
        self.user_info = ctk.CTkFrame(self.user_frame, fg_color="transparent")
        self.user_info.pack(side="left", fill="x")
        
        ctk.CTkLabel(self.user_info, text=self.usuario, font=ctk.CTkFont(size=13, weight="bold"), text_color="white").pack(anchor="w")
        ctk.CTkLabel(self.user_info, text="Administrador", font=ctk.CTkFont(size=11), text_color="#9ca3af").pack(anchor="w")
        
        # Botón cerrar sesión
        self.btn_logout = ctk.CTkButton(self.sidebar, text="🚪 Cerrar Sesión", fg_color="transparent", 
                                        anchor="w", font=ctk.CTkFont(size=13), height=35,
                                        command=self.cerrar_sesion)
        self.btn_logout.pack(fill="x", padx=15, pady=(20, 10))

        # --- CONTENIDO PRINCIPAL ---
        self.main_container = ctk.CTkScrollableFrame(self, fg_color=COLOR_BG_MAIN, corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        self.header_label = ctk.CTkLabel(self.main_container, text="Panel de Control", 
                                         text_color=COLOR_TEXT_MAIN, font=ctk.CTkFont(size=28, weight="bold"))
        self.header_label.pack(anchor="w", padx=30, pady=(20, 10))
        
        # Tarjetas
        self.metrics_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.metrics_frame.pack(fill="x", padx=20, pady=10)
        self.metrics_frame.grid_columnconfigure((0,1,2,3), weight=1)
        
        self.card_total = self.create_card(0, "Contratos Totales", "0", "+12%")
        self.card_valor = self.create_card(1, "Valor Invertido", "$0", "")
        self.card_progreso = self.create_card(2, "Progreso Medio", "68.4%", "")
        self.card_por_vencer = self.create_card(3, "Por Vencer (30d)", "0", "⚠️")
        
        # Barra de progreso
        self.progress_bar = ctk.CTkProgressBar(self.card_progreso, width=150, height=6, progress_color="#10b981")
        self.progress_bar.pack(anchor="w", padx=15, pady=(5, 15))
        self.progress_bar.set(0)
        
        # Tabla
        self.table_bg = ctk.CTkFrame(self.main_container, fg_color=COLOR_CARD, corner_radius=16)
        self.table_bg.pack(fill="both", expand=True, padx=30, pady=20)
        
        self.table_header = ctk.CTkFrame(self.table_bg, fg_color="transparent", height=50)
        self.table_header.pack(fill="x", padx=24, pady=(20, 10))
        
        ctk.CTkLabel(self.table_header, text="Gestión de Contratos", 
                     text_color=COLOR_TEXT_MAIN, font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        
        self.btn_new = ctk.CTkButton(self.table_header, text="+ Nuevo Contrato", fg_color=COLOR_ACCENT, 
                                     hover_color=COLOR_ACCENT_HOVER, width=140, height=38,
                                     font=ctk.CTkFont(size=13, weight="bold"), command=self.registrar_contrato)
        self.btn_new.pack(side="right", padx=5)
        
        ctk.CTkLabel(self.table_bg, text="Gestione, busque y añada seguimientos detallados.", 
                     text_color=COLOR_TEXT_SECONDARY, font=ctk.CTkFont(size=13)).pack(anchor="w", padx=24, pady=(0, 15))
        
        self.table_container = ctk.CTkFrame(self.table_bg, fg_color="transparent")
        self.table_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Headers de la tabla
        self.headers_frame = ctk.CTkFrame(self.table_container, fg_color="transparent")
        self.headers_frame.pack(fill="x", pady=(0, 10))
        
        headers = ["CÓDIGO", "CONTRATISTA", "FECHA FIN", "VALOR", "ESTADO", "ACCIÓN"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(self.headers_frame, text=header, width=120 if i == 0 else 150 if i == 1 else 110 if i == 2 else 120 if i == 3 else 100 if i == 4 else 100, 
                         font=ctk.CTkFont(size=13, weight="bold"), text_color=COLOR_TEXT_SECONDARY).grid(row=0, column=i, padx=5, pady=5, sticky="w")
        
        self.rows_frame = ctk.CTkFrame(self.table_container, fg_color="transparent")
        self.rows_frame.pack(fill="both", expand=True)
        
        # Cargar datos iniciales
        self.cargar_panel()

    def crear_boton_menu(self, texto, color, comando):
        btn = ctk.CTkButton(self.sidebar, text=texto, fg_color=color, anchor="w", 
                            font=ctk.CTkFont(size=14), height=40, command=comando)
        btn.pack(fill="x", padx=15, pady=5)
        return btn

    def crear_sub_boton(self, texto, comando):
        btn = ctk.CTkButton(self.submenu_frame, text=f"  • {texto}", fg_color="transparent", 
                            anchor="w", font=ctk.CTkFont(size=12), height=30, hover_color="#1e2538",
                            command=comando)
        btn.pack(fill="x", padx=(35, 15), pady=2)
        return btn

    def toggle_submenu(self):
        if self.submenu_visible:
            self.submenu_frame.pack_forget()
            self.btn_contratos.configure(text="📄 Contratos  ▶")
        else:
            self.submenu_frame.pack(fill="x", after=self.btn_contratos)
            self.btn_contratos.configure(text="📄 Contratos  ▼")
        self.submenu_visible = not self.submenu_visible

    def create_card(self, col, title, value, extra):
        card = ctk.CTkFrame(self.metrics_frame, fg_color=COLOR_CARD, corner_radius=12, height=110)
        card.grid(row=0, column=col, padx=10, pady=10, sticky="nsew")
        card.grid_propagate(False)
        
        ctk.CTkLabel(card, text=title, text_color=COLOR_TEXT_SECONDARY, font=("Arial", 12)).pack(anchor="w", padx=15, pady=(15, 0))
        
        value_label = ctk.CTkLabel(card, text=value, text_color=COLOR_TEXT_MAIN, font=("Arial", 26, "bold"))
        value_label.pack(anchor="w", padx=15)
        
        if extra and extra != "⚠️":
            ctk.CTkLabel(card, text=extra, text_color="#10b981" if "+" in extra else "#ef4444", 
                        font=("Arial", 11)).pack(anchor="w", padx=15, pady=(0, 10))
        elif extra == "⚠️":
            ctk.CTkLabel(card, text="⚠️", text_color="#f59e0b", font=("Arial", 16)).pack(anchor="w", padx=15, pady=(0, 10))
        
        setattr(self, f"card_{col}_label", value_label)
        return card

    def limpiar_filas(self):
        for widget in self.rows_frame.winfo_children():
            widget.destroy()

    def mostrar_contratos_en_tabla(self, contratos):
        self.limpiar_filas()
        
        if not contratos:
            ctk.CTkLabel(self.rows_frame, text="No hay contratos registrados", text_color=COLOR_TEXT_SECONDARY).pack(pady=40)
            return
        
        for row, c in enumerate(contratos):
            row_frame = ctk.CTkFrame(self.rows_frame, fg_color="transparent", height=50)
            row_frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row_frame, text=c.get("number", ""), width=120, font=ctk.CTkFont(size=13, weight="bold"),
                        text_color=COLOR_ACCENT, anchor="w").grid(row=0, column=0, padx=5, pady=8, sticky="w")
            
            ctk.CTkLabel(row_frame, text=c.get("contractor", "")[:30], width=150, anchor="w").grid(row=0, column=1, padx=5, pady=8, sticky="w")
            
            ctk.CTkLabel(row_frame, text=c.get("end", ""), width=110, anchor="w").grid(row=0, column=2, padx=5, pady=8, sticky="w")
            
            valor = c.get("value", 0)
            valor_str = f"${valor:,.0f}" if isinstance(valor, (int, float)) else f"${valor}"
            ctk.CTkLabel(row_frame, text=valor_str, width=120, anchor="w").grid(row=0, column=3, padx=5, pady=8, sticky="w")
            
            estado = c.get("status", "")
            estado_color = {"ACTIVO": "#10b981", "SUSPENDIDO": "#f59e0b", "TERMINADO": "#ef4444"}.get(estado, "#6b7280")
            ctk.CTkLabel(row_frame, text=estado, width=100, text_color=estado_color, 
                        font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=0, column=4, padx=5, pady=8, sticky="w")
            
            self.btn_ver = ctk.CTkButton(row_frame, text="Ver", width=70, height=30,
                                   fg_color="transparent", text_color=COLOR_ACCENT,
                                   hover_color="#eef2ff", border_width=0,
                                   command=lambda num=c.get("number"): self.ver_detalle_contrato(num))
            self.btn_ver.grid(row=0, column=5, padx=5, pady=8, sticky="w")

    def ver_detalle_contrato(self, numero):
        """1. Inicia la búsqueda en un hilo para no congelar la ventana"""
        def hilo_busqueda():
            try:
                # Petición al servidor (esto es lo que tardaba y lagueaba)
                respuesta = cli.searchContract(URL, self.usuario, self.password, numero)
                data = json.loads(respuesta)
                
                # 2. Volvemos al hilo principal para dibujar la interfaz
                # Usamos self.after para que 'self' sea válido y cargue los paneles
                self.after(0, lambda: self.dibujar_interfaz_detalle(data, numero))
                
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Error de red: {e}"))

        threading.Thread(target=hilo_busqueda, daemon=True).start()

    def dibujar_interfaz_detalle(self, data, numero):
        """3. Dibuja la ventana. Aquí self ya funciona y no falla."""
        if "error" in data:
            messagebox.showerror("Error", data["error"])
            return
        
        # IMPORTANTE: Verificar que la ventana principal sigue viva
        if not self.winfo_exists():
            return

        # Ahora creamos el Toplevel
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Detalle Contrato - {numero}")
        dialog.geometry("700x500")
        
        # Levantar la ventana por encima de la principal
        dialog.after(100, dialog.lift)
        dialog.after(100, dialog.focus_force)

        # Aquí pegas el resto de tu código que crea el scroll_frame, labels, etc.
        # Al estar dentro de la clase, 'self.anadir_seguimiento' y otros funcionarán.
        scroll_frame = ctk.CTkScrollableFrame(dialog, fg_color=COLOR_BG_MAIN)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def cargar_panel(self):
        self.header_label.configure(text="Panel de Control")
        self.cargar_stats()
        self.listar_contratos()

    def cargar_stats(self):
        try:
            respuesta = cli.stats(URL, self.usuario, self.password)
            stats = json.loads(respuesta)
            
            if "error" in stats:
                return
            
            total = stats.get("total_contracts", 0)
            total_valor = stats.get("total_value", 0)
            
            self.card_0_label.configure(text=str(total))
            self.card_1_label.configure(text=f"${total_valor:,.0f}")
            
            soon = len(stats.get("contracts_soon_to_end", []))
            self.card_3_label.configure(text=str(soon))
            
        except Exception as e:
            print(f"Error cargando stats: {e}")

    def listar_contratos(self):
        self.header_label.configure(text="📋 Gestión de Contratos")
        try:
            respuesta = cli.listContracts(URL, self.usuario, self.password)
            data = json.loads(respuesta)
            
            if "error" in data:
                messagebox.showerror("Error", data["error"])
                return
            
            contratos = data.get("contracts", [])
            self.mostrar_contratos_en_tabla(contratos)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar al servidor: {e}")

    def buscar_contrato(self):
        numero = simpledialog.askstring("Buscar Contrato", "Ingrese el número del contrato:")
        if not numero:
            return
        
        try:
            respuesta = cli.searchContract(URL, self.usuario, self.password, numero)
            data = json.loads(respuesta)
            
            if "error" in data:
                messagebox.showerror("Error", data["error"])
                return
            
            self.mostrar_contratos_en_tabla([data])
            self.header_label.configure(text=f"🔍 Resultado de búsqueda: {numero}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")

    def registrar_contrato(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Registrar Contrato")
        dialog.geometry("500x650")
        dialog.configure(fg_color=COLOR_BG_MAIN)
        
        scroll = ctk.CTkScrollableFrame(dialog, fg_color=COLOR_BG_MAIN)
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        campos = [
            ("number", "Número del contrato*"),
            ("contractor", "Contratista*"),
            ("object", "Objeto del contrato*"),
            ("start", "Fecha inicio (dd/mm/aaaa)*"),
            ("end", "Fecha fin (dd/mm/aaaa)*"),
            ("value", "Valor*"),
            ("supervisor", "Supervisor*"),
            ("status", "Estado (ACTIVO/SUSPENDIDO/TERMINADO)*"),
            ("email", "Email*")
        ]
        
        entries = {}
        for key, label in campos:
            ctk.CTkLabel(scroll, text=label).pack(anchor="w", pady=(10, 0))
            entry = ctk.CTkEntry(scroll, width=400)
            entry.pack(pady=5)
            entries[key] = entry
        
        def guardar():
            data = {k: e.get().strip() for k, e in entries.items()}
            
            if not all(data.values()):
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
            
            try:
                respuesta = cli.registerContract(
                    URL, self.usuario, self.password,
                    data["number"], data["contractor"], data["object"],
                    data["start"], data["end"], data["value"],
                    data["supervisor"], data["status"], data["email"]
                )
                res = json.loads(respuesta)
                
                if "error" in res:
                    messagebox.showerror("Error", res["error"])
                else:
                    messagebox.showinfo("Éxito", "Contrato registrado correctamente")
                    dialog.destroy()
                    self.listar_contratos()
                    self.cargar_stats()
            except Exception as e:
                messagebox.showerror("Error", f"Error al registrar: {e}")
        
        ctk.CTkButton(scroll, text="Guardar", command=guardar, fg_color=COLOR_ACCENT).pack(pady=20)

    def anadir_seguimiento(self, numero=None, parent_dialog=None):
        if numero is None:
            numero = simpledialog.askstring("Añadir Seguimiento", "Número del contrato:")
        if not numero:
            return
        
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Añadir Seguimiento - {numero}")
        dialog.geometry("450x500")
        dialog.configure(fg_color=COLOR_BG_MAIN)
        
        ctk.CTkLabel(dialog, text="Fecha (dd/mm/aaaa)*").pack(pady=(20, 0), anchor="w", padx=30)
        date_entry = ctk.CTkEntry(dialog, width=350)
        date_entry.pack(pady=5, padx=30)
        
        ctk.CTkLabel(dialog, text="Descripción*").pack(pady=(10, 0), anchor="w", padx=30)
        desc_entry = ctk.CTkEntry(dialog, width=350)
        desc_entry.pack(pady=5, padx=30)
        
        ctk.CTkLabel(dialog, text="Progreso (0-100)*").pack(pady=(10, 0), anchor="w", padx=30)
        prog_entry = ctk.CTkEntry(dialog, width=350)
        prog_entry.pack(pady=5, padx=30)
        
        ctk.CTkLabel(dialog, text="Observaciones").pack(pady=(10, 0), anchor="w", padx=30)
        obs_entry = ctk.CTkEntry(dialog, width=350)
        obs_entry.pack(pady=5, padx=30)
        
        def guardar():
            fecha = date_entry.get().strip()
            desc = desc_entry.get().strip()
            progreso = prog_entry.get().strip()
            obs = obs_entry.get().strip()
            
            if not fecha or not desc or not progreso:
                messagebox.showerror("Error", "Fecha, descripción y progreso son obligatorios")
                return
            
            try:
                respuesta = cli.addTracking(URL, self.usuario, self.password, numero, fecha, desc, progreso, obs)
                res = json.loads(respuesta)
                
                if "error" in res:
                    messagebox.showerror("Error", res["error"])
                else:
                    messagebox.showinfo("Éxito", "Seguimiento añadido correctamente")
                    dialog.destroy()
                    if parent_dialog:
                        parent_dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")
        
        ctk.CTkButton(dialog, text="Guardar", command=guardar, fg_color=COLOR_ACCENT).pack(pady=20)

    def ver_seguimientos(self):
        numero = simpledialog.askstring("Ver Seguimientos", "Número del contrato:")
        if not numero:
            return
        
        try:
            respuesta = cli.listTrackings(URL, self.usuario, self.password, numero)
            data = json.loads(respuesta)
            
            if "error" in data:
                messagebox.showerror("Error", data["error"])
                return
            
            trackings = data.get("trackings", [])
            
            dialog = ctk.CTkToplevel(self)
            dialog.title(f"Seguimientos - {numero}")
            dialog.geometry("700x450")
            dialog.configure(fg_color=COLOR_BG_MAIN)
            
            text_area = Text(dialog, wrap="word", font=("Consolas", 11), bg=COLOR_CARD, fg=COLOR_TEXT_MAIN)
            scrollbar = Scrollbar(dialog, command=text_area.yview)
            text_area.configure(yscrollcommand=scrollbar.set)
            
            text_area.pack(side="left", fill="both", expand=True, padx=15, pady=15)
            scrollbar.pack(side="right", fill="y")
            
            if not trackings:
                text_area.insert("1.0", "No hay seguimientos para este contrato")
            else:
                text_area.insert("1.0", f"SEGUIMIENTOS DEL CONTRATO {numero}\n{'='*50}\n\n")
                for t in trackings:
                    text_area.insert("end", f"📅 ID: {t.get('id')} | Fecha: {t.get('date')}\n")
                    text_area.insert("end", f"📝 Descripción: {t.get('desc')}\n")
                    text_area.insert("end", f"📊 Progreso: {t.get('progress')}%\n")
                    text_area.insert("end", f"💬 Observaciones: {t.get('obs')}\n")
                    text_area.insert("end", "-" * 50 + "\n\n")
            
            text_area.configure(state="disabled")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")

    def ver_mis_datos(self):
        messagebox.showinfo("Info", f"Usuario: {self.usuario}\nRol: Supervisor\nPuede gestionar contratos y seguimientos.")

    def ver_configuracion(self):
        messagebox.showinfo("Configuración", "Preferencias guardadas localmente.\nTema: Claro\nIdioma: Español")

    def cerrar_sesion(self):
        try:
            cli.closeSession(URL, self.usuario, self.password)
        except:
            pass
        # En lugar de solo self.destroy()
        self.after(100, self.destroy)
        login = root1.AppLogin()
        login.mainloop()


if __name__ == "__main__":
    app = App("testuser", "testpass")
    app.mainloop()