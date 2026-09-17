import requests
import time
import re

def get_2captcha_balance(api_key, timeout=10):
    """
    Mengambil saldo akun 2Captcha.
    Returns: float (saldo dalam USD) atau None jika gagal.
    """
    if not api_key:
        return None
    try:
        url = f"https://2captcha.com/res.php?key={api_key.strip()}&action=getbalance&json=1"
        res = requests.get(url, timeout=timeout).json()
        if res.get("status") == 1:
            return float(res.get("request", 0.0))
    except Exception as e:
        print(f"[2Captcha Service] Gagal cek saldo: {e}")
    return None

def solve_google_recaptcha(driver, api_key, domain, status_callback=None, stop_check_callback=None):
    """
    Mendeteksi dan memecahkan reCAPTCHA v2 Google menggunakan API 2Captcha.
    """
    if not api_key:
        return False, "API Key 2Captcha belum diisi"

    def log(msg):
        if status_callback:
            status_callback(msg)

    try:
        log(f"[2Captcha] Mendeteksi parameter CAPTCHA untuk {domain}...")
        sitekey = None
        data_s = None

        # 1. Cek di elemen div.g-recaptcha
        try:
            from selenium.webdriver.common.by import By
            recaptcha_els = driver.find_elements(By.CSS_SELECTOR, "div.g-recaptcha")
            if recaptcha_els:
                sitekey = recaptcha_els[0].get_attribute("data-sitekey")
                data_s = recaptcha_els[0].get_attribute("data-s")

            # 2. Cek di iframe reCAPTCHA
            if not sitekey:
                iframes = driver.find_elements(By.CSS_SELECTOR, "iframe[src*='recaptcha']")
                for ifr in iframes:
                    src = ifr.get_attribute("src") or ""
                    k_m = re.search(r'[?&]k=([^&]+)', src)
                    if k_m:
                        sitekey = k_m.group(1)
                    s_m = re.search(r'[?&]s=([^&]+)', src)
                    if s_m:
                        data_s = s_m.group(1)
                    if sitekey:
                        break
        except Exception:
            pass

        # 3. Fallback Regex di page_source
        if not sitekey:
            ps = driver.page_source
            k_m = re.search(r'data-sitekey=["\']([^"\']+)["\']', ps)
            if k_m:
                sitekey = k_m.group(1)
            s_m = re.search(r'data-s=["\']([^"\']+)["\']', ps)
            if s_m:
                data_s = s_m.group(1)

        if not sitekey:
            return False, "Gagal mendeteksi data-sitekey reCAPTCHA Google"

        # Kirim task ke 2Captcha in.php
        in_payload = {
            "key": api_key.strip(),
            "method": "userrecaptcha",
            "googlekey": sitekey,
            "pageurl": driver.current_url,
            "json": 1
        }
        if data_s:
            in_payload["data-s"] = data_s

        log(f"[2Captcha] Mengirim request pemecahan CAPTCHA ({domain})...")
        in_resp = requests.post("https://2captcha.com/in.php", data=in_payload, timeout=20).json()

        if in_resp.get("status") != 1:
            return False, f"2Captcha Error: {in_resp.get('request')}"

        req_id = in_resp.get("request")
        log(f"[2Captcha] Task #{req_id}: Menunggu pemrosesan token...")

        # Polling hasil (maks 120 detik)
        start_poll = time.time()
        for _ in range(25):
            if stop_check_callback and stop_check_callback():
                return False, "Dibatalkan oleh pengguna"

            time.sleep(5)
            elapsed = int(time.time() - start_poll)
            log(f"[2Captcha] Memecahkan CAPTCHA ({elapsed}d)...")

            res_url = f"https://2captcha.com/res.php?key={api_key.strip()}&action=get&id={req_id}&json=1"
            res_resp = requests.get(res_url, timeout=15).json()

            if res_resp.get("status") == 1:
                token = res_resp.get("request")
                log(f"[2Captcha] Solusi didapat! Menyuntikkan token...")

                # Inject token ke response form Google
                driver.execute_script("""
                    var token = arguments[0];
                    var el = document.getElementById('g-recaptcha-response');
                    if (!el) {
                        el = document.createElement('textarea');
                        el.id = 'g-recaptcha-response';
                        el.name = 'g-recaptcha-response';
                        document.body.appendChild(el);
                    }
                    el.innerHTML = token;
                    el.value = token;
                    el.style.display = 'block';

                    var form = document.getElementById('captcha-form') || 
                               document.querySelector('form[action*="sorry"]') || 
                               document.querySelector('form[action*="index"]') || 
                               document.querySelector('form');
                    if (form) {
                        form.submit();
                    }
                """, token)

                time.sleep(4)
                return True, "CAPTCHA berhasil diselesaikan"

            if res_resp.get("request") != "CAPCHA_NOT_READY":
                return False, f"2Captcha gagal: {res_resp.get('request')}"

        return False, "2Captcha Timeout (120 detik)"

    except Exception as e:
        return False, f"Kesalahan 2Captcha: {str(e)[:40]}"
