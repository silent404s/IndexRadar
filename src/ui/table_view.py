import tkinter as tk
from tkinter import ttk
import webbrowser
from urllib.parse import quote_plus

class ModernTableView(tk.Frame):
    def __init__(
        self, 
        parent, 
        on_delete_callback=None, 
        on_retry_single_callback=None, 
        on_retry_failed_callback=None, 
        on_status_callback=None,
        *args, 
        **kwargs
    ):
        super().__init__(parent, bg="#111827", *args, **kwargs)
        self.on_delete_callback = on_delete_callback
        self.on_retry_single_callback = on_retry_single_callback
        self.on_retry_failed_callback = on_retry_failed_callback
        self.on_status_callback = on_status_callback
        
        # State animasi loading per baris
        self.checking_indices = set()
        self.spinner_frames = ["⏳ Memeriksa   ", "⏳ Memeriksa.  ", "⏳ Memeriksa.. ", "⏳ Memeriksa..."]
        self.spinner_idx = 0
        self.animating = False

        # Style ttk Treeview for dark mode
        self.setup_dark_style()
        
        # Build widgets
        columns = ("NO", "DOMAIN", "STATUS", "PAGES", "DETAIL")
        self.tree = ttk.Treeview(
            self, 
            columns=columns, 
            show="headings", 
            selectmode="browse",
            style="Dark.Treeview"
        )
        
        self.tree.heading("NO", text="#")
        self.tree.heading("DOMAIN", text="Domain / URL")
        self.tree.heading("STATUS", text="Status")
        self.tree.heading("PAGES", text="Jumlah Index")
        self.tree.heading("DETAIL", text="Keterangan / Pesan")

        # Konfigurasi lebar kolom agar proporsional dan tidak terpotong
        self.tree.column("NO", width=55, minwidth=48, anchor="center", stretch=False)
        self.tree.column("DOMAIN", width=280, minwidth=220, anchor="w", stretch=True)
        self.tree.column("STATUS", width=165, minwidth=145, anchor="center", stretch=False)
        self.tree.column("PAGES", width=120, minwidth=100, anchor="center", stretch=False)
        self.tree.column("DETAIL", width=380, minwidth=240, anchor="w", stretch=True)

        # Scrollbars
        scroll_y = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        scroll_x = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Tags styling
        self.tree.tag_configure("INDEX", foreground="#10B981", font=("Segoe UI", 9, "bold"))
        self.tree.tag_configure("UN-INDEX", foreground="#F59E0B", font=("Segoe UI", 9, "bold"))
        self.tree.tag_configure("UN-INDEXED", foreground="#F59E0B", font=("Segoe UI", 9, "bold"))
        self.tree.tag_configure("FAILED", foreground="#EF4444", font=("Segoe UI", 9, "bold"))
        self.tree.tag_configure("GAGAL", foreground="#EF4444", font=("Segoe UI", 9, "bold"))
        self.tree.tag_configure("QUEUED", foreground="#64748B", font=("Segoe UI", 9))
        self.tree.tag_configure("CHECKING", foreground="#38BDF8", font=("Segoe UI", 9, "bold"))

        # Context Menu
        self.context_menu = tk.Menu(self, tearoff=0, bg="#1E293B", fg="#F8FAFC", activebackground="#334155", activeforeground="#FFFFFF")
        self.context_menu.add_command(label="🌐  Buka site: di Google", command=self.open_google)
        self.context_menu.add_command(label="📋  Salin Nama Domain", command=self.copy_domain)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🔄  Cek Ulang Domain Ini", command=self.retry_single)
        self.context_menu.add_command(label="🔄  Cek Ulang Semua yang Gagal", command=self.retry_failed)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="❌  Hapus dari Tabel", command=self.delete_selected)

        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", lambda event: self.open_google())

    def setup_dark_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "Dark.Treeview",
            background="#0F172A",
            foreground="#E2E8F0",
            fieldbackground="#0F172A",
            rowheight=28,
            font=("Segoe UI", 9),
            borderwidth=0
        )
        style.configure(
            "Dark.Treeview.Heading",
            background="#1E293B",
            foreground="#94A3B8",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            padding=(6, 6)
        )
        style.map(
            "Dark.Treeview.Heading",
            background=[("active", "#334155")],
            foreground=[("active", "#F8FAFC")]
        )
        style.map(
            "Dark.Treeview",
            background=[("selected", "#2563EB")],
            foreground=[("selected", "#FFFFFF")]
        )

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def open_google(self):
        selected = self.tree.selection()
        if not selected:
            return
        item_vals = self.tree.item(selected[0], "values")
        if item_vals and len(item_vals) >= 2:
            domain = item_vals[1]
            url = f"https://www.google.com/search?q=site:{quote_plus(domain)}&hl=en"
            webbrowser.open_new_tab(url)
            if self.on_status_callback:
                self.on_status_callback(f"🌐 Membuka Google Search: site:{domain}")

    def copy_domain(self):
        selected = self.tree.selection()
        if not selected:
            return
        item_vals = self.tree.item(selected[0], "values")
        if item_vals and len(item_vals) >= 2:
            domain = item_vals[1]
            self.clipboard_clear()
            self.clipboard_append(domain)
            if self.on_status_callback:
                self.on_status_callback(f"📋 Domain tersalin ke clipboard: {domain}")

    def retry_single(self):
        selected = self.tree.selection()
        if not selected:
            return
        item_vals = self.tree.item(selected[0], "values")
        if item_vals and len(item_vals) >= 2:
            try:
                idx_no = int(item_vals[0])
            except ValueError:
                idx_no = 1
            domain = item_vals[1]
            if self.on_retry_single_callback:
                self.on_retry_single_callback(domain, idx_no)

    def retry_failed(self):
        if self.on_retry_failed_callback:
            self.on_retry_failed_callback()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
        item_id = selected[0]
        item_vals = self.tree.item(item_id, "values")
        try:
            idx_no = int(item_vals[0])
            self.checking_indices.discard(idx_no)
        except Exception:
            pass
        self.tree.delete(item_id)
        if self.on_delete_callback and item_vals:
            self.on_delete_callback(item_vals)
        if self.on_status_callback and item_vals and len(item_vals) >= 2:
            self.on_status_callback(f"🗑️ Domain dihapus dari tabel: {item_vals[1]}")

    def populate_initial_rows(self, domains):
        """
        Mengisi seluruh tabel sejak awal secara berurutan (1, 2, 3...)
        dengan status 'Menunggu' agar urutan baris tidak pernah berantakan.
        """
        self.clear()
        for idx, domain in enumerate(domains, start=1):
            iid = f"row_{idx}"
            self.tree.insert(
                "", 
                tk.END, 
                iid=iid, 
                values=(idx, domain, "⏳ Menunggu", "-", "Dalam antrean..."), 
                tags=("QUEUED",)
            )

    def set_row_checking(self, index_no, domain, detail="Sedang menganalisa SERP Google..."):
        """
        Mengaktifkan status animasi pengecekan pada baris tertentu.
        """
        self.checking_indices.add(index_no)
        iid = f"row_{index_no}"
        frame_text = self.spinner_frames[self.spinner_idx]
        if self.tree.exists(iid):
            self.tree.item(iid, values=(index_no, domain, frame_text, "-", detail), tags=("CHECKING",))
            self.tree.see(iid)
        else:
            self.tree.insert("", tk.END, iid=iid, values=(index_no, domain, frame_text, "-", detail), tags=("CHECKING",))

        self._start_animation()

    def update_row_detail(self, index_no, domain, status_text, count_text, detail_text):
        """
        Memperbarui status/keterangan baris yang sedang aktif (misal saat solving CAPTCHA).
        """
        iid = f"row_{index_no}"
        if self.tree.exists(iid):
            tags = self.tree.item(iid, "tags")
            self.tree.item(iid, values=(index_no, domain, status_text, count_text, detail_text), tags=tags)

    def set_row_result(self, index_no, domain, status, count, detail):
        """
        Menyimpan hasil akhir pemeriksaan pada baris dan menghentikan animasi loading baris tersebut.
        """
        self.checking_indices.discard(index_no)
        iid = f"row_{index_no}"
        tag = status if status in ("INDEX", "UN-INDEX", "UN-INDEXED", "FAILED") else "FAILED"
        if self.tree.exists(iid):
            self.tree.item(iid, values=(index_no, domain, status, count, detail), tags=(tag,))
        else:
            self.tree.insert("", tk.END, iid=iid, values=(index_no, domain, status, count, detail), tags=(tag,))

    def set_row_queued(self, index_no, domain):
        """
        Mengembalikan status baris ke status antrean (misal saat disiapkan untuk cek ulang).
        """
        self.checking_indices.discard(index_no)
        iid = f"row_{index_no}"
        if self.tree.exists(iid):
            self.tree.item(iid, values=(index_no, domain, "⏳ Menunggu", "-", "Menunggu antrean cek ulang..."), tags=("QUEUED",))

    def _start_animation(self):
        if not self.animating and self.checking_indices:
            self.animating = True
            self._animate_step()

    def _animate_step(self):
        if not self.checking_indices:
            self.animating = False
            return

        self.spinner_idx = (self.spinner_idx + 1) % len(self.spinner_frames)
        frame_text = self.spinner_frames[self.spinner_idx]

        for idx in list(self.checking_indices):
            iid = f"row_{idx}"
            if self.tree.exists(iid):
                vals = list(self.tree.item(iid, "values"))
                if len(vals) >= 5:
                    vals[2] = frame_text
                    self.tree.item(iid, values=vals, tags=("CHECKING",))

        self.after(300, self._animate_step)

    def insert_row(self, no, domain, status, count, detail):
        """Fallback untuk kompatibilitas."""
        self.set_row_result(no, domain, status, count, detail)

    def clear(self):
        self.checking_indices.clear()
        self.animating = False
        for item in self.tree.get_children():
            self.tree.delete(item)
