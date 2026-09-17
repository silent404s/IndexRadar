import re
import random
import time
import queue
import threading
from urllib.parse import urlparse, quote_plus

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from .captcha_service import solve_google_recaptcha

def clean_domain(text):
    """
    Membersihkan URL atau domain dari skema protokol, path, query string, trailing slash,
    serta otomatis menghilangkan awalan www. agar format domain dan pengecekan site: bersih.
    """
    text = text.strip()
    if not text:
        return ""
    
    if not text.startswith(('http://', 'https://')):
        candidate = 'http://' + text
    else:
        candidate = text

    try:
        parsed = urlparse(candidate)
        netloc = parsed.netloc or parsed.path
        if ':' in netloc:
            netloc = netloc.split(':')[0]
        netloc = netloc.strip().strip('/')
        netloc = re.sub(r'[^\w\.-]', '', netloc)
        
        # Hilangkan awalan www. (case-insensitive) dan jadikan huruf kecil
        netloc = netloc.lower()
        while netloc.startswith('www.'):
            netloc = netloc[4:]
            
        return netloc
    except Exception:
        clean = text.split('/')[0].strip().lower()
        while clean.startswith('www.'):
            clean = clean[4:]
        return clean

def create_headless_driver(proxy=None):
    """
    Membuat instance Chrome Headless anti-detection yang ringan.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--lang=en-US")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ]
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    if proxy:
        proxy_clean = proxy.strip()
        if not proxy_clean.startswith(('http://', 'https://')):
            proxy_clean = 'http://' + proxy_clean
        chrome_options.add_argument(f"--proxy-server={proxy_clean}")

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)

    # Bypass navigator.webdriver
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """
    })
    return driver

def parse_google_result(driver, domain):
    """
    Menganalisa halaman hasil pencarian SERP Google untuk query site:domain.
    Returns: (status, pages_str, detail_msg)
    """
    try:
        page_source = driver.page_source.lower()
        current_url = driver.current_url.lower()

        # 1. Cek keberadaan CAPTCHA / Unusual Traffic
        if "unusual traffic" in page_source or "sorry/index" in current_url or "g-recaptcha" in page_source:
            return ("CAPTCHA", "0", "Terdeteksi CAPTCHA Google")

        # 2. Tangani Cookie Consent Dialog Google
        if "consent.google.com" in current_url or "before you continue to google" in page_source:
            try:
                consent_btns = driver.find_elements(By.CSS_SELECTOR, "button#L2AGLb, button#W0wltc, form[action*='consent'] button")
                for b in consent_btns:
                    if b.is_displayed():
                        b.click()
                        time.sleep(1.5)
                        page_source = driver.page_source.lower()
                        break
            except Exception:
                pass

        # 3. Cek pola halaman tidak terindeks (Un-indexed)
        unindex_keywords = [
            "did not match any documents",
            "tidak cocok dengan dokumen",
            "tidak menghasilkan dokumen",
            "no results found for",
            "tidak ada hasil untuk",
            "did not match any search results"
        ]
        for kw in unindex_keywords:
            if kw in page_source:
                return ("UN-INDEX", "0", "Tidak ditemukan di indeks Google")

        # 4. Cek statistik hasil dari #result-stats
        stats_elements = driver.find_elements(By.ID, "result-stats")
        if stats_elements:
            raw_text = stats_elements[0].get_attribute("textContent").strip()
            if re.search(r'\b0\s+(results|hasil)\b', raw_text, re.IGNORECASE):
                return ("UN-INDEX", "0", "0 Hasil")

            before_paren = raw_text.split('(')[0]
            num_match = re.search(r'([\d\.,\s]+)\s*(?:results|hasil)', before_paren, re.IGNORECASE)
            if num_match:
                pages_str = num_match.group(1).strip()
                pages_str = re.sub(r'\s+', '', pages_str)
                if pages_str and pages_str != "0":
                    return ("INDEX", pages_str, f"{pages_str} hasil ditemukan")
                elif pages_str == "0":
                    return ("UN-INDEX", "0", "0 Hasil")
            elif raw_text:
                clean_txt = raw_text.split('(')[0].replace("About", "").replace("Sekitar", "").strip()
                return ("INDEX", clean_txt, f"Terindeks ({clean_txt})")

        # 5. Cek elemen hasil pencarian organik
        search_items = driver.find_elements(By.CSS_SELECTOR, "div.g, div.MjjYud, div[data-sokoban-container], #search")
        if len(search_items) > 0:
            return ("INDEX", f"{len(search_items)}+", f"Ditemukan {len(search_items)}+ halaman")

        return ("UN-INDEX", "0", "Halaman kosong / tidak ada hasil")

    except Exception as e:
        return ("FAILED", "N/A", f"Error analisa: {str(e)[:40]}")

class CheckerEngine:
    def __init__(self, gui_queue):
        self.gui_queue = gui_queue
        self.stop_requested = False
        self.worker_drivers = []
        self.active_threads = []

    def stop(self):
        """Menghentikan seluruh worker dan menutup instance browser."""
        self.stop_requested = True
        drivers_to_close = list(self.worker_drivers)
        for d in drivers_to_close:
            try:
                d.quit()
            except Exception:
                pass

    def run_supervisor(self, items, proxies_list, num_threads, base_delay, use_2captcha, api_key_2captcha, is_task_list=False):
        """
        Thread supervisor yang membagi tugas ke pool worker.
        Jika is_task_list=True, items adalah list tuple [(index_no, domain), ...].
        Jika is_task_list=False, items adalah list domain ['domain1', 'domain2', ...].
        """
        self.stop_requested = False
        self.worker_drivers = []
        self.active_threads = []

        task_queue = queue.Queue()
        if is_task_list:
            for idx, d in items:
                task_queue.put((idx, d))
            total_items = len(items)
        else:
            for idx, d in enumerate(items, start=1):
                task_queue.put((idx, d))
            total_items = len(items)

        actual_threads = max(1, min(num_threads, total_items)) if total_items > 0 else 1
        threads = []

        for _ in range(actual_threads):
            t = threading.Thread(
                target=self._worker_loop,
                args=(task_queue, proxies_list, base_delay, use_2captcha, api_key_2captcha),
                daemon=True
            )
            t.start()
            threads.append(t)
            self.active_threads.append(t)

        for t in threads:
            t.join()

        self.gui_queue.put(("ALL_DONE", None))

    def _worker_loop(self, task_queue, proxies_list, base_delay, use_2captcha, api_key_2captcha):
        driver = None
        current_proxy = random.choice(proxies_list) if proxies_list else None

        try:
            driver = create_headless_driver(current_proxy)
            with threading.Lock():
                self.worker_drivers.append(driver)

            while not self.stop_requested:
                try:
                    task = task_queue.get_nowait()
                except queue.Empty:
                    break

                index_no, domain = task
                self.gui_queue.put(("ROW_START", (index_no, domain)))
                self.gui_queue.put(("STATUS", f"Sedang memeriksa (#{index_no}): {domain}..."))

                status, pages, detail = "FAILED", "N/A", "Error"
                try:
                    query_url = f"https://www.google.com/search?q=site:{quote_plus(domain)}&hl=en"
                    driver.get(query_url)
                    time.sleep(1.0)

                    status, pages, detail = parse_google_result(driver, domain)

                    # Jika terdeteksi CAPTCHA dan opsi 2Captcha aktif
                    if status == "CAPTCHA":
                        if use_2captcha and api_key_2captcha:
                            def captcha_status_cb(m):
                                self.gui_queue.put(("STATUS", m))
                                self.gui_queue.put(("ROW_UPDATE", (index_no, domain, "⏳ CAPTCHA", "⏳", f"2Captcha: {m}")))

                            solved, msg = solve_google_recaptcha(
                                driver=driver,
                                api_key=api_key_2captcha,
                                domain=domain,
                                status_callback=captcha_status_cb,
                                stop_check_callback=lambda: self.stop_requested
                            )
                            if solved:
                                status, pages, detail = parse_google_result(driver, domain)
                                if status in ("INDEX", "UN-INDEX"):
                                    detail += " [2Captcha Solved]"
                                else:
                                    status, pages, detail = "FAILED", "0", "Gagal verifikasi setelah solve"
                            else:
                                status, pages, detail = "FAILED", "0", f"CAPTCHA: {msg}"
                        else:
                            status, pages, detail = "FAILED", "0", "Terdeteksi CAPTCHA (2Captcha tidak aktif)"

                except Exception as e:
                    detail = f"Browser Error: {str(e)[:35]}"
                    status = "FAILED"

                # Kirim hasil ke antrean GUI
                self.gui_queue.put(("RESULT", (index_no, domain, status, pages, detail)))
                task_queue.task_done()

                if not self.stop_requested:
                    jitter = random.uniform(0.8, 1.8)
                    time.sleep(base_delay * jitter)

        except Exception as err:
            self.gui_queue.put(("LOG_ERROR", f"Worker crash: {err}"))
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
                with threading.Lock():
                    if driver in self.worker_drivers:
                        self.worker_drivers.remove(driver)
