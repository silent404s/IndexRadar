import json
import os
import sys

def get_base_dir():
    """Mengambil base direktori baik saat runtime python maupun setelah di-bundle PyInstaller."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_FILE = os.path.join(get_base_dir(), 'config.json')

DEFAULT_CONFIG = {
    "captcha_api_key": "",
    "use_captcha": True,
    "threads": 2,
    "delay": 2.0,
    "auto_check_updates": True,
    "update_url": "https://raw.githubusercontent.com/silent404s/IndexRadar/main/version.json"
}

def load_config():
    """Memuat konfigurasi aplikasi. Jika file belum ada, buat dari DEFAULT_CONFIG."""
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            merged = DEFAULT_CONFIG.copy()
            merged.update(config)
            return merged
    except Exception as e:
        print(f"[ConfigManager] Gagal membaca config.json: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config):
    """Menyimpan dictionary konfigurasi ke file config.json."""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"[ConfigManager] Gagal menyimpan config.json: {e}")
        return False
