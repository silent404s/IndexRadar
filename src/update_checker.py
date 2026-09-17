import threading
import webbrowser
import requests
import customtkinter as ctk
from tkinter import messagebox

CURRENT_VERSION = "1.0.0"

def parse_version(version_str):
    """
    Mengonversi string versi seperti '1.0.0' atau 'v1.0.1' menjadi tuple integer untuk perbandingan numerik.
    """
    cleaned = str(version_str).strip().lstrip('vV')
    parts = []
    for p in cleaned.split('.'):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    return tuple(parts)

def fetch_remote_version_info(update_url, timeout=10):
    """
    Mengambil metadata versi terbaru dari URL JSON GitHub.
    """
    headers = {
        'User-Agent': 'IndexRadarPro-UpdateChecker/1.0'
    }
    
    response = requests.get(update_url, headers=headers, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    
    if isinstance(data, list) and len(data) > 0:
        data = data[0]
        
    version = data.get("version") or data.get("tag_name") or "0.0.0"
    release_notes = data.get("release_notes") or data.get("body") or "Tidak ada catatan rilis."
    html_url = data.get("html_url") or data.get("url") or ""
    
    download_url = data.get("download_url") or ""
    if not download_url and "assets" in data and isinstance(data["assets"], list):
        for asset in data["assets"]:
            if asset.get("name", "").endswith(".exe"):
                download_url = asset.get("browser_download_url", "")
                break
    if not download_url:
        download_url = html_url
        
    return {
        "version": version.strip().lstrip('vV'),
        "download_url": download_url,
        "release_notes": release_notes,
        "html_url": html_url
    }

class UpdateDialog(ctk.CTkToplevel):
    def __init__(self, parent, current_ver, remote_info):
        super().__init__(parent)
        self.title("⚡ Pembaruan Tersedia - IndexRadar Pro")
        self.geometry("520x470")
        self.resizable(False, False)
        self.configure(fg_color="#0B0F19")
        
        self.remote_info = remote_info
        
        self.transient(parent)
        self.grab_set()
        
        # Center dialog relative to parent window
        self.center_window(parent)
        
        # Main Container
        frame = ctk.CTkFrame(self, corner_radius=12, fg_color="#111827", border_width=1, border_color="#1E293B")
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header
        lbl_header = ctk.CTkLabel(
            frame, 
            text="🚀 Pembaruan Aplikasi Tersedia!", 
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#10B981"
        )
        lbl_header.pack(pady=(18, 5))
        
        # Version Badges Frame
        ver_frame = ctk.CTkFrame(frame, fg_color="#1E293B", corner_radius=8)
        ver_frame.pack(pady=8, padx=20, fill="x")
        
        lbl_curr = ctk.CTkLabel(
            ver_frame, 
            text=f"Versi Anda: v{current_ver}", 
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#9CA3AF"
        )
        lbl_curr.pack(side="left", padx=15, pady=8)
        
        lbl_new = ctk.CTkLabel(
            ver_frame, 
            text=f"Versi Terbaru: v{remote_info['version']}", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#38BDF8"
        )
        lbl_new.pack(side="right", padx=15, pady=8)
        
        # Release Notes Label
        lbl_notes_title = ctk.CTkLabel(
            frame, 
            text="📋 Catatan Rilis (Release Notes):", 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#E2E8F0",
            anchor="w"
        )
        lbl_notes_title.pack(fill="x", padx=18, pady=(10, 4))
        
        # Release Notes Text Box
        txt_notes = ctk.CTkTextbox(
            frame, 
            font=ctk.CTkFont(family="Segoe UI", size=11), 
            wrap="word",
            fg_color="#0B0F19",
            text_color="#CBD5E1",
            border_color="#334155",
            border_width=1,
            corner_radius=8
        )
        txt_notes.pack(fill="both", expand=True, padx=18, pady=(0, 15))
        txt_notes.insert("1.0", remote_info.get("release_notes", "- Tidak ada catatan rilis."))
        txt_notes.configure(state="disabled")
        
        # Action Buttons
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=18, pady=(0, 15))
        
        btn_download = ctk.CTkButton(
            btn_frame, 
            text="🚀 Unduh & Update Setup (.exe)", 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#10B981", 
            hover_color="#059669",
            height=36,
            corner_radius=8,
            command=self.open_download
        )
        btn_download.pack(side="left", fill="x", expand=True, padx=(0, 6))
        
        btn_close = ctk.CTkButton(
            btn_frame, 
            text="Tutup", 
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="#334155", 
            hover_color="#475569",
            height=36,
            width=90,
            corner_radius=8,
            command=self.destroy
        )
        btn_close.pack(side="right")

    def center_window(self, parent):
        try:
            parent.update_idletasks()
            self.update_idletasks()
            w, h = 520, 470
            px, py = parent.winfo_x(), parent.winfo_y()
            pw, ph = parent.winfo_width(), parent.winfo_height()
            x = px + max(0, (pw - w) // 2)
            y = py + max(0, (ph - h) // 2)
            self.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass

    def open_download(self):
        url = self.remote_info.get("download_url") or self.remote_info.get("html_url")
        if url:
            webbrowser.open(url)
        self.destroy()

def check_for_updates(parent, current_version=CURRENT_VERSION, update_url="", silent=False):
    """
    Melakukan pemeriksaan pembaruan di background thread secara non-blocking.
    """
    if not update_url:
        if not silent:
            messagebox.showwarning("Cek Pembaruan", "URL endpoint pembaruan belum dikonfigurasi.")
        return

    def worker():
        try:
            info = fetch_remote_version_info(update_url)
            remote_ver = info["version"]
            
            if parse_version(remote_ver) > parse_version(current_version):
                parent.after(0, lambda: UpdateDialog(parent, current_version, info))
            else:
                if not silent:
                    parent.after(0, lambda: messagebox.showinfo(
                        "Cek Pembaruan", 
                        f"IndexRadar Pro Anda sudah menggunakan versi terbaru (v{current_version})."
                    ))
        except Exception as e:
            if not silent:
                err_msg = str(e)
                parent.after(0, lambda: messagebox.showerror(
                    "Gagal Cek Pembaruan", 
                    f"Tidak dapat menghubungi server pembaruan:\n{err_msg}"
                ))

    threading.Thread(target=worker, daemon=True).start()
