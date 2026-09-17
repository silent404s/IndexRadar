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


class HelpInfoDialog(ctk.CTkToplevel):
    HELP_DATA = {
        "threads": {
            "title": "⚡ Penjelasan Fungsi: Threads",
            "summary": "Threads menentukan berapa banyak browser headless Chromium yang bekerja secara bersamaan (paralel) di latar belakang.",
            "points": [
                ("Prinsip Kerja:", "Jika Threads = 1, program mengecek domain satu per satu secara berurutan. Jika Threads = 3, program menjalankan 3 browser sekaligus sehingga 3 domain diperiksa pada detik yang sama (proses ~3x lebih cepat)."),
                ("Konsumsi Sumber Daya:", "Tiap 1 thread menjalankan 1 instance browser Chromium. Semakin tinggi threads, penggunaan memori RAM komputer akan bertambah."),
                ("Rekomendasi Wi-Fi / IP Pribadi:", "Gunakan 1 atau 2 threads agar pola pencarian tidak dicurigai sebagai bot oleh Google."),
                ("Rekomendasi dengan Proxy / 2Captcha:", "Gunakan 3 hingga 5 threads untuk mempercepat pengecekan ratusan/ribuan domain.")
            ],
            "tip": "💡 Tips: Jika sering muncul CAPTCHA Google, gunakan nilai Threads 1 atau 2 dan perbesar jeda waktu."
        },
        "delay": {
            "title": "⏱️ Penjelasan Fungsi: Jeda (Delay)",
            "summary": "Jeda adalah waktu istirahat (dalam detik) antar pencarian yang dilakukan oleh masing-masing browser worker.",
            "points": [
                ("Prinsip Kerja:", "Setelah satu domain selesai dicek, browser akan berhenti sejenak selama durasi jeda yang Anda tentukan sebelum mengirim kueri berikutnya ke Google."),
                ("Human-Like Jitter:", "Sistem otomatis menambahkan variasi acak halus (+/- 0.8s s/d 1.8s) agar ritme pencarian menyerupai perilaku penjelajahan manusia."),
                ("Opsi Cepat (1.0 - 1.5 detik):", "Hanya disarankan jika Anda menggunakan daftar proxy bergilir (rotating proxy)."),
                ("Opsi Aman (2.0 - 3.0 detik):", "Standar rekomendasi terbaik untuk menjaga alamat IP tetap aman dan tidak mudah diblokir oleh Google.")
            ],
            "tip": "💡 Tips: Nilai 2.0 detik adalah rasio paling ideal antara kecepatan proses dan keamanan IP."
        },
        "proxy": {
            "title": "🌐 Penjelasan Fungsi: Proxy List",
            "summary": "Proxy berfungsi mengalihkan dan menyamarkan alamat IP koneksi pencarian Google agar tidak menggunakan IP internet utama Anda.",
            "points": [
                ("Format Penulisan:", "Masukkan 1 proxy per baris dengan format ip:port atau http://user:pass@ip:port (contoh: 123.45.67.89:8080)."),
                ("Kapan Dibutuhkan?:", "Sangat dianjurkan ketika Anda ingin memeriksa ratusan atau ribuan domain dengan threads tinggi tanpa khawatir IP Wi-Fi/kantor Anda terkena limit atau CAPTCHA dari Google."),
                ("Sifat Opsional:", "Fitur ini bersifat opsional. Jika Anda hanya mengecek sedikit domain, kolom ini dapat dibiarkan kosong.")
            ],
            "tip": "💡 Tips: Pastikan proxy yang dimasukkan aktif dan memiliki kecepatan respons yang stabil."
        }
    }

    def __init__(self, parent, topic="threads"):
        super().__init__(parent)
        data = self.HELP_DATA.get(topic, self.HELP_DATA["threads"])
        
        self.title(data["title"])
        self.geometry("500x450")
        self.resizable(False, False)
        self.configure(fg_color="#0B0F19")
        
        self.transient(parent)
        self.grab_set()

        # Center relative to parent
        self.center_window(parent)
        
        frame = ctk.CTkFrame(self, fg_color="#111827", corner_radius=12, border_width=1, border_color="#1E293B")
        frame.pack(fill="both", expand=True, padx=14, pady=14)
        
        # Header Title
        lbl_title = ctk.CTkLabel(
            frame, 
            text=data["title"], 
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#38BDF8"
        )
        lbl_title.pack(pady=(16, 6), padx=16, anchor="w")
        
        # Summary Box
        lbl_summary = ctk.CTkLabel(
            frame,
            text=data["summary"],
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#CBD5E1",
            wraplength=440,
            justify="left"
        )
        lbl_summary.pack(padx=16, pady=(0, 10), anchor="w")
        
        # Points Container (Scrollable or Frame)
        points_box = ctk.CTkFrame(frame, fg_color="#0B0F19", corner_radius=8, border_width=1, border_color="#1E293B")
        points_box.pack(fill="both", expand=True, padx=16, pady=(0, 10))
        
        inner_pts = ctk.CTkScrollableFrame(points_box, fg_color="transparent", corner_radius=0)
        inner_pts.pack(fill="both", expand=True, padx=8, pady=8)
        
        for subtitle, text in data["points"]:
            p_frame = ctk.CTkFrame(inner_pts, fg_color="transparent")
            p_frame.pack(fill="x", pady=4)
            
            ctk.CTkLabel(
                p_frame,
                text=f"• {subtitle}",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color="#10B981"
            ).pack(anchor="w")
            
            ctk.CTkLabel(
                p_frame,
                text=text,
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color="#94A3B8",
                wraplength=410,
                justify="left"
            ).pack(anchor="w", padx=(12, 0), pady=(1, 2))
        
        # Tip Box
        tip_frame = ctk.CTkFrame(frame, fg_color="#1E293B", corner_radius=6)
        tip_frame.pack(fill="x", padx=16, pady=(0, 12))
        
        ctk.CTkLabel(
            tip_frame,
            text=data["tip"],
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#FDE68A",
            wraplength=440,
            justify="left"
        ).pack(padx=10, pady=6, anchor="w")
        
        # Close Button
        btn_close = ctk.CTkButton(
            frame, 
            text="Mengerti / Tutup", 
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#1E293B", 
            hover_color="#334155",
            text_color="#FFFFFF",
            height=30,
            width=130,
            corner_radius=6,
            command=self.destroy
        )
        btn_close.pack(pady=(0, 12))

    def center_window(self, parent):
        try:
            parent.update_idletasks()
            self.update_idletasks()
            w, h = 500, 450
            px, py = parent.winfo_x(), parent.winfo_y()
            pw, ph = parent.winfo_width(), parent.winfo_height()
            x = px + max(0, (pw - w) // 2)
            y = py + max(0, (ph - h) // 2)
            self.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass
