import os
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image

from ..config_manager import load_config, save_config
from ..update_checker import check_for_updates, CURRENT_VERSION
from ..captcha_service import get_2captcha_balance
from ..checker_engine import CheckerEngine, clean_domain
from ..export_utils import export_to_csv
from .table_view import ModernTableView
from .dialogs import AboutDialog, HelpInfoDialog

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("IndexRadar Pro - Bulk Google Index Checker")
        self.geometry("1100x820")
        self.minsize(960, 720)
        self.configure(fg_color="#0B0F19")

        # Load configurations
        self.config = load_config()

        # State storage
        self.results = {"INDEX": [], "UN-INDEX": [], "FAILED": []}
        self.data_by_index = {}
        self.all_data = []
        self.gui_queue = queue.Queue()
        self.is_checking = False

        # Init Engine
        self.engine = CheckerEngine(self.gui_queue)

        # Set App Icon
        self.set_app_icon()

        # Setup Protocol Close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Build Modern CustomTkinter UI
        self.build_ui()

        # Start GUI Queue Loop
        self.process_queue()

        # Auto Check Balance & Update
        self.check_initial_state()

    def set_app_icon(self):
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            ico_path = os.path.join(base_dir, "indexradar_icon.ico")
            png_path = os.path.join(base_dir, "indexradar_icon.png")

            if os.path.exists(ico_path):
                self.iconbitmap(default=ico_path)
            elif os.path.exists(png_path):
                img = ctk.CTkImage(light_image=Image.open(png_path), dark_image=Image.open(png_path), size=(32, 32))
        except Exception as e:
            print(f"[Icon] Warning: {e}")

    def check_initial_state(self):
        # Auto check 2Captcha balance
        api_key = self.entry_captcha.get().strip() if hasattr(self, 'entry_captcha') else self.config.get("captcha_api_key", "").strip()
        if api_key:
            threading.Thread(target=self.refresh_balance, daemon=True).start()
        else:
            self.lbl_balance.configure(text="Belum diisi", text_color="#94A3B8")

        # Otomatis periksa pembaruan aplikasi setiap kali buka aplikasi (seperti FlarePilot)
        update_url = self.config.get("update_url", "")
        check_for_updates(self, CURRENT_VERSION, update_url, silent=True)

    def refresh_balance(self):
        api_key = self.entry_captcha.get().strip() if hasattr(self, 'entry_captcha') else self.config.get("captcha_api_key", "").strip()
        if not api_key:
            self.gui_queue.put(("BALANCE", ("Belum diisi", "#94A3B8")))
            return

        # Simpan otomatis ke config saat cek saldo
        if self.config.get("captcha_api_key") != api_key:
            self.config["captcha_api_key"] = api_key
            save_config(self.config)

        self.gui_queue.put(("BALANCE", ("Memeriksa...", "#F59E0B")))
        bal = get_2captcha_balance(api_key)
        if bal is not None:
            self.gui_queue.put(("BALANCE", (f"${bal:.2f}", "#10B981")))
        else:
            self.gui_queue.put(("BALANCE", ("Key Invalid / Error", "#EF4444")))

    def build_ui(self):
        # 1. Top Navigation Bar / Header
        header = ctk.CTkFrame(self, fg_color="#111827", corner_radius=0, height=60)
        header.pack(fill="x", side="top")

        # Brand / Title
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left", padx=16, pady=10)

        lbl_logo = ctk.CTkLabel(
            title_box, 
            text="🎯 IndexRadar", 
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#10B981"
        )
        lbl_logo.pack(side="left")

        lbl_pro = ctk.CTkLabel(
            title_box, 
            text="PRO", 
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color="#1E293B",
            text_color="#38BDF8",
            corner_radius=6,
            padx=6,
            pady=2
        )
        lbl_pro.pack(side="left", padx=(6, 8))

        lbl_ver = ctk.CTkLabel(
            title_box, 
            text=f"v{CURRENT_VERSION}", 
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#64748B"
        )
        lbl_ver.pack(side="left")

        # Header Right Controls
        header_right = ctk.CTkFrame(header, fg_color="transparent")
        header_right.pack(side="right", padx=16, pady=10)

        # Update button (seperti FlarePilot)
        btn_update = ctk.CTkButton(
            header_right,
            text="⚡ Cek Update",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#059669",
            hover_color="#047857",
            text_color="#FFFFFF",
            height=30,
            corner_radius=8,
            command=self.check_updates_manual
        )
        btn_update.pack(side="left", padx=(0, 8))

        # About button
        btn_about = ctk.CTkButton(
            header_right,
            text="ℹ️",
            width=32,
            height=30,
            corner_radius=8,
            fg_color="#1E293B",
            hover_color="#0F172A",
            border_width=1,
            border_color="#334155",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            command=lambda: AboutDialog(self, CURRENT_VERSION)
        )
        btn_about.pack(side="left")

        # 2. Main Content Body
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=10)

        # Top Section: Input Domains & Proxy Cards
        inputs_frame = ctk.CTkFrame(body, fg_color="transparent")
        inputs_frame.pack(fill="x", pady=(0, 10))

        # Domains Card (Left)
        card_domains = ctk.CTkFrame(inputs_frame, fg_color="#111827", corner_radius=10, border_width=1, border_color="#1E293B")
        card_domains.pack(side="left", fill="both", expand=True, padx=(0, 6))

        domain_header = ctk.CTkFrame(card_domains, fg_color="transparent")
        domain_header.pack(fill="x", padx=12, pady=(8, 4))

        ctk.CTkLabel(
            domain_header, 
            text="📋 Daftar Domain Target (1 per baris)", 
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#E2E8F0"
        ).pack(side="left")

        btn_clear_domain = ctk.CTkButton(
            domain_header,
            text="🧹 Bersihkan",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color="#1E293B",
            hover_color="#0F172A",
            border_width=1,
            border_color="#334155",
            text_color="#FFFFFF",
            height=24,
            width=80,
            corner_radius=6,
            command=lambda: self.txt_domains.delete("1.0", "end")
        )
        btn_clear_domain.pack(side="right")

        btn_import = ctk.CTkButton(
            domain_header,
            text="📂 Import File (.txt / .csv)",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color="#1E293B",
            hover_color="#0F172A",
            border_width=1,
            border_color="#334155",
            text_color="#FFFFFF",
            height=24,
            width=140,
            corner_radius=6,
            command=self.import_file
        )
        btn_import.pack(side="right", padx=(0, 6))

        self.txt_domains = ctk.CTkTextbox(
            card_domains, 
            height=110, 
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#0B0F19",
            text_color="#F8FAFC",
            border_width=1,
            border_color="#1E293B",
            corner_radius=8
        )
        self.txt_domains.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        # Proxy & Options Card (Right)
        card_proxy = ctk.CTkFrame(inputs_frame, fg_color="#111827", corner_radius=10, border_width=1, border_color="#1E293B")
        card_proxy.pack(side="right", fill="both", expand=True, padx=(6, 0))

        proxy_header = ctk.CTkFrame(card_proxy, fg_color="transparent")
        proxy_header.pack(fill="x", padx=12, pady=(8, 4))

        ctk.CTkLabel(
            proxy_header, 
            text="🌐 Proxy List (Opsional - format ip:port)", 
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#E2E8F0"
        ).pack(side="left")

        btn_proxy_help = ctk.CTkButton(
            proxy_header,
            text="?",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#1E293B",
            hover_color="#334155",
            text_color="#38BDF8",
            border_width=1,
            border_color="#334155",
            width=20,
            height=20,
            corner_radius=10,
            command=lambda: self.show_help_dialog("proxy")
        )
        btn_proxy_help.pack(side="left", padx=(6, 0))

        btn_clear_proxy = ctk.CTkButton(
            proxy_header,
            text="🧹 Bersihkan",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color="#1E293B",
            hover_color="#0F172A",
            border_width=1,
            border_color="#334155",
            text_color="#FFFFFF",
            height=24,
            width=80,
            corner_radius=6,
            command=lambda: self.txt_proxy.delete("1.0", "end")
        )
        btn_clear_proxy.pack(side="right")

        self.txt_proxy = ctk.CTkTextbox(
            card_proxy, 
            height=110, 
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#0B0F19",
            text_color="#F8FAFC",
            border_width=1,
            border_color="#1E293B",
            corner_radius=8
        )
        self.txt_proxy.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        # 2.5 Dedicated 2Captcha Configuration Card (Tampilan Utama)
        card_captcha = ctk.CTkFrame(body, fg_color="#111827", corner_radius=10, border_width=1, border_color="#1E293B")
        card_captcha.pack(fill="x", pady=(0, 10))

        captcha_inner = ctk.CTkFrame(card_captcha, fg_color="transparent")
        captcha_inner.pack(fill="x", padx=14, pady=8)

        # Toggle Aktifkan 2Captcha
        self.var_captcha = ctk.BooleanVar(value=self.config.get("use_captcha", True))
        chk_use_captcha = ctk.CTkCheckBox(
            captcha_inner,
            text="Aktifkan Auto-Solve CAPTCHA (2Captcha.com)",
            variable=self.var_captcha,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            text_color="#F8FAFC",
            command=self.on_toggle_captcha
        )
        chk_use_captcha.pack(side="left", padx=(0, 15))

        # API Key Label & Input
        ctk.CTkLabel(
            captcha_inner, 
            text="API Key:", 
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#94A3B8"
        ).pack(side="left", padx=(0, 6))

        self.entry_captcha = ctk.CTkEntry(
            captcha_inner,
            placeholder_text="Masukkan 2Captcha API Key...",
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#0B0F19",
            border_color="#334155",
            text_color="#F8FAFC",
            height=30,
            width=320,
            corner_radius=6
        )
        self.entry_captcha.insert(0, self.config.get("captcha_api_key", ""))
        self.entry_captcha.pack(side="left", padx=(0, 10))
        self.entry_captcha.bind("<FocusOut>", lambda e: self.on_captcha_key_changed())

        # Tombol Cek Saldo
        btn_check_bal = ctk.CTkButton(
            captcha_inner,
            text="💰 Cek Saldo",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#059669",
            hover_color="#047857",
            text_color="#FFFFFF",
            height=30,
            width=100,
            corner_radius=6,
            command=lambda: threading.Thread(target=self.refresh_balance, daemon=True).start()
        )
        btn_check_bal.pack(side="left", padx=(0, 12))

        # Label Saldo Live
        lbl_bal_title = ctk.CTkLabel(
            captcha_inner,
            text="Saldo:",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#94A3B8"
        )
        lbl_bal_title.pack(side="left", padx=(0, 4))

        self.lbl_balance = ctk.CTkLabel(
            captcha_inner,
            text="Memuat...",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#10B981"
        )
        self.lbl_balance.pack(side="left")

        # 3. Action & Controls Bar
        controls_bar = ctk.CTkFrame(body, fg_color="#111827", corner_radius=10, border_width=1, border_color="#1E293B")
        controls_bar.pack(fill="x", pady=(0, 10), ipady=4)

        ctrl_inner = ctk.CTkFrame(controls_bar, fg_color="transparent")
        ctrl_inner.pack(fill="x", padx=14, pady=8)

        # Settings: Threads
        ctk.CTkLabel(ctrl_inner, text="Threads:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#94A3B8").pack(side="left", padx=(0, 3))
        btn_threads_help = ctk.CTkButton(
            ctrl_inner,
            text="?",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color="#1E293B",
            hover_color="#334155",
            text_color="#38BDF8",
            border_width=1,
            border_color="#334155",
            width=18,
            height=18,
            corner_radius=9,
            command=lambda: self.show_help_dialog("threads")
        )
        btn_threads_help.pack(side="left", padx=(0, 6))

        self.opt_threads = ctk.CTkOptionMenu(
            ctrl_inner,
            values=["1", "2", "3", "4", "5", "6", "8"],
            width=65,
            height=28,
            corner_radius=6,
            fg_color="#1E293B",
            button_color="#334155",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=11)
        )
        self.opt_threads.set(str(self.config.get("threads", 2)))
        self.opt_threads.pack(side="left", padx=(0, 15))

        # Settings: Delay
        ctk.CTkLabel(ctrl_inner, text="Jeda (detik):", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#94A3B8").pack(side="left", padx=(0, 3))
        btn_delay_help = ctk.CTkButton(
            ctrl_inner,
            text="?",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color="#1E293B",
            hover_color="#334155",
            text_color="#38BDF8",
            border_width=1,
            border_color="#334155",
            width=18,
            height=18,
            corner_radius=9,
            command=lambda: self.show_help_dialog("delay")
        )
        btn_delay_help.pack(side="left", padx=(0, 6))

        self.opt_delay = ctk.CTkOptionMenu(
            ctrl_inner,
            values=["1.0", "1.5", "2.0", "3.0", "5.0", "8.0", "10.0"],
            width=75,
            height=28,
            corner_radius=6,
            fg_color="#1E293B",
            button_color="#334155",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=11)
        )
        self.opt_delay.set(str(self.config.get("delay", 2.0)))
        self.opt_delay.pack(side="left", padx=(0, 20))

        # Start & Stop Buttons
        self.btn_start = ctk.CTkButton(
            ctrl_inner,
            text="▶  Mulai Cek",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            text_color="#FFFFFF",
            height=32,
            width=120,
            corner_radius=8,
            command=self.start_checking
        )
        self.btn_start.pack(side="left", padx=(0, 8))

        self.btn_stop = ctk.CTkButton(
            ctrl_inner,
            text="⏹  Berhenti",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#450A0A",
            hover_color="#B91C1C",
            text_color="#FFFFFF",
            text_color_disabled="#FFFFFF",
            border_width=1,
            border_color="#7F1D1D",
            height=32,
            width=100,
            corner_radius=8,
            state="disabled",
            command=self.stop_checking
        )
        self.btn_stop.pack(side="left", padx=(0, 8))

        # Tombol Cek Ulang Khusus Domain yang Gagal
        self.btn_retry_failed = ctk.CTkButton(
            ctrl_inner,
            text="🔄  Cek Ulang Gagal",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#78350F",
            hover_color="#92400E",
            text_color="#FFFFFF",
            text_color_disabled="#64748B",
            border_width=1,
            border_color="#B45309",
            height=32,
            width=140,
            corner_radius=8,
            state="disabled",
            command=self.retry_failed
        )
        self.btn_retry_failed.pack(side="left", padx=(0, 10))

        # Reset & Export Buttons
        btn_clear = ctk.CTkButton(
            ctrl_inner,
            text="🗑  Reset",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#1E293B",
            hover_color="#0F172A",
            border_width=1,
            border_color="#334155",
            text_color="#FFFFFF",
            height=32,
            width=80,
            corner_radius=8,
            command=self.clear_table
        )
        btn_clear.pack(side="left", padx=(0, 8))

        btn_export = ctk.CTkButton(
            ctrl_inner,
            text="💾  Export CSV",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#0284C7",
            hover_color="#0369A1",
            text_color="#FFFFFF",
            height=32,
            width=110,
            corner_radius=8,
            command=self.export_csv
        )
        btn_export.pack(side="right")

        # 4. Metrics Dashboard & Progress Bar
        metrics_card = ctk.CTkFrame(body, fg_color="#111827", corner_radius=10, border_width=1, border_color="#1E293B")
        metrics_card.pack(fill="x", pady=(0, 10), padx=0)

        metrics_inner = ctk.CTkFrame(metrics_card, fg_color="transparent")
        metrics_inner.pack(fill="x", padx=12, pady=8)

        # Counter Badges
        self.badge_total = self.create_badge(metrics_inner, "TOTAL", "0", "#64748B")
        self.badge_total.pack(side="left", padx=(0, 8))

        self.badge_indexed = self.create_badge(metrics_inner, "INDEX", "0", "#10B981")
        self.badge_indexed.pack(side="left", padx=(0, 8))

        self.badge_unindexed = self.create_badge(metrics_inner, "UN-INDEX", "0", "#F59E0B")
        self.badge_unindexed.pack(side="left", padx=(0, 8))

        self.badge_failed = self.create_badge(metrics_inner, "GAGAL", "0", "#EF4444")
        self.badge_failed.pack(side="left", padx=(0, 15))

        # Progress bar & Text
        self.lbl_progress = ctk.CTkLabel(
            metrics_inner,
            text="0 / 0 (0%)",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#94A3B8"
        )
        self.lbl_progress.pack(side="right")

        self.progressbar = ctk.CTkProgressBar(
            metrics_inner,
            height=10,
            width=220,
            corner_radius=5,
            progress_color="#10B981",
            fg_color="#1E293B"
        )
        self.progressbar.set(0)
        self.progressbar.pack(side="right", padx=(0, 12))

        # 5. Table View Container
        table_container = ctk.CTkFrame(body, fg_color="#111827", corner_radius=10, border_width=1, border_color="#1E293B")
        table_container.pack(fill="both", expand=True, pady=(0, 10))

        self.table_view = ModernTableView(
            table_container, 
            on_delete_callback=self.on_row_deleted,
            on_retry_single_callback=self.retry_single_domain,
            on_retry_failed_callback=self.retry_failed,
            on_status_callback=lambda msg: self.lbl_status.configure(text=msg, text_color="#38BDF8")
        )
        self.table_view.pack(fill="both", expand=True, padx=8, pady=8)

        # 6. Bottom Quick-Copy Toolbar & Status Bar
        bottom_bar = ctk.CTkFrame(self, fg_color="#111827", corner_radius=0, height=45)
        bottom_bar.pack(fill="x", side="bottom")

        bottom_inner = ctk.CTkFrame(bottom_bar, fg_color="transparent")
        bottom_inner.pack(fill="x", padx=16, pady=6)

        ctk.CTkLabel(
            bottom_inner, 
            text="Salin Cepat:", 
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#94A3B8"
        ).pack(side="left", padx=(0, 8))

        btn_copy_index = ctk.CTkButton(
            bottom_inner,
            text="📋 Salin INDEX",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color="#065F46",
            hover_color="#047857",
            border_width=1,
            border_color="#10B981",
            text_color="#FFFFFF",
            height=28,
            width=110,
            corner_radius=6,
            command=lambda: self.copy_by_status("INDEX")
        )
        btn_copy_index.pack(side="left", padx=(0, 6))

        btn_copy_unindex = ctk.CTkButton(
            bottom_inner,
            text="📋 Salin UN-INDEX",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color="#92400E",
            hover_color="#B45309",
            border_width=1,
            border_color="#F59E0B",
            text_color="#FFFFFF",
            height=28,
            width=125,
            corner_radius=6,
            command=lambda: self.copy_by_status("UN-INDEX")
        )
        btn_copy_unindex.pack(side="left", padx=(0, 6))

        btn_copy_failed = ctk.CTkButton(
            bottom_inner,
            text="📋 Salin GAGAL",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color="#991B1B",
            hover_color="#DC2626",
            border_width=1,
            border_color="#EF4444",
            text_color="#FFFFFF",
            height=28,
            width=110,
            corner_radius=6,
            command=lambda: self.copy_by_status("FAILED")
        )
        btn_copy_failed.pack(side="left", padx=(0, 15))

        # Status text
        self.lbl_status = ctk.CTkLabel(
            bottom_inner,
            text="Siap. Masukkan daftar domain lalu klik Mulai Cek.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#94A3B8"
        )
        self.lbl_status.pack(side="left", fill="x", expand=True)

    def create_badge(self, parent, title, value, color):
        frame = ctk.CTkFrame(parent, fg_color="#1E293B", corner_radius=6)
        lbl_t = ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"), text_color="#94A3B8")
        lbl_t.pack(side="left", padx=(8, 4), pady=3)
        lbl_v = ctk.CTkLabel(frame, text=value, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=color)
        lbl_v.pack(side="left", padx=(0, 8), pady=3)
        frame.value_label = lbl_v
        return frame

    def on_toggle_captcha(self):
        val = self.var_captcha.get()
        self.config["use_captcha"] = val
        save_config(self.config)

    def on_captcha_key_changed(self):
        key = self.entry_captcha.get().strip()
        self.config["captcha_api_key"] = key
        save_config(self.config)

    def show_help_dialog(self, topic):
        HelpInfoDialog(self, topic=topic)

    def check_updates_manual(self):
        update_url = self.config.get("update_url", "")
        # Otomatis mencari endpoint update seperti cara kerja FlarePilot
        check_for_updates(self, CURRENT_VERSION, update_url, silent=False)

    def import_file(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Text & CSV Files", "*.txt *.csv"), ("All Files", "*.*")]
        )
        if not filepath:
            return
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                domains = []
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    if filepath.endswith('.csv') and ',' in line:
                        col = line.split(',')[0].strip(' "\'')
                    else:
                        col = line
                    cleaned = clean_domain(col)
                    if cleaned:
                        domains.append(cleaned)

                seen = set()
                unique_domains = [d for d in domains if not (d.lower() in seen or seen.add(d.lower()))]

                self.txt_domains.delete("1.0", "end")
                self.txt_domains.insert("end", "\n".join(unique_domains))
                self.lbl_status.configure(text=f"✅ Berhasil memuat {len(unique_domains)} domain unik dari file.", text_color="#10B981")
        except Exception as e:
            self.lbl_status.configure(text=f"❌ Gagal membaca file: {e}", text_color="#EF4444")

    def export_csv(self):
        if not self.all_data:
            self.lbl_status.configure(text="⚠️ Belum ada data untuk diekspor!", text_color="#F59E0B")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        success, err = export_to_csv(filepath, self.all_data)
        if success:
            self.lbl_status.configure(text=f"✅ Data berhasil disimpan ke: {os.path.basename(filepath)}", text_color="#10B981")
        else:
            self.lbl_status.configure(text=f"❌ Gagal mengekspor file: {err}", text_color="#EF4444")

    def copy_by_status(self, status):
        domains = self.results.get(status, [])
        if not domains:
            self.lbl_status.configure(text=f"ℹ️ Tidak ada data domain dengan status {status}.", text_color="#94A3B8")
            return
        self.clipboard_clear()
        self.clipboard_append("\n".join(domains))
        self.lbl_status.configure(text=f"✅ Berhasil menyalin {len(domains)} domain ({status}) ke clipboard!", text_color="#10B981")

    def update_domain_result(self, idx_no, domain, status, count, detail):
        for cat in ("INDEX", "UN-INDEX", "FAILED"):
            if domain in self.results[cat]:
                self.results[cat].remove(domain)
        if status in self.results:
            self.results[status].append(domain)
        self.data_by_index[idx_no] = [idx_no, domain, status, count, detail]
        self.all_data = [self.data_by_index[k] for k in sorted(self.data_by_index.keys())]

    def on_row_deleted(self, values):
        try:
            idx_no = int(values[0])
        except Exception:
            idx_no = None
        domain = values[1]
        status = values[2]
        if status in self.results and domain in self.results[status]:
            self.results[status].remove(domain)
        if idx_no is not None and idx_no in self.data_by_index:
            del self.data_by_index[idx_no]
        self.all_data = [self.data_by_index[k] for k in sorted(self.data_by_index.keys())]
        self.update_badges(len(self.all_data))
        failed_count = len(self.results["FAILED"])
        if hasattr(self, 'btn_retry_failed'):
            if failed_count > 0:
                self.btn_retry_failed.configure(state="normal", fg_color="#B45309", text=f"🔄  Cek Ulang Gagal ({failed_count})")
            else:
                self.btn_retry_failed.configure(state="disabled", fg_color="#78350F", text="🔄  Cek Ulang Gagal")

    def clear_table(self):
        if self.is_checking:
            self.lbl_status.configure(text="⚠️ Hentikan pengecekan terlebih dahulu sebelum mereset tabel!", text_color="#F59E0B")
            return
        self.table_view.clear()
        self.results = {"INDEX": [], "UN-INDEX": [], "FAILED": []}
        self.data_by_index = {}
        self.all_data = []
        self.update_badges(0)
        self.progressbar.set(0)
        self.lbl_progress.configure(text="0 / 0 (0%)")
        self.lbl_status.configure(text="Tabel berhasil direset.", text_color="#94A3B8")
        if hasattr(self, 'btn_retry_failed'):
            self.btn_retry_failed.configure(state="disabled", fg_color="#78350F", text="🔄  Cek Ulang Gagal")

    def update_badges(self, total_target):
        self.badge_total.value_label.configure(text=str(total_target))
        self.badge_indexed.value_label.configure(text=str(len(self.results["INDEX"])))
        self.badge_unindexed.value_label.configure(text=str(len(self.results["UN-INDEX"])))
        self.badge_failed.value_label.configure(text=str(len(self.results["FAILED"])))

    def start_checking(self):
        if self.is_checking:
            return

        raw_text = self.txt_domains.get("1.0", "end")
        lines = [line.strip() for line in raw_text.split("\n") if line.strip()]

        cleaned_domains = []
        for line in lines:
            c = clean_domain(line)
            if c:
                cleaned_domains.append(c)

        seen = set()
        domains = [d for d in cleaned_domains if not (d.lower() in seen or seen.add(d.lower()))]

        if not domains:
            self.lbl_status.configure(text="⚠️ Daftar domain masih kosong! Masukkan domain terlebih dahulu.", text_color="#EF4444")
            return

        raw_proxies = self.txt_proxy.get("1.0", "end")
        proxies_list = [p.strip() for p in raw_proxies.split("\n") if p.strip()]

        use_captcha = self.var_captcha.get()
        api_key_captcha = self.entry_captcha.get().strip()

        # Simpan config terbaru
        self.config["use_captcha"] = use_captcha
        self.config["captcha_api_key"] = api_key_captcha
        save_config(self.config)

        if use_captcha and not api_key_captcha:
            resp = messagebox.askyesno(
                "2Captcha Belum Diisi", 
                "Fitur Auto-Solve CAPTCHA aktif tetapi API Key di kolom 2Captcha masih kosong.\n\nApakah Anda ingin melanjutkan pengecekan tanpa 2Captcha?"
            )
            if not resp:
                self.entry_captcha.focus()
                return
            use_captcha = False

        # Reset & Pre-populasi tabel dari awal berurutan 1, 2, 3...
        self.clear_table()
        self.total_tasks = len(domains)
        self.table_view.populate_initial_rows(domains)

        self.data_by_index = {idx: [idx, d, "QUEUED", "-", "Dalam antrean..."] for idx, d in enumerate(domains, start=1)}
        self.all_data = [self.data_by_index[k] for k in sorted(self.data_by_index.keys())]

        self.update_badges(self.total_tasks)
        self.progressbar.set(0)
        self.lbl_progress.configure(text=f"0 / {self.total_tasks} (0%)")

        # Update State
        self.is_checking = True
        self.btn_start.configure(state="disabled")
        self.btn_retry_failed.configure(state="disabled", fg_color="#78350F", text="🔄  Cek Ulang Gagal")
        self.btn_stop.configure(state="normal", fg_color="#DC2626")
        self.opt_threads.configure(state="disabled")
        self.opt_delay.configure(state="disabled")

        num_threads = int(self.opt_threads.get())
        base_delay = float(self.opt_delay.get())

        self.lbl_status.configure(text="Menyiapkan browser headless Chromium...")

        # Supervisor thread
        threading.Thread(
            target=self.engine.run_supervisor,
            args=(domains, proxies_list, num_threads, base_delay, use_captcha, api_key_captcha, False),
            daemon=True
        ).start()

    def retry_failed(self):
        """
        Melakukan pencarian/pengecekan index ulang khusus untuk domain yang berstatus GAGAL (FAILED).
        """
        if self.is_checking:
            self.lbl_status.configure(text="⚠️ Proses masih berjalan. Tunggu atau klik Berhenti terlebih dahulu.", text_color="#F59E0B")
            return

        failed_tasks = [
            (row[0], row[1]) for row in self.all_data if row[2] == "FAILED"
        ]
        if not failed_tasks:
            self.lbl_status.configure(text="ℹ️ Tidak ada domain yang berstatus GAGAL untuk dicek ulang.", text_color="#94A3B8")
            return

        use_captcha = self.var_captcha.get()
        api_key_captcha = self.entry_captcha.get().strip()
        raw_proxies = self.txt_proxy.get("1.0", "end")
        proxies_list = [p.strip() for p in raw_proxies.split("\n") if p.strip()]

        num_threads = int(self.opt_threads.get())
        base_delay = float(self.opt_delay.get())

        for idx, domain in failed_tasks:
            self.table_view.set_row_queued(idx, domain)
            if domain in self.results["FAILED"]:
                self.results["FAILED"].remove(domain)
            self.data_by_index[idx] = [idx, domain, "QUEUED", "-", "Menunggu antrean cek ulang..."]

        self.all_data = [self.data_by_index[k] for k in sorted(self.data_by_index.keys())]
        self.update_badges(len(self.data_by_index))

        self.is_checking = True
        self.btn_start.configure(state="disabled")
        self.btn_retry_failed.configure(state="disabled")
        self.btn_stop.configure(state="normal", fg_color="#DC2626")
        self.opt_threads.configure(state="disabled")
        self.opt_delay.configure(state="disabled")

        self.lbl_status.configure(text=f"Menjalankan cek ulang untuk {len(failed_tasks)} domain yang gagal...")

        threading.Thread(
            target=self.engine.run_supervisor,
            args=(failed_tasks, proxies_list, num_threads, base_delay, use_captcha, api_key_captcha, True),
            daemon=True
        ).start()

    def retry_single_domain(self, domain, index_no):
        """
        Cek ulang hanya satu domain yang dipilih dari menu klik kanan.
        """
        if self.is_checking:
            self.lbl_status.configure(text="⚠️ Proses masih berjalan. Tunggu atau klik Berhenti terlebih dahulu.", text_color="#F59E0B")
            return

        use_captcha = self.var_captcha.get()
        api_key_captcha = self.entry_captcha.get().strip()
        raw_proxies = self.txt_proxy.get("1.0", "end")
        proxies_list = [p.strip() for p in raw_proxies.split("\n") if p.strip()]

        num_threads = 1
        base_delay = float(self.opt_delay.get())

        self.table_view.set_row_queued(index_no, domain)
        for cat in ("INDEX", "UN-INDEX", "FAILED"):
            if domain in self.results[cat]:
                self.results[cat].remove(domain)
        self.data_by_index[index_no] = [index_no, domain, "QUEUED", "-", "Menunggu antrean cek ulang..."]
        self.all_data = [self.data_by_index[k] for k in sorted(self.data_by_index.keys())]
        self.update_badges(len(self.data_by_index))

        self.is_checking = True
        self.btn_start.configure(state="disabled")
        self.btn_retry_failed.configure(state="disabled")
        self.btn_stop.configure(state="normal", fg_color="#DC2626")

        self.lbl_status.configure(text=f"Cek ulang #{index_no} ({domain})...")

        threading.Thread(
            target=self.engine.run_supervisor,
            args=([(index_no, domain)], proxies_list, num_threads, base_delay, use_captcha, api_key_captcha, True),
            daemon=True
        ).start()

    def stop_checking(self):
        if not self.is_checking:
            return
        self.lbl_status.configure(text="Sedang menghentikan semua browser worker...")
        self.btn_stop.configure(state="disabled")
        threading.Thread(target=self.engine.stop, daemon=True).start()

    def process_queue(self):
        try:
            while True:
                msg_type, data = self.gui_queue.get_nowait()

                if msg_type == "ROW_START":
                    idx_no, domain = data
                    self.table_view.set_row_checking(idx_no, domain)

                elif msg_type == "ROW_UPDATE":
                    idx_no, domain, st, cnt, dt = data
                    self.table_view.update_row_detail(idx_no, domain, st, cnt, dt)

                elif msg_type == "RESULT":
                    idx_no, domain, status, count, detail = data
                    self.update_domain_result(idx_no, domain, status, count, detail)
                    self.table_view.set_row_result(idx_no, domain, status, count, detail)

                    done = sum(1 for row in self.data_by_index.values() if row[2] in ("INDEX", "UN-INDEX", "FAILED"))
                    tot = getattr(self, "total_tasks", len(self.data_by_index))
                    self.update_badges(tot)
                    frac = done / tot if tot > 0 else 0
                    self.progressbar.set(frac)
                    self.lbl_progress.configure(text=f"{done} / {tot} ({int(frac*100)}%)")

                elif msg_type == "STATUS":
                    self.lbl_status.configure(text=data)

                elif msg_type == "BALANCE":
                    text, color = data
                    self.lbl_balance.configure(text=text, text_color=color)

                elif msg_type == "LOG_ERROR":
                    print(f"[-] {data}")

                elif msg_type == "ALL_DONE":
                    self.is_checking = False
                    self.btn_start.configure(state="normal")
                    self.btn_stop.configure(state="disabled", fg_color="#450A0A")
                    self.opt_threads.configure(state="normal")
                    self.opt_delay.configure(state="normal")

                    # Perbarui status tombol Cek Ulang Gagal
                    failed_count = len(self.results["FAILED"])
                    if failed_count > 0:
                        self.btn_retry_failed.configure(state="normal", fg_color="#B45309", text=f"🔄  Cek Ulang Gagal ({failed_count})")
                    else:
                        self.btn_retry_failed.configure(state="disabled", fg_color="#78350F", text="🔄  Cek Ulang Gagal")

                    threading.Thread(target=self.refresh_balance, daemon=True).start()

                    if self.engine.stop_requested:
                        self.lbl_status.configure(text="⏹ Pengecekan dihentikan oleh pengguna.", text_color="#F59E0B")
                    else:
                        self.lbl_status.configure(
                            text=f"✅ Pengecekan selesai! {len(self.all_data)} domain telah diproses • INDEX: {len(self.results['INDEX'])} | UN-INDEX: {len(self.results['UN-INDEX'])} | GAGAL: {len(self.results['FAILED'])}",
                            text_color="#10B981"
                        )

        except queue.Empty:
            pass

        self.after(80, self.process_queue)

    def on_closing(self):
        self.is_checking = False
        self.engine.stop()
        self.destroy()
