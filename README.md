# 🎯 IndexRadar Pro

**IndexRadar Pro** adalah aplikasi desktop modern berbasis Python & CustomTkinter yang dirancang untuk memeriksa status pengindeksan domain pada Google Search (`site:domain.com`) secara massal, cepat, dan akurat.

---

## ✨ Fitur Utama

- 🎨 **Modern Dark UI/UX**: Tampilan elegan berbasis CustomTkinter dengan dukungan High-DPI Windows.
- ⚡ **Multi-Threaded Engine**: Pengecekan paralel menggunakan engine headless Chromium anti-detection.
- 🛡️ **Auto-Bypass CAPTCHA**: Terintegrasi langsung dengan resolver 2Captcha untuk penanganan otomatis jika muncul reCAPTCHA Google.
- 📋 **Quick-Copy Status**: Tombol instan untuk menyalin hasil spesifik (Hanya INDEX, Hanya UN-INDEX, atau GAGAL).
- 💾 **Export CSV**: Ekspor hasil laporan lengkap berstandar UTF-8 BOM.
- 🚀 **Auto-Update Tracker**: Sistem pelacakan rilis dan update checker otomatis berbasis repository GitHub.
- 📦 **Standalone Windows Installer**: Wizard instalasi resmi Windows berbasis Inno Setup.

---

## 📁 Struktur Direktori

```
IndexRadar/
├── .gitignore               # Konfigurasi filter Git untuk keamanan & sanitasi kredensial
├── requirements.txt         # Daftar pustaka dependensi Python
├── version.json             # Informasi versi & release notes untuk auto-update
├── config.json.example      # Template konfigurasi bersih
├── build_exe.py             # Script builder standalone PyInstaller & Inno Setup
├── installer_setup.iss      # Script Inno Setup compiler Windows installer
├── indexradar_icon.ico      # Ikon aplikasi
├── indexradar_icon.png      # Ikon resolusi tinggi PNG
├── main.py                  # Entry point aplikasi utama
└── src/
    ├── config_manager.py    # Modul pembaca dan penyimpan konfigurasi
    ├── update_checker.py    # Modul pengecekan versi dan dialog update modal
    ├── captcha_service.py   # Modul service 2Captcha resolver
    ├── checker_engine.py    # Modul engine Selenium multi-threading
    ├── export_utils.py      # Modul ekspor laporan CSV
    └── ui/
        ├── main_window.py   # Window UI utama CustomTkinter
        ├── table_view.py    # Komponen tabel dark mode modern
        └── dialogs.py       # Dialog modal Pengaturan & Info Aplikasi
```

---

## 🚀 Panduan Menjalankan Aplikasi

### 1. Persyaratan Sistem
- Python 3.9+
- Google Chrome Browser terpasang

### 2. Instalasi Dependensi
```bash
pip install -r requirements.txt
```

### 3. Menjalankan Aplikasi
```bash
python main.py
```

---

## 🔨 Membangun File Executable & Installer

Untuk membuat file `.exe` standalone dan installer Windows secara otomatis:
```bash
python build_exe.py
```
Output installer `.exe` akan tersimpan di folder `Output/IndexRadar_Setup_v1.0.0.exe`.
