import asyncio
import base64
import json
import os
import time
from datetime import datetime
import flet as ft
import httpx

# ==================== تنظیمات هسته سناتور ====================
BASE_URL = "https://utcms.ir"
LOGIN_PAGE_URL = f"{BASE_URL}/Account/Login"
CAPTCHA_URL = f"{BASE_URL}/Account/CaptchaImage"
DASHBOARD_URL = f"{BASE_URL}/Panel/Index"
ISSUE_PERMIT_URL = f"{BASE_URL}/Permit/Create"

SESSION_FILE = "senator_session.json"
FLEET_FILE = "senator_fleet.json"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 15; SM-A546E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Origin": BASE_URL,
    "Referer": LOGIN_PAGE_URL,
}


class SenatorCoreEngine:
    def __init__(self, log_callback):
        self.log = log_callback
        self.client: httpx.AsyncClient | None = None
        self.csrf_token = ""
        self.is_logged_in = False
        self.radar_active = False
        self.keep_alive_active = False
        self.burst_running = False

    async def init_client(self):
        if self.client is None or self.client.is_closed:
            limits = httpx.Limits(max_keepalive_connections=20, max_connections=50)
            timeout = httpx.Timeout(connect=5.0, read=5.0, write=5.0, pool=5.0)
            self.client = httpx.AsyncClient(
                headers=DEFAULT_HEADERS, limits=limits, timeout=timeout, follow_redirects=True, verify=False
            )
            self.load_saved_session()

    def save_session(self):
        if not self.client:
            return
        try:
            cookies_dict = dict(self.client.cookies)
            data = {"cookies": cookies_dict, "csrf_token": self.csrf_token}
            with open(SESSION_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f)
            self.log("کوکی‌ها و نشست در حافظه قفل شدند.")
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
                self.log("نشست قبلی از حافظه بارگذاری شد.")
        except Exception as e:
            self.log(f"خطا در بارگذاری نشست: {e}")

    def extract_csrf_simple(self, html_text: str) -> str:
        """استخراج توکن امنیتی بدون نیاز به پکیج‌های سنگین"""
        try:
            target = 'name="__RequestVerificationToken" type="hidden" value="'
            idx = html_text.find(target)
            if idx != -1:
                start = idx + len(target)
                end = html_text.find('"', start)
                if end != -1:
                    self.csrf_token = html_text[start:end]
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
            if resp.status_code < 500:
                self.extract_csrf_simple(resp.text)
                return True, elapsed, resp.status_code
            return False, elapsed, resp.status_code
        except Exception:
            elapsed = int((time.perf_counter() - start) * 1000)
            return False, elapsed, 0

    async def fetch_captcha_base64(self) -> str | None:
        await self.init_client()
        try:
            page_resp = await self.client.get(LOGIN_PAGE_URL, timeout=6.0)
            if page_resp.status_code == 200:
                self.extract_csrf_simple(page_resp.text)

            ts = int(time.time() * 1000)
            cap_resp = await self.client.get(f"{CAPTCHA_URL}?t={ts}", timeout=5.0)
            if cap_resp.status_code == 200 and len(cap_resp.content) > 100:
                return base64.b64encode(cap_resp.content).decode("utf-8")
        except Exception as e:
            self.log(f"خطا در دریافت کپچا: {e}")
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
        try:
            resp = await self.client.post(LOGIN_PAGE_URL, data=payload, timeout=6.0)
            if resp.status_code in (200, 302):
                if "خروج" in resp.text or "Panel" in str(resp.url) or ".ASPXAUTH" in self.client.cookies:
                    self.is_logged_in = True
                    self.extract_csrf_simple(resp.text)
                    self.save_session()
                    self.log("ورود موفقیت‌آمیز! نشست قفل شد.")
                    return True
        except Exception as e:
            self.log(f"خطا در لاگین: {e}")
        return False

    async def burst_issue_permit(
        self, truck_data: dict, cargo_title: str, weight_kg: str, origin: str, destination: str, workers: int = 3
    ) -> tuple[bool, str]:
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

        async def single_shot(worker_id: int):
            nonlocal result_message
            if success_flag.is_set() or not self.burst_running:
                return
            try:
                resp = await self.client.post(ISSUE_PERMIT_URL, data=payload, timeout=4.0)
                if resp.status_code == 200:
                    text = resp.text
                    if any(k in text for k in ["با موفقیت", "کد رهگیری", "صادر شد"]):
                        success_flag.set()
                        result_message = f"باربرگ با موفقیت صادر شد! (ورکر {worker_id})"
                        self.log(result_message)
            except Exception:
                pass

        self.log(f"شروع شلیک رگباری برای پلاک {truck_data.get('title')}...")
        for _ in range(30):
            if success_flag.is_set() or not self.burst_running:
                break
            await asyncio.gather(*(single_shot(w) for w in range(1, workers + 1)))
            await asyncio.sleep(0.3)

        self.burst_running = False
        return success_flag.is_set(), result_message


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


async def main(page: ft.Page):
    page.title = "سناتور باربرگ"
    page.rtl = True
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0F172A"
    page.padding = 12
    page.scroll = ft.ScrollMode.ADAPTIVE

    fleet_data = load_fleet()
    logs_list = ft.ListView(expand=True, spacing=4, auto_scroll=True, height=200)

    def add_log(msg: str):
        now = datetime.now().strftime("%H:%M:%S")
        logs_list.controls.append(ft.Text(f"[{now}] {msg}", size=12, color="#E2E8F0", font_family="monospace"))
        if len(logs_list.controls) > 100:
            logs_list.controls.pop(0)
        page.update()

    engine = SenatorCoreEngine(log_callback=add_log)
    await engine.init_client()

    status_badge = ft.Container(
        content=ft.Text("رادار: آماده", size=12, color="#FFFFFF"),
        bgcolor="#334155",
        padding=ft.padding.symmetric(horizontal=8, vertical=4),
        border_radius=6,
    )

    fleet_dropdown = ft.Dropdown(
        label="انتخاب ناوگان آفلاین",
        options=[ft.dropdown.Option(key=str(i), text=item["title"]) for i, item in enumerate(fleet_data)],
        value="0" if fleet_data else None,
        border_color="#38BDF8",
    )

    cargo_input = ft.TextField(label="نوع محموله", value="مصالح ساختمانی", border_color="#475569")
    weight_input = ft.TextField(label="وزن (کیلوگرم)", value="10000", border_color="#475569")
    origin_input = ft.TextField(label="مبدا", value="بندر لنگه", border_color="#475569")
    dest_input = ft.TextField(label="مقصد", value="شهرک صنعتی", border_color="#475569")
    workers_slider = ft.Slider(min=1, max=5, divisions=4, value=3, label="{value} خط")

    result_banner = ft.Container(
        content=ft.Text("آماده شلیک...", size=13, weight=ft.FontWeight.BOLD, color="#F8FAFC"),
        bgcolor="#1E293B",
        padding=10,
        border_radius=8,
    )

    async def start_burst_click(e):
        if not fleet_data or fleet_dropdown.value is None:
            result_banner.content.value = "ابتدا یک کامیون انتخاب کنید!"
            page.update()
            return
        selected = fleet_data[int(fleet_dropdown.value)]
        result_banner.content.value = "در حال شلیک رگباری..."
        page.update()
        ok, msg = await engine.burst_issue_permit(
            selected, cargo_input.value, weight_input.value, origin_input.value, dest_input.value, int(workers_slider.value)
        )
        result_banner.bgcolor = "#10B981" if ok else "#EF4444"
        result_banner.content.value = msg
        page.update()

    async def radar_loop():
        while engine.radar_active:
            is_up, ping, _ = await engine.check_server_radar()
            status_badge.bgcolor = "#10B981" if is_up else "#EF4444"
            status_badge.content.value = f"سرور: {'آنلاین' if is_up else 'قطع'} ({ping}ms)"
            page.update()
            await asyncio.sleep(4.0)

    def toggle_radar(e):
        engine.radar_active = e.control.value
        if engine.radar_active:
            page.run_task(radar_loop)
        page.update()

    tab_issue = ft.Column([
        ft.Switch(label="روشن کردن رادار زنده", value=False, on_change=toggle_radar),
        fleet_dropdown,
        cargo_input,
        weight_input,
        origin_input,
        dest_input,
        workers_slider,
        result_banner,
        ft.ElevatedButton("🔥 شروع شلیک رگباری", bgcolor="#F59E0B", color="#0F172A", height=45, on_click=start_burst_click),
    ])

    user_input = ft.TextField(label="نام کاربری سامانه", border_color="#475569")
    pass_input = ft.TextField(label="رمز عبور", password=True, border_color="#475569")
    captcha_img = ft.Image(src_base64="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=", width=150, height=50)
    captcha_input = ft.TextField(label="کد کپچا", border_color="#38BDF8", expand=True)

    async def load_cap(e):
        b64 = await engine.fetch_captcha_base64()
        if b64:
            captcha_img.src_base64 = b64
            page.update()

    async def do_login(e):
        await engine.perform_login(user_input.value, pass_input.value, captcha_input.value)
        page.update()

    tab_session = ft.Column([
        user_input, pass_input,
        ft.Row([captcha_img, ft.ElevatedButton("دریافت کپچا", on_click=load_cap)]),
        captcha_input,
        ft.ElevatedButton("🔐 ورود و قفل نشست", bgcolor="#10B981", color="#FFFFFF", on_click=do_login),
    ])

    body = ft.Container(content=tab_issue, padding=8)

    def switch_tab(e):
        body.content = tab_issue if e.control.data == "issue" else tab_session
        page.update()

    page.add(
        ft.Row([ft.Text("⚡ سناتور باربرگ", size=16, weight=ft.FontWeight.BOLD, color="#FFFFFF"), status_badge], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Row([ft.ElevatedButton("🚀 صدور", data="issue", on_click=switch_tab), ft.ElevatedButton("🔑 نشست", data="session", on_click=switch_tab)], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
        body,
        ft.Divider(),
        ft.Container(content=logs_list, bgcolor="#020617", padding=6, border_radius=6),
    )

ft.app(target=main)
