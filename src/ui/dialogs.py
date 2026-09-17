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
            hover_color="#0F172A",
            border_width=1,
            border_color="#334155",
            text_color="#FFFFFF",
            command=lambda: webbrowser.open("https://github.com/silent404s/IndexRadar")
        )
        btn_repo.pack(pady=(0, 15))
        
        btn_close = ctk.CTkButton(
            frame, 
            text="Tutup", 
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="#1E293B", 
            hover_color="#0F172A",
            text_color="#FFFFFF",
            width=100,
            command=self.destroy
        )
        btn_close.pack(pady=(0, 10))

