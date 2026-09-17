import customtkinter as ctk
import webbrowser

class AboutDialog(ctk.CTkToplevel):
    def __init__(self, parent, version="1.0.0"):
        super().__init__(parent)
        self.title("Tentang IndexRadar Pro")
        self.geometry("450x380")
        self.resizable(False, False)
        self.configure(fg_color="#0B0F19")
        
        self.transient(parent)
        self.grab_set()
        
        frame = ctk.CTkFrame(self, fg_color="#111827", corner_radius=12, border_width=1, border_color="#1E293B")
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Icon / Title
        lbl_title = ctk.CTkLabel(
            frame, 
            text="🎯 IndexRadar Pro", 
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#10B981"
        )
        lbl_title.pack(pady=(20, 4))
        
        lbl_sub = ctk.CTkLabel(
            frame, 
            text="High-Performance Bulk Google Index Checker", 
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#94A3B8"
        )
        lbl_sub.pack(pady=(0, 10))
        
        lbl_ver = ctk.CTkLabel(
            frame, 
            text=f"Versi: v{version}", 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#38BDF8"
        )
        lbl_ver.pack(pady=(0, 15))
        
        # Info Box
        desc_text = (
            "Aplikasi otomatisasi untuk memeriksa status pengindeksan Google "
            "secara massal dan cepat, dilengkapi engine headless anti-detection, "
            "resolusi CAPTCHA terintegrasi, serta sistem pelacakan pembaruan otomatis."
        )
        lbl_desc = ctk.CTkLabel(
            frame, 
            text=desc_text, 
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#CBD5E1",
            wraplength=380,
            justify="center"
        )
        lbl_desc.pack(padx=20, pady=(0, 20))
        
        btn_repo = ctk.CTkButton(
            frame,
            text="🌐 Kunjungi Repository GitHub",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#1E293B",
            hover_color="#334155",
            command=lambda: webbrowser.open("https://github.com/silent404s/IndexRadar")
        )
        btn_repo.pack(pady=(0, 15))
        
        btn_close = ctk.CTkButton(
            frame, 
            text="Tutup", 
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="#334155", 
            hover_color="#475569",
            width=100,
            command=self.destroy
        )
        btn_close.pack(pady=(0, 10))

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, current_config, on_save_callback=None):
        super().__init__(parent)
        self.title("⚙️ Pengaturan Aplikasi")
        self.geometry("480x420")
        self.resizable(False, False)
        self.configure(fg_color="#0B0F19")
        
        self.current_config = current_config
        self.on_save_callback = on_save_callback
        
        self.transient(parent)
        self.grab_set()
        
        frame = ctk.CTkFrame(self, fg_color="#111827", corner_radius=12, border_width=1, border_color="#1E293B")
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        lbl_head = ctk.CTkLabel(
            frame, 
            text="⚙️ Pengaturan & Konfigurasi", 
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#E2E8F0"
        )
        lbl_head.pack(anchor="w", padx=20, pady=(15, 10))
        
        # 2Captcha API Key
        ctk.CTkLabel(frame, text="2Captcha API Key:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#94A3B8").pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_key = ctk.CTkEntry(frame, font=ctk.CTkFont(family="Consolas", size=11), fg_color="#0B0F19", border_color="#334155")
        self.entry_key.insert(0, current_config.get("captcha_api_key", ""))
        self.entry_key.pack(fill="x", padx=20, pady=(0, 20))
        
        # Buttons
        btn_box = ctk.CTkFrame(frame, fg_color="transparent")
        btn_box.pack(fill="x", padx=20, pady=(10, 15))
        
        btn_save = ctk.CTkButton(
            btn_box, 
            text="💾 Simpan Pengaturan", 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            command=self.save_settings
        )
        btn_save.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        btn_cancel = ctk.CTkButton(
            btn_box, 
            text="Batal", 
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="#334155",
            hover_color="#475569",
            width=90,
            command=self.destroy
        )
        btn_cancel.pack(side="right")

    def save_settings(self):
        new_key = self.entry_key.get().strip()
        self.current_config["captcha_api_key"] = new_key
        
        if self.on_save_callback:
            self.on_save_callback(self.current_config)
        self.destroy()
