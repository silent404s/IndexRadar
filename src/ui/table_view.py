import tkinter as tk
from tkinter import ttk
import webbrowser
from urllib.parse import quote_plus

class ModernTableView(ctk_frame := tk.Frame):
    def __init__(self, parent, on_delete_callback=None, *args, **kwargs):
        super().__init__(parent, bg="#111827", *args, **kwargs)
        self.on_delete_callback = on_delete_callback
        
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
        self.tree.heading("PAGES", text="Jumlah Terindeks")
        self.tree.heading("DETAIL", text="Keterangan / Pesan")

        self.tree.column("NO", width=50, anchor="center", stretch=False)
        self.tree.column("DOMAIN", width=280, anchor="w")
        self.tree.column("STATUS", width=120, anchor="center", stretch=False)
        self.tree.column("PAGES", width=140, anchor="center", stretch=False)
        self.tree.column("DETAIL", width=380, anchor="w")

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
        self.tree.tag_configure("FAILED", foreground="#EF4444", font=("Segoe UI", 9, "bold"))

        # Context Menu
        self.context_menu = tk.Menu(self, tearoff=0, bg="#1E293B", fg="#F8FAFC", activebackground="#334155", activeforeground="#FFFFFF")
        self.context_menu.add_command(label="🌐  Buka site: di Google", command=self.open_google)
        self.context_menu.add_command(label="📋  Salin Nama Domain", command=self.copy_domain)
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

    def copy_domain(self):
        selected = self.tree.selection()
        if not selected:
            return
        item_vals = self.tree.item(selected[0], "values")
        if item_vals and len(item_vals) >= 2:
            domain = item_vals[1]
            self.clipboard_clear()
            self.clipboard_append(domain)

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
        item_id = selected[0]
        item_vals = self.tree.item(item_id, "values")
        self.tree.delete(item_id)
        if self.on_delete_callback and item_vals:
            self.on_delete_callback(item_vals)

    def insert_row(self, no, domain, status, count, detail):
        self.tree.insert("", tk.END, values=(no, domain, status, count, detail), tags=(status,))
        self.tree.yview_moveto(1.0)

    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
