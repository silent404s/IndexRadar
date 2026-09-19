import os
import sys
import ctypes
import customtkinter as ctk

from src.ui.main_window import MainWindow

def setup_windows_environment():
    """Mengaktifkan pengaturan Windows untuk rendering High-DPI dan Taskbar Grouping."""
    try:
        # App UserModelID untuk taskbar icon grouping
        app_id = 'indexradar.pro.checker.v1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        
        # Per-Monitor V2 DPI Aware (2) atau Per-Monitor (1) fallback
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

def main():
    setup_windows_environment()
    
    # CustomTkinter theme setup
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
