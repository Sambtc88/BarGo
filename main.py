import asyncio
import base64
import json
import os
import time
from datetime import datetime
import flet as ft
import httpx
from bs4 import BeautifulSoup

# ==================== تنظیمات هسته سناتور ====================
BASE_URL = "https://utcms.ir"
LOGIN_PAGE_URL = f"{BASE_URL}/Account/Login"
CAPTCHA_URL = f"{BASE_URL}/Account/CaptchaImage"
DASHBOARD_URL = f"{BASE_URL}/Panel/Index"
DEFAULT_PERMIT_URL = f"{BASE_URL}/Permit/Create"

SESSION_FILE = "senator_session.json"
FLEET_FILE = "senator_fleet.json"
EXTRACTED_FIELDS_FILE = "extracted_fields.json"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 15; SM-A546E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Origin": BASE_URL,
    "Referer": LOGIN_PAGE_URL,
}


class SenatorCoreEngine:
    """موتور ارتباطی ضد اختلال با قابلیت حفظ نشست، اسکن فرم و شلیک رگباری"""

    def __init__(self, log_callback):
        self.log = log_callback
        self.client: httpx.AsyncClient | None = None
        self.csrf_token = ""
        self.permit_url = DEFAULT_PERMIT_URL
        self.is_logged_in = False
        self.radar_active = False
        self.keep_alive_active = False
        self.burst_running = False
        self.server_ping_ms = -1
        self.server_status = "نامشخص"
        self.extra_form_fields = {}

    async def init_client(self):
        if self.client is None or self.client.is_closed:
            limits = httpx.Limits(
                max_keepalive_connections=25,
                max_connections=60,
                keepalive_expiry=120.0,
            )
            timeout = httpx.Timeout(connect=4.0, read=6.0, write=5.0, pool=4.0)
            self.client = httpx.AsyncClient(
                headers=DEFAULT_HEADERS,
                limits=limits,
                timeout=timeout,
                follow_redirects=True,
                verify=False,
            )
            self.load_saved_session()
            self.load_extracted_fields()

    def save_session(self):
        if not self.client:
            return
        try:
            cookies_dict = dict(self.client.cookies)
            data = {
                "cookies": cookies_dict,
                "csrf_token": self.csrf_token,
                "permit_url": self.permit_url,
                "timestamp": time.time(),
            }
            with open(SESSION_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            self.log("💾 نشست و کوکی‌ها در حافظه گوشی قفل شدند.")
        except Exception as e:
            self.log(f"خطا در ذخیره نشست: {e}")

    def load_saved_session(self):
        if not os.path.exists(SESSION_FILE) or not self.client:
            return
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for k, v in data.get("cookies", {}).items():
                self.client.cookies.set(k, v)
            self.csrf_token = data.get("csrf_token", "")
            self.permit_url = data.get("permit_url", DEFAULT_PERMIT_URL)
            if self.client.cookies:
                self.is_logged_in = True
                self.log("✅ نشست قبلی از حافظه گوشی بازیابی شد.")
        except Exception as e:
            self.log(f"خطا در بازیابی نشست: {e}")

    def load_extracted_fields(self):
        if os.path.exists(EXTRACTED_FIELDS_FILE):
            try:
                with open(EXTRACTED_FIELDS_FILE, "r", encoding="utf-8") as f:
                    self.extra_form_fields = json.load(f)
            except Exception:
                self.extra_form_fields = {}

    def extract_csrf(self, html_text: str) -> str:
        try:
            soup = BeautifulSoup(html_text, "html.parser")
            token_input = soup.find("input", {"name": "__RequestVerificationToken"})
            if token_input and token_input.get("value"):
                self.csrf_token = token_input["value"]
                return self.csrf_token
        except Exception:
            pass
        return self.csrf_token

    async def check_server_radar(self) -> tuple[bool, int, int]:
        await self.init_client()
        start = time.perf_counter()
        try:
            resp = await self.client.get(BASE_URL, timeout=3.5)
            elapsed = int((time.perf_counter() - start) * 1000)
            self.server_ping_ms = elapsed
            if resp.status_code < 500:
                self.server_status = f"آنلاین ({elapsed}ms)"
                if "__RequestVerificationToken" in resp.text:
                    self.extract_csrf(resp.text)
                return True, elapsed, resp.status_code
            else:
                self.server_status = f"اختلال سرور ({resp.status_code})"
                return False, elapsed, resp.status_code
        except Exception:
            elapsed = int((time.perf_counter() - start) * 1000)
            self.server_ping_ms = -1
            self.server_status = "قطع / تایم‌اوت"
            return False, elapsed, 0

    async def fetch_captcha_base64(self) -> str | None:
        await self.init_client()
        for attempt in range(1, 5):
            try:
                self.log(f"در حال دریافت توکن و کپچا (تلاش {attempt})...")
                page_resp = await self.client.get(LOGIN_PAGE_URL, timeout=6.0)
                if page_resp.status_code == 200:
                    self.extract_csrf(page_resp.text)

                ts = int(time.time() * 1000)
                cap_resp = await self.client.get(f"{CAPTCHA_URL}?t={ts}", timeout=5.0)
                if cap_resp.status_code == 200 and len(cap_resp.content) > 100:
                    b64_img = base64.b64encode(cap_resp.content).decode("utf-8")
                    self.log("✅ کپچا دریافت شد.")
                    return b64_img
            except Exception as e:
                self.log(f"خطای شبکه در دریافت کپچا: {type(e).__name__}")
                await asyncio.sleep(0.8)
        return None

    async def perform_login(self, username: str, password: str, captcha_code: str) -> bool:
        await self.init_client()
        payload = {
            "__RequestVerificationToken": self.csrf_token,
            "UserName": username.strip(),
            "Password": password.strip(),
            "Captcha": captcha_code.strip(),
            "RememberMe": "true",
        }
        for attempt in range(1, 6):
            try:
                self.log(f"ارسال پکت لاگین (تلاش {attempt} از ۵)...")
                resp = await self.client.post(LOGIN_PAGE_URL, data=payload, timeout=6.0)
                if resp.status_code in (200, 302):
                    if "خروج" in resp.text or "Panel" in str(resp.url) or ".ASPXAUTH" in self.client.cookies:
                        self.is_logged_in = True
                        self.extract_csrf(resp.text)
                        self.save_session()
                        self.log("🎯 ورود موفقیت‌آمیز! نشست روی سرور قفل شد.")
                        return True
                    elif "کد امنیتی" in resp.text or "کپچا" in resp.text:
                        self.log("⛔ کد کپچا اشتباه یا منقضی شده است.")
                        return False
            except Exception as e:
                self.log(f"تایم‌اوت در لاگین (تلاش {attempt}): {type(e).__name__}")
                await asyncio.sleep(0.5)
        return False

    async def warm_session_heartbeat(self):
        await self.init_client()
        try:
            resp = await self.client.get(DASHBOARD_URL, timeout=5.0)
            if resp.status_code == 200 and "Login" not in str(resp.url):
                self.extract_csrf(resp.text)
                self.save_session()
                self.log("💓 ضربان نشست: کوکی تازه شد و اتصال برقرار است.")
                return True
            elif "Login" in str(resp.url):
                self.is_logged_in = False
                self.log("⚠️ هشدار: نشست توسط سرور بسته شد، نیاز به لاگین مجدد.")
                return False
        except Exception:
            self.log("ضربان نشست: سرور پاسخ نداد (کوکی در حافظه حفظ شد).")
        return False

    async def scan_permit_form_fields(self, custom_url: str = ""):
        """استخراج خودکار نام دقیق فیلدهای فرم سامانه باربرگ روی گوشی"""
        await self.init_client()
        target_url = custom_url.strip() if custom_url.strip() else self.permit_url
        self.permit_url = target_url
        try:
            self.log(f"🔍 در حال اسکن صفحه: {target_url}")
            resp = await self.client.get(target_url, timeout=6.0)
            if resp.status_code != 200 or "Login" in str(resp.url):
                self.log("⛔ خطا: ابتدا لاگین کنید یا آدرس صفحه صدور را بررسی کنید.")
                return

            self.extract_csrf(resp.text)
            soup = BeautifulSoup(resp.text, "html.parser")
            fields = {}
            for tag in soup.find_all(["input", "select", "textarea"]):
                field_name = tag.get("name")
                field_val = tag.get("value", "")
                if field_name:
                    fields[field_name] = field_val
                    self.log(f"📌 فیلد: {field_name} = {field_val}")

            self.extra_form_fields = fields
            with open(EXTRACTED_FIELDS_FILE, "w", encoding="utf-8") as f:
                json.dump(fields, f, ensure_ascii=False, indent=2)
            self.save_session()
            self.log(f"✅ اسکن کامل شد! {len(fields)} فیلد استخراج و به موتور شلیک متصل شد.")
        except Exception as e:
            self.log(f"خطا در اسکن فرم: {type(e).__name__}")

    async def burst_issue_permit(
        self,
        truck_data: dict,
        cargo_title: str,
        weight_kg: str,
        origin: str,
        destination: str,
        workers: int = 3,
        max_rounds: int = 40,
    ) -> tuple[bool, str]:
        await self.init_client()
        self.burst_running = True
        success_flag = asyncio.Event()
        result_message = "ثبت انجام نشد."

        # ترکیب فیلدهای مخفی اسکن‌شده با اطلاعات کامیون و بار
        payload = dict(self.extra_form_fields)
        payload.update({
            "__RequestVerificationToken": self.csrf_token,
            "DriverNationalCode": truck_data.get("national_id", ""),
            "DriverMobile": truck_data.get("mobile", ""),
            "SmartCardNo": truck_data.get("smart_card", ""),
            "PlaquePart1": truck_data.get("p1", ""),
            "PlaqueChar": truck_data.get("p_char", "ع"),
            "PlaquePart2": truck_data.get("p2", ""),
            "PlaqueIran": truck_data.get("p_iran", ""),
            "CargoTypeTitle": cargo_title,
            "CargoWeight": weight_kg,
            "OriginAddress": origin,
            "DestinationAddress": destination,
        })

        async def single_shot(worker_id: int, round_num: int):
            nonlocal result_message
            if success_flag.is_set() or not self.burst_running:
                return
            try:
                start_t = time.perf_counter()
                resp = await self.client.post(self.permit_url, data=payload, timeout=4.5)
                ms = int((time.perf_counter() - start_t) * 1000)

                if resp.status_code == 200:
                    text = resp.text
                    if any(k in text for k in ["با موفقیت", "کد رهگیری", "صادر شد", "چاپ باربرگ"]):
                        success_flag.set()
                        result_message = f"باربرگ با موفقیت صادر شد! (ورکر {worker_id} - پینگ {ms}ms)"
                        self.log(f"🎯 {result_message}")
                        return
                    elif "تکراری" in text or "قبلا ثبت" in text:
                        success_flag.set()
                        result_message = "باربرگ در شلیک قبلی ثبت شده است (تکراری)."
                        self.log(f"✅ {result_message}")
                        return
                    elif "Login" in str(resp.url):
                        self.burst_running = False
                        result_message = "نشست منقضی شده! ابتدا در تب نشست لاگین کنید."
                        self.log(f"⛔ {result_message}")
                        return
                    else:
                        self.log(f"[ورکر {worker_id} | دور {round_num}] پاسخ ۲۰۰ اما ثبت نشد ({ms}ms)")
                else:
                    self.log(f"[ورکر {worker_id} | دور {round_num}] خطای سرور {resp.status_code} ({ms}ms)")
            except Exception as exc:
                self.log(f"[ورکر {worker_id} | دور {round_num}] اختلال/تایم‌اوت ({type(exc).__name__})")

        self.log(f"🚀 شروع شلیک رگباری با {workers} خط همزمان برای {truck_data.get('title')}...")

        for r in range(1, max_rounds + 1):
            if success_flag.is_set() or not self.burst_running:
                break
            tasks = [single_shot(w, r) for w in range(1, workers + 1)]
            await asyncio.gather(*tasks)
            if not success_flag.is_set() and self.burst_running:
                await asyncio.sleep(0.35)

        self.burst_running = False
        return success_flag.is_set(), result_message


# ==================== مدیریت بانک آفلاین ناوگان ====================
def load_fleet() -> list[dict]:
    if not os.path.exists(FLEET_FILE):
        return [
            {
                "title": "کامیون نمونه - ۱۲ع۳۴۵ ایران ۶۴",
                "national_id": "2990000000",
                "mobile": "09373016550",
                "smart_card": "1234567",
                "p1": "12",
                "p_char": "ع",
                "p2": "345",
                "p_iran": "64",
            }
        ]
    try:
        with open(FLEET_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_fleet(fleet_list: list[dict]):
    try:
        with open(FLEET_FILE, "w", encoding="utf-8") as f:
            json.dump(fleet_list, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ==================== رابط کاربری اپلیکیشن (Flet UI) ====================
async def main(page: ft.Page):
    page.title = "سناتور باربرگ | نسخه ویژه ضد اختلال"
    page.rtl = True
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0F172A"
    page.padding = 12
    page.scroll = ft.ScrollMode.ADAPTIVE

    fleet_data = load_fleet()
    logs_list = ft.ListView(expand=True, spacing=4, auto_scroll=True, height=220)

    def add_log(msg: str):
        now = datetime.now().strftime("%H:%M:%S")
        logs_list.controls.append(
            ft.Text(f"[{now}] {msg}", size=12, color="#E2E8F0", font_family="monospace")
        )
        if len(logs_list.controls) > 120:
            logs_list.controls.pop(0)
        page.update()

    engine = SenatorCoreEngine(log_callback=add_log)
    await engine.init_client()

    status_badge = ft.Container(
        content=ft.Text("رادار: آماده", size=12, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
        bgcolor="#334155",
        padding=ft.padding.symmetric(horizontal=10, vertical=5),
        border_radius=8,
    )
    session_badge = ft.Container(
        content=ft.Text(
            "نشست: فعال" if engine.is_logged_in else "نشست: نیاز به ورود",
            size=12,
            weight=ft.FontWeight.BOLD,
            color="#FFFFFF",
        ),
        bgcolor="#10B981" if engine.is_logged_in else "#EF4444",
        padding=ft.padding.symmetric(horizontal=10, vertical=5),
        border_radius=8,
    )

    def update_badges():
        session_badge.bgcolor = "#10B981" if engine.is_logged_in else "#EF4444"
        session_badge.content.value = "نشست: قفل شده" if engine.is_logged_in else "نشست: قطع"
        page.update()

    # ---------- تب ۱: صدور رگباری و قفل رادار ----------
    fleet_dropdown = ft.Dropdown(
        label="انتخاب سریع ناوگان (از بانک آفلاین)",
        options=[ft.dropdown.Option(key=str(i), text=item["title"]) for i, item in enumerate(fleet_data)],
        value="0" if fleet_data else None,
        border_color="#38BDF8",
    )

    cargo_input = ft.TextField(label="نوع محموله / بار", value="مصالح ساختمانی", border_color="#475569")
    weight_input = ft.TextField(
        label="وزن بار (کیلوگرم)", value="10000", keyboard_type=ft.KeyboardType.NUMBER, border_color="#475569"
    )
    origin_input = ft.TextField(label="مبدا حرکت", value="بندر لنگه - اسکله", border_color="#475569")
    dest_input = ft.TextField(label="مقصد تخلیه", value="بندر لنگه - شهرک صنعتی", border_color="#475569")

    workers_slider = ft.Slider(min=1, max=6, divisions=5, value=3, label="{value} خط همزمان")
    auto_snipe_switch = ft.Switch(
        label="قفل رادار خودکار (به محض باز شدن سرور، خودش شلیک کند)",
        value=False,
        active_color="#10B981",
    )

    result_banner = ft.Container(
        content=ft.Text("آماده شلیک به هسته سامانه...", size=13, weight=ft.FontWeight.BOLD, color="#F8FAFC"),
        bgcolor="#1E293B",
        padding=12,
        border_radius=10,
        border=ft.border.all(1, "#334155"),
    )

    async def start_burst_click(e):
        if engine.burst_running:
            engine.burst_running = False
            add_log("توقف دستی شلیک رگباری توسط کاربر.")
            result_banner.bgcolor = "#B45309"
            result_banner.content.value = "عملیات متوقف شد."
            page.update()
            return

        if not fleet_data or fleet_dropdown.value is None:
            result_banner.bgcolor = "#EF4444"
            result_banner.content.value = "ابتدا یک کامیون از لیست انتخاب کنید!"
            page.update()
            return

        selected_truck = fleet_data[int(fleet_dropdown.value)]
        result_banner.bgcolor = "#0284C7"
        result_banner.content.value = "در حال شلیک رگباری به سرور... لطفاً صبر کنید"
        page.update()

        ok, msg = await engine.burst_issue_permit(
            truck_data=selected_truck,
