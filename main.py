import asyncio
import base64
import json
import os
import time
from datetime import datetime
import flet as ft
import httpx
from bs4 import BeautifulSoup

# ==================== تنظیمات هسته سناتور (قابل تنظیم مطابق اندپوینت‌ها) ====================
BASE_URL = "https://utcms.ir"
LOGIN_PAGE_URL = f"{BASE_URL}/Account/Login"
CAPTCHA_URL = f"{BASE_URL}/Account/CaptchaImage"
DASHBOARD_URL = f"{BASE_URL}/Panel/Index"
ISSUE_PERMIT_URL = f"{BASE_URL}/Permit/Create"  # مسیر ثبت نهایی باربرگ

SESSION_FILE = "senator_session.json"
FLEET_FILE = "senator_fleet.json"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 15; SM-A546E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Origin": BASE_URL,
    "Referer": LOGIN_PAGE_URL,
}


class SenatorCoreEngine:
    """موتور ارتباطی ضد اختلال با قابلیت حفظ نشست و شلیک رگباری روی اینترنت موبایل"""

    def __init__(self, log_callback):
        self.log = log_callback
        self.client: httpx.AsyncClient | None = None
        self.csrf_token = ""
        self.is_logged_in = False
        self.radar_active = False
        self.keep_alive_active = False
        self.burst_running = False
        self.server_ping_ms = -1
        self.server_status = "نامشخص"

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

    def save_session(self):
        if not self.client:
            return
        try:
            cookies_dict = dict(self.client.cookies)
            data = {
                "cookies": cookies_dict,
                "csrf_token": self.csrf_token,
                "timestamp": time.time(),
            }
            with open(SESSION_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            self.log("نشست و کوکی‌ها در حافظه گوشی قفل شدند.")
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
            if self.client.cookies:
                self.is_logged_in = True
                self.log("نشست قبلی از حافظه بازیابی شد (نیاز به لاگین مجدد نیست).")
        except Exception as e:
            self.log(f"خطا در بازیابی نشست: {e}")

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
        """تست پینگ و باز بودن درگاه سامانه بدون هدر دادن ترافیک"""
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
        """دریافت تصویر کپچا و توکن همزمان در یک نشست واحد"""
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
                    self.log("کپچا با موفقیت دریافت شد.")
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
                        self.log("ورود موفقیت‌آمیز! نشست روی سرور قفل شد.")
                        return True
                    elif "کد امنیتی" in resp.text or "کپچا" in resp.text:
                        self.log("کد کپچا اشتباه یا منقضی شده است.")
                        return False
            except Exception as e:
                self.log(f"تایم‌اوت در لاگین (تلاش {attempt}): {type(e).__name__}")
                await asyncio.sleep(0.5)
        return False

    async def warm_session_heartbeat(self):
        """گرم نگه داشتن نشست در پس‌زمینه برای جلوگیری از پریدن لاگین در زمان اختلال"""
        await self.init_client()
        try:
            resp = await self.client.get(DASHBOARD_URL, timeout=5.0)
            if resp.status_code == 200 and "Login" not in str(resp.url):
                self.extract_csrf(resp.text)
                self.save_session()
                self.log("ضربان نشست: کوکی تازه شد و اتصال برقرار است.")
                return True
            elif "Login" in str(resp.url):
                self.is_logged_in = False
                self.log("هشدار: نشست توسط سرور بسته شد، نیاز به لاگین مجدد.")
                return False
        except Exception:
            self.log("ضربان نشست: سرور فعلاً پاسخ نداد (کوکی در حافظه حفظ شد).")
        return False

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
        """
        موتور شلیک رگباری سناتور:
        ارسال همزمان چند درخواست با تایم‌اوت کوتاه تا اولین پاسخ مثبت از سرور در زمان اختلال دریافت شود.
        """
        await self.init_client()
        self.burst_running = True
        success_flag = asyncio.Event()
        result_message = "ثبت انجام نشد."

        payload = {
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
        }

        async def single_shot(worker_id: int, round_num: int):
            nonlocal result_message
            if success_flag.is_set() or not self.burst_running:
                return
            try:
                start_t = time.perf_counter()
                resp = await self.client.post(ISSUE_PERMIT_URL, data=payload, timeout=4.5)
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

        self.log(f"🚀 شروع شلیک رگباری با {workers} خط همزمان برای پلاک {truck_data.get('title')}...")

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

    # ---------- نوار وضعیت بالای صفحه (رادار زنده) ----------
    status_badge = ft.Container(
        content=ft.Text("رادار: آماده بررسی", size=12, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
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
            cargo_title=cargo_input.value,
            weight_kg=weight_input.value,
            origin=origin_input.value,
            destination=dest_input.value,
            workers=int(workers_slider.value),
            max_rounds=35,
        )
        update_badges()
        result_banner.bgcolor = "#10B981" if ok else "#EF4444"
        result_banner.content.value = msg
        page.update()

    async def radar_loop():
        while engine.radar_active:
            is_up, ping, code = await engine.check_server_radar()
            if is_up:
                status_badge.bgcolor = "#10B981"
                status_badge.content.value = f"سرور باز است ({ping}ms)"
                if auto_snipe_switch.value and not engine.burst_running:
                    add_log("⚡ رادار باز شدن سرور را شکار کرد! شروع خودکار شلیک رگباری...")
                    await start_burst_click(None)
                    auto_snipe_switch.value = False
            else:
                status_badge.bgcolor = "#EF4444"
                status_badge.content.value = f"اختلال سرور ({code if code else 'Timeout'})"
            page.update()
            await asyncio.sleep(3.5)

    def toggle_radar(e):
        engine.radar_active = e.control.value
        if engine.radar_active:
            add_log("رادار پایش زنده سرور فعال شد (بررسی هر ۳.۵ ثانیه).")
            page.run_task(radar_loop)
        else:
            status_badge.bgcolor = "#334155"
            status_badge.content.value = "رادار: غیرفعال"
            add_log("رادار متوقف شد.")
            page.update()

    radar_switch = ft.Switch(label="روشن کردن رادار زنده سرور", value=False, on_change=toggle_radar)

    tab_issue_content = ft.Column(
        spacing=10,
        controls=[
            ft.Container(
                bgcolor="#1E293B",
                padding=12,
                border_radius=10,
                content=ft.Column(
                    spacing=6,
                    controls=[
                        radar_switch,
                        auto_snipe_switch,
                        ft.Text("تعداد خطوط شلیک همزمان (پیشنهادی: ۳ خط):", size=12, color="#94A3B8"),
                        workers_slider,
                    ],
                ),
            ),
            fleet_dropdown,
            ft.Row(
                controls=[
                    ft.Container(content=cargo_input, expand=True),
                    ft.Container(content=weight_input, expand=True),
                ]
            ),
            origin_input,
            dest_input,
            result_banner,
            ft.ElevatedButton(
                text="🔥 شروع / توقف شلیک رگباری باربرگ",
                bgcolor="#F59E0B",
                color="#0F172A",
                height=50,
                on_click=start_burst_click,
            ),
        ],
    )

    # ---------- تب ۲: مدیریت نشست و کپچا ----------
    user_input = ft.TextField(label="نام کاربری سامانه", border_color="#475569")
    pass_input = ft.TextField(label="رمز عبور سامانه", password=True, can_reveal_password=True, border_color="#475569")
    captcha_img = ft.Image(
        src_base64="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",
        width=180,
        height=60,
        fit=ft.ImageFit.CONTAIN,
    )
    captcha_input = ft.TextField(
        label="کد کپچا", keyboard_type=ft.KeyboardType.NUMBER, border_color="#38BDF8", expand=True
    )

    async def load_captcha_click(e):
        b64 = await engine.fetch_captcha_base64()
        if b64:
            captcha_img.src_base64 = b64
            page.update()

    async def login_click(e):
        if not captcha_input.value:
            add_log("لطفاً کد کپچا را وارد کنید.")
            return
        ok = await engine.perform_login(user_input.value, pass_input.value, captcha_input.value)
        update_badges()

    async def keep_alive_loop():
        while engine.keep_alive_active:
            await engine.warm_session_heartbeat()
            update_badges()
            await asyncio.sleep(90)

    def toggle_keep_alive(e):
        engine.keep_alive_active = e.control.value
        if engine.keep_alive_active:
            add_log("نگهبان نشست فعال شد (ارسال پالس هر ۹۰ ثانیه برای جلوگیری از پریدن لاگین).")
            page.run_task(keep_alive_loop)
        else:
            add_log("نگهبان نشست غیرفعال شد.")

    tab_session_content = ft.Column(
        spacing=12,
        controls=[
            ft.Text(
                "نکته طلایی: یک‌بار که لاگین کنید، کوکی روی گوشی ذخیره می‌شود و حتی در صورت بسته شدن برنامه یا اختلال سامانه نیازی به لاگین مجدد نیست.",
                size=12,
                color="#38BDF8",
            ),
            user_input,
            pass_input,
            ft.Row(
                controls=[
                    ft.Container(
                        content=captcha_img,
                        bgcolor="#FFFFFF",
                        border_radius=8,
                        padding=4,
                    ),
                    ft.ElevatedButton(
                        text="دریافت کپچا",
                        bgcolor="#334155",
                        color="#FFFFFF",
                        on_click=load_captcha_click,
                    ),
                ]
            ),
            captcha_input,
            ft.ElevatedButton(
                text="🔐 ورود و قفل کردن نشست روی گوشی",
                bgcolor="#10B981",
                color="#FFFFFF",
                height=48,
                on_click=login_click,
            ),
            ft.Switch(
                label="نگهبان نشست (گرم نگه داشتن خودکار لاگین در پس‌زمینه)",
                value=False,
                on_change=toggle_keep_alive,
            ),
        ],
    )

    # ---------- تب ۳: بانک آفلاین ناوگان ----------
    f_title = ft.TextField(label="نام نمایشی (مثلاً: ولوو احمد - ۱۲ع۳۴۵)", border_color="#475569")
    f_nid = ft.TextField(label="کد ملی راننده", keyboard_type=ft.KeyboardType.NUMBER, border_color="#475569")
    f_mob = ft.TextField(label="موبایل راننده", keyboard_type=ft.KeyboardType.PHONE, border_color="#475569")
    f_smart = ft.TextField(label="شماره هوشمند ناوگان", keyboard_type=ft.KeyboardType.NUMBER, border_color="#475569")
    f_p1 = ft.TextField(label="دو رقم اول", width=90, keyboard_type=ft.KeyboardType.NUMBER)
    f_char = ft.TextField(label="حرف", value="ع", width=70)
    f_p2 = ft.TextField(label="سه رقم", width=100, keyboard_type=ft.KeyboardType.NUMBER)
    f_iran = ft.TextField(label="ایران", value="64", width=80, keyboard_type=ft.KeyboardType.NUMBER)

    fleet_list_view = ft.Column(spacing=6)

    def refresh_fleet_ui():
        fleet_dropdown.options = [
            ft.dropdown.Option(key=str(i), text=item["title"]) for i, item in enumerate(fleet_data)
        ]
        if fleet_data and fleet_dropdown.value is None:
            fleet_dropdown.value = "0"
        fleet_list_view.controls.clear()
        for idx, item in enumerate(fleet_data):
            fleet_list_view.controls.append(
                ft.Container(
                    bgcolor="#1E293B",
                    padding=10,
                    border_radius=8,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(f"{item['title']} | ملی: {item['national_id']}", size=12, color="#E2E8F0"),
                            ft.TextButton(
                                text="حذف",
                                data=idx,
                                on_click=delete_truck_click,
                            ),
                        ],
                    ),
                )
            )
        page.update()

    def delete_truck_click(e):
        idx = e.control.data
        if 0 <= idx < len(fleet_data):
            removed = fleet_data.pop(idx)
            save_fleet(fleet_data)
            add_log(f"ناوگان '{removed['title']}' حذف شد.")
            refresh_fleet_ui()

    def add_truck_click(e):
        if not f_title.value or not f_nid.value:
            add_log("نام نمایشی و کد ملی راننده الزامی است.")
            return
        new_item = {
            "title": f_title.value.strip(),
            "national_id": f_nid.value.strip(),
            "mobile": f_mob.value.strip(),
            "smart_card": f_smart.value.strip(),
            "p1": f_p1.value.strip(),
            "p_char": f_char.value.strip(),
            "p2": f_p2.value.strip(),
            "p_iran": f_iran.value.strip(),
        }
        fleet_data.append(new_item)
        save_fleet(fleet_data)
        f_title.value = ""
        f_nid.value = ""
        add_log("کامیون جدید در بانک آفلاین گوشی ذخیره شد.")
        refresh_fleet_ui()

    refresh_fleet_ui()

    tab_fleet_content = ft.Column(
        spacing=10,
        controls=[
            ft.Text("افزودن کامیون به حافظه آفلاین (برای صدور بدون استعلام):", size=13, weight=ft.FontWeight.BOLD),
            f_title,
            ft.Row(controls=[ft.Container(f_nid, expand=True), ft.Container(f_mob, expand=True)]),
            f_smart,
            ft.Row(controls=[f_p1, f_char, f_p2, f_iran]),
            ft.ElevatedButton(
                text="➕ ذخیره در بانک آفلاین گوشی",
                bgcolor="#0284C7",
                color="#FFFFFF",
                on_click=add_truck_click,
            ),
            ft.Divider(color="#334155"),
            ft.Text("لیست ناوگان ذخیره شده:", size=13, weight=ft.FontWeight.BOLD),
            fleet_list_view,
        ],
    )

    # ---------- چیدمان اصلی صفحه با سوئیچ تب‌ها ----------
    body_container = ft.Container(content=tab_issue_content, padding=ft.padding.only(top=8))

    def switch_tab(e):
        selected = e.control.data
        if selected == "issue":
            body_container.content = tab_issue_content
        elif selected == "session":
            body_container.content = tab_session_content
        elif selected == "fleet":
            body_container.content = tab_fleet_content
        page.update()

    nav_bar = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        controls=[
            ft.ElevatedButton("🚀 صدور رگباری", data="issue", on_click=switch_tab, bgcolor="#1E293B", color="#38BDF8"),
            ft.ElevatedButton("🔑 نشست و کپچا", data="session", on_click=switch_tab, bgcolor="#1E293B", color="#10B981"),
            ft.ElevatedButton("🚛 بانک ناوگان", data="fleet", on_click=switch_tab, bgcolor="#1E293B", color="#F59E0B"),
        ],
    )

    page.add(
        ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text("⚡ سناتور باربرگ | هسته موبایل", size=16, weight=ft.FontWeight.BOLD, color="#F8FAFC"),
                ft.Row(controls=[status_badge, session_badge]),
            ],
        ),
        nav_bar,
        body_container,
        ft.Divider(color="#334155"),
        ft.Text("کنسول زنده شبکه و پاسخ سرور:", size=12, weight=ft.FontWeight.BOLD, color="#94A3B8"),
        ft.Container(
            content=logs_list,
            bgcolor="#020617",
            padding=8,
            border_radius=8,
            border=ft.border.all(1, "#1E293B"),
        ),
    )


if __name__ == "__main__":
    ft.app(target=main)
