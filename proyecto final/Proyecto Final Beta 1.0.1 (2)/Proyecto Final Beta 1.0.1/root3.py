import customtkinter as ctk
from tkinter import messagebox, simpledialog
import supervision_client as cli
import json

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

        self.title("Contractify - Supervisor")
        self.geometry("1200x750")
        self.configure(fg_color=COLOR_BG_MAIN)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=COLOR_BG_SIDEBAR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # Logo
        ctk.CTkLabel(self.sidebar, text="🛡️ Contractify", font=ctk.CTkFont(size=22, weight="bold"), text_color="white").pack(pady=(30, 20), padx=20, anchor="w")
        
        # Menús
        self.crear_boton_menu("📊 Panel Principal", self.cargar_dashboard)
        self.crear_boton_menu("📄 Contratos", self.listar_contratos)
        self.crear_boton_menu("➕ Registrar Contrato", self.registrar_contrato)
        self.crear_boton_menu("👥 Registrar Usuario", self.registrar_usuario)
        self.crear_boton_menu("📈 Estadísticas", self.ver_estadisticas)
        self.crear_boton_menu("📁 Exportar CSV", self.exportar_csv)
        
        # Separador
        ctk.CTkFrame(self.sidebar, height=1, fg_color="#2c344d").pack(fill="x", padx=15, pady=20)
        
        # Usuario actual
        self.user_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.user_frame.pack(fill="x", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(self.user_frame, text="USUARIO ACTUAL", font=ctk.CTkFont(size=10), text_color="#9ca3af").pack(anchor="w")
        
        self.avatar_frame = ctk.CTkFrame(self.user_frame, fg_color="transparent")
        self.avatar_frame.pack(fill="x", pady=(5, 0))
        
        self.avatar = ctk.CTkLabel(self.avatar_frame, text="👤", font=ctk.CTkFont(size=28), text_color="white")
        self.avatar.pack(side="left", padx=(0, 10))
        
        self.user_info = ctk.CTkFrame(self.avatar_frame, fg_color="transparent")
        self.user_info.pack(side="left", fill="x")
        
        ctk.CTkLabel(self.user_info, text=self.usuario, font=ctk.CTkFont(size=14, weight="bold"), text_color="white").pack(anchor="w")
        ctk.CTkLabel(self.user_info, text="Supervisor", font=ctk.CTkFont(size=12), text_color="#9ca3af").pack(anchor="w")
        
        # Botón cerrar sesión
        self.btn_logout = ctk.CTkButton(self.sidebar, text="🚪 Cerrar Sesión", fg_color="transparent", 
                                        anchor="w", font=ctk.CTkFont(size=13), height=35,
                                        command=self.cerrar_sesion)
        self.btn_logout.pack(fill="x", padx=15, pady=(20, 10))

        # --- CONTENIDO PRINCIPAL ---
        self.main_container = ctk.CTkScrollableFrame(self, fg_color=COLOR_BG_MAIN, corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        self.header_label = ctk.CTkLabel(self.main_container, text="Panel de Administración", 
                                         text_color=COLOR_TEXT_MAIN, font=ctk.CTkFont(size=28, weight="bold"))
        self.header_label.pack(anchor="w", padx=30, pady=(20, 10))
        
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        self.cargar_dashboard()

    def crear_boton_menu(self, texto, comando):
        btn = ctk.CTkButton(self.sidebar, text=texto, fg_color="transparent", anchor="w", 
                            font=ctk.CTkFont(size=14), height=40, command=comando,
                            hover_color="#1e293b")
        btn.pack(fill="x", padx=15, pady=5)
        return btn

    def limpiar_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def cargar_dashboard(self):
        self.limpiar_content()
        self.header_label.configure(text="📊 Panel Principal")
        
        try:
            respuesta = cli.stats(URL, self.usuario, self.password)
            stats = json.loads(respuesta)
            
            if "error" in stats:
                ctk.CTkLabel(self.content_frame, text=f"Error: {stats['error']}", text_color="red").pack()
                return
            
            # Tarjetas
            frame_cards = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            frame_cards.pack(fill="x", pady=10)
            frame_cards.grid_columnconfigure((0,1,2), weight=1)
            
            cards = [
                ("Contratos Totales", str(stats.get("total_contracts", 0)), "+12%"),
                ("Valor Invertido", f"${stats.get('total_value', 0):,.0f}", ""),
                ("Valor Promedio", f"${stats.get('avg_value', 0):,.0f}", ""),
            ]
            
            for i, (title, value, extra) in enumerate(cards):
                card = ctk.CTkFrame(frame_cards, fg_color=COLOR_CARD, corner_radius=12, height=110)
                card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
                card.grid_propagate(False)
                ctk.CTkLabel(card, text=title, text_color=COLOR_TEXT_SECONDARY, font=("Arial", 12)).pack(anchor="w", padx=15, pady=(15, 0))
                ctk.CTkLabel(card, text=value, font=("Arial", 26, "bold")).pack(anchor="w", padx=15)
                if extra:
                    ctk.CTkLabel(card, text=extra, text_color="#10b981", font=("Arial", 11)).pack(anchor="w", padx=15, pady=(0, 10))
            
            # Contratos por estado
            ctk.CTkLabel(self.content_frame, text="📊 Contratos por Estado", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(20, 10))
            frame_estados = ctk.CTkFrame(self.content_frame, fg_color=COLOR_CARD, corner_radius=12)
            frame_estados.pack(fill="x", pady=5)
            
            estados = stats.get("total_by_status", {})
            for estado, count in estados.items():
                color = {"ACTIVO": "#10b981", "SUSPENDIDO": "#f59e0b", "TERMINADO": "#ef4444"}.get(estado, "#6b7280")
                ctk.CTkLabel(frame_estados, text=f"{estado}: {count}", font=("Arial", 14), text_color=color).pack(side="left", padx=30, pady=15)
            
            # Contratos por vencer
            soon = stats.get("contracts_soon_to_end", [])
            if soon:
                ctk.CTkLabel(self.content_frame, text="⚠️ Contratos que vencen en 30 días", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(20, 10))
                soon_frame = ctk.CTkFrame(self.content_frame, fg_color=COLOR_CARD, corner_radius=12)
                soon_frame.pack(fill="x", pady=5)
                for c in soon[:5]:
                    ctk.CTkLabel(soon_frame, text=f"📄 {c['number']} - {c['contractor']} (Vence: {c['end']})", anchor="w").pack(fill="x", padx=20, pady=8)
            
            # Mayor y menor
            max_c = stats.get("max_contract")
            min_c = stats.get("min_contract")
            
            if max_c:
                ctk.CTkLabel(self.content_frame, text=f"💰 Contrato mayor valor: {max_c['number']} - ${max_c['value']:,.0f}", anchor="w").pack(pady=5)
            if min_c:
                ctk.CTkLabel(self.content_frame, text=f"💰 Contrato menor valor: {min_c['number']} - ${min_c['value']:,.0f}", anchor="w").pack(pady=5)
                
        except Exception as e:
            ctk.CTkLabel(self.content_frame, text=f"Error cargando datos: {e}", text_color="red").pack()

    def listar_contratos(self):
        self.limpiar_content()
        self.header_label.configure(text="📋 Gestión de Contratos")
        
        try:
            respuesta = cli.listContracts(URL, self.usuario, self.password)
            data = json.loads(respuesta)
            
            if "error" in data:
                ctk.CTkLabel(self.content_frame, text=f"Error: {data['error']}", text_color="red").pack()
                return
            
            contratos = data.get("contracts", [])
            
            if not contratos:
                ctk.CTkLabel(self.content_frame, text="No hay contratos registrados").pack(pady=40)
                return
            
            headers = ["CÓDIGO", "CONTRATISTA", "FECHA FIN", "VALOR", "ESTADO"]
            for i, h in enumerate(headers):
                ctk.CTkLabel(self.content_frame, text=h, font=ctk.CTkFont(weight="bold"), 
                            text_color=COLOR_TEXT_SECONDARY).grid(row=0, column=i, padx=15, pady=10, sticky="w")
            
            for row, c in enumerate(contratos, start=1):
                ctk.CTkLabel(self.content_frame, text=c.get("number", ""), width=100, anchor="w").grid(row=row, column=0, padx=15, pady=8, sticky="w")
                ctk.CTkLabel(self.content_frame, text=c.get("contractor", "")[:30], width=200, anchor="w").grid(row=row, column=1, padx=15, pady=8, sticky="w")
                ctk.CTkLabel(self.content_frame, text=c.get("end", ""), width=110, anchor="w").grid(row=row, column=2, padx=15, pady=8, sticky="w")
                valor = c.get("value", 0)
                ctk.CTkLabel(self.content_frame, text=f"${valor:,.0f}", width=120, anchor="w").grid(row=row, column=3, padx=15, pady=8, sticky="w")
                
                estado = c.get("status", "")
                color = {"ACTIVO": "#10b981", "SUSPENDIDO": "#f59e0b", "TERMINADO": "#ef4444"}.get(estado, "#6b7280")
                ctk.CTkLabel(self.content_frame, text=estado, text_color=color, font=ctk.CTkFont(weight="bold")).grid(row=row, column=4, padx=15, pady=8, sticky="w")
                
        except Exception as e:
            ctk.CTkLabel(self.content_frame, text=f"Error: {e}", text_color="red").pack()

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
                    self.cargar_dashboard()
            except Exception as e:
                messagebox.showerror("Error", f"Error al registrar: {e}")
        
        ctk.CTkButton(scroll, text="Guardar", command=guardar, fg_color=COLOR_ACCENT).pack(pady=20)

    def registrar_usuario(self):
        self.limpiar_content()
        self.header_label.configure(text="👥 Registrar Nuevo Usuario")
        
        ctk.CTkLabel(self.content_frame, text="Usuario*").pack(anchor="w", pady=(10, 0))
        user_entry = ctk.CTkEntry(self.content_frame, width=350)
        user_entry.pack(pady=5)
        
        ctk.CTkLabel(self.content_frame, text="Contraseña*").pack(anchor="w", pady=(10, 0))
        pass_entry = ctk.CTkEntry(self.content_frame, width=350, show="*")
        pass_entry.pack(pady=5)
        
        ctk.CTkLabel(self.content_frame, text="Rol* (admin / supervisor / viewer)").pack(anchor="w", pady=(10, 0))
        role_entry = ctk.CTkEntry(self.content_frame, width=350)
        role_entry.pack(pady=5)
        
        def guardar():
            user = user_entry.get().strip()
            pwd = pass_entry.get().strip()
            role = role_entry.get().strip().lower()
            
            if not user or not pwd or not role:
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
            
            if role not in ["admin", "supervisor", "viewer"]:
                messagebox.showerror("Error", "Rol inválido. Use: admin, supervisor o viewer")
                return
            
            try:
                respuesta = cli.registerUser(URL, user, pwd, role)
                res = json.loads(respuesta)
                
                if "error" in res:
                    messagebox.showerror("Error", res["error"])
                else:
                    messagebox.showinfo("Éxito", f"Usuario {user} registrado como {role}")
                    user_entry.delete(0, "end")
                    pass_entry.delete(0, "end")
                    role_entry.delete(0, "end")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")
        
        ctk.CTkButton(self.content_frame, text="Registrar Usuario", command=guardar, fg_color=COLOR_ACCENT).pack(pady=30)

    def ver_estadisticas(self):
        self.limpiar_content()
        self.header_label.configure(text="📈 Estadísticas Detalladas")
        
        try:
            respuesta = cli.stats(URL, self.usuario, self.password)
            stats = json.loads(respuesta)
            
            if "error" in stats:
                ctk.CTkLabel(self.content_frame, text=f"Error: {stats['error']}", text_color="red").pack()
                return
            
            texto = f"""
📊 ESTADÍSTICAS DEL SISTEMA

📌 Contratos totales: {stats.get('total_contracts', 0)}
💰 Valor total invertido: ${stats.get('total_value', 0):,.0f}
📈 Valor promedio por contrato: ${stats.get('avg_value', 0):,.0f}

📋 Por estado:
   • ACTIVO: {stats.get('total_by_status', {}).get('ACTIVO', 0)}
   • SUSPENDIDO: {stats.get('total_by_status', {}).get('SUSPENDIDO', 0)}
   • TERMINADO: {stats.get('total_by_status', {}).get('TERMINADO', 0)}

⚠️ Contratos por vencer (30 días): {len(stats.get('contracts_soon_to_end', []))}
"""
            
            ctk.CTkLabel(self.content_frame, text=texto, justify="left", font=("Consolas", 13)).pack(anchor="w", pady=20)
            
        except Exception as e:
            ctk.CTkLabel(self.content_frame, text=f"Error: {e}", text_color="red").pack()

    def exportar_csv(self):
        try:
            respuesta = cli.exportCsv(URL, self.usuario, self.password)
            res = json.loads(respuesta)
            
            if "error" in res:
                messagebox.showerror("Error", res["error"])
            else:
                messagebox.showinfo("Éxito", "Datos exportados a contracts.csv y trackings.csv")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {e}")

    def cerrar_sesion(self):
        try:
            cli.closeSession(URL, self.usuario, self.password)
        except:
            pass
        self.destroy()
        import root1
        login = root1.AppLogin()
        login.mainloop()


if __name__ == "__main__":
    app = App("admin1", "adm")
    app.mainloop()