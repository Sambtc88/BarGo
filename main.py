import random
import time
import traceback
import flet as ft

try:
  from engine import (
      BarbargEngine,
      build_iran_plate,
      latlon_to_tile,
      tile_to_latlon,
      to_fa,
  )
except Exception:
  BarbargEngine = None
  ENGINE_ERR = traceback.format_exc()


def main(page: ft.Page):
  page.title = "بارگو بندر"
  page.rtl = True
  page.bgcolor = "#f1f5f9"
  page.padding = 0

  if BarbargEngine is None:
    page.add(
        ft.Container(
            padding=20,
            content=ft.Text(
                f"خطا در engine.py:\n{ENGINE_ERR}",
                color="red",
                selectable=True,
            ),
        )
    )
    return

  engine = BarbargEngine()
  current_user = engine.data["clients"][0]
  active_tab = "کاربران"
  barbarg_grp = None
  amen_sub = None
  body_holder = ft.Container(expand=True, padding=10)
  ai_badge_Text = ft.Text("۳ هشدار", size=10, color="white", weight="bold")

  # پاپ‌آپ استاندارد وضعیت و هشدار قرمز/سبز
  def show_popup(title, msg, is_err=False):
    bg = "#fee2e2" if is_err else "#dcfce7"
    col = "#991b1b" if is_err else "#166534"
    ic = ft.icons.WARNING_AMBER_ROUNDED if is_err else ft.icons.CHECK_CIRCLE
    dlg = ft.AlertDialog(
        modal=True,
        content_padding=0,
        content=ft.Container(
            width=335,
            bgcolor=bg,
            border_radius=16,
            border=ft.border.all(2, "#ef4444" if is_err else "#22c55e"),
            padding=14,
            content=ft.Column(
                tight=True,
                spacing=10,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=6,
                                controls=[
                                    ft.Icon(ic, color=col, size=22),
                                    ft.Text(
                                        title,
                                        size=14,
                                        weight="bold",
                                        color=col,
                                    ),
                                ],
                            ),
                            ft.Text(
                                to_fa(time.strftime("%H:%M:%S")),
                                size=11,
                                color="#334155",
                            ),
                        ],
                    ),
                    ft.Container(
                        bgcolor="white",
                        padding=12,
                        border_radius=10,
                        width=305,
                        content=ft.Text(
                            msg,
                            size=12,
                            color="#0f172a",
                            weight="bold",
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ),
                    ft.ElevatedButton(
                        "متوجه شدم ←",
                        bgcolor="#0f172a" if is_err else "white",
                        color="white" if is_err else "#0f172a",
                        width=305,
                        on_click=lambda e: setattr(dlg, "open", False)
                        or page.update(),
                    ),
                ],
            ),
        ),
    )
    page.dialog = dlg
    dlg.open = True
    page.update()

  # ==================== ۱. صفحه ورود (Login) ====================
  def build_login():
    tf_u = ft.TextField(
        hint_text="نام کاربری",
        value="Davood",
        bgcolor="#f1f5f9",
        border_radius=10,
    )
    tf_p = ft.TextField(
        hint_text="کلمه عبور",
        value="1234",
        password=True,
        can_reveal_password=True,
        bgcolor="#f1f5f9",
        border_radius=10,
    )
    err = ft.Text("", color="#dc2626", size=12, weight="bold")

    def do_log(e):
      ok, c = engine.authenticate(tf_u.value, tf_p.value)
      if ok:
        nonlocal current_user
        current_user = c
        build_scaffold()
      else:
        err.value = "نام کاربری یا کلمه عبور اشتباه است!"
        page.update()

    return ft.View(
        route="/login",
        bgcolor="#0f172a",
        padding=24,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                width=340,
                padding=22,
                bgcolor="white",
                border_radius=20,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                    controls=[
                        ft.Container(
                            width=68,
                            height=68,
                            bgcolor="#0f172a",
                            border_radius=18,
                            alignment=ft.alignment.center,
                            content=ft.Icon(
                                ft.icons.LOCAL_SHIPPING_ROUNDED,
                                color="#38bdf8",
                                size=38,
                            ),
                        ),
                        ft.Text(
                            "بارگو بندر",
                            size=24,
                            weight="bold",
                            color="#0f172a",
                        ),
                        ft.Text(
                            "سامانه هوشمند باربرگ و پایش ناوگان",
                            size=11,
                            color="#64748b",
                        ),
                        tf_u,
                        tf_p,
                        ft.Container(
                            padding=10,
                            bgcolor="#f0fdf4",
                            border=ft.border.all(1.5, "#86efac"),
                            border_radius=10,
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(
                                        "✓ من ربات نیستم (تأیید هوشمند)",
                                        size=11,
                                        weight="bold",
                                        color="#166534",
                                    ),
                                    ft.Icon(
                                        ft.icons.VERIFIED_USER,
                                        color="#0284c7",
                                        size=18,
                                    ),
                                ],
                            ),
                        ),
                        err,
                        ft.ElevatedButton(
                            "ورود به پنل بارگو بندر",
                            bgcolor="#0284c7",
                            color="white",
                            width=300,
                            height=45,
                            on_click=do_log,
                        ),
                    ],
                ),
            )
        ],
    )

  # ==================== ۲. پنجره لاگین زنده کپچا به درگاه barname.utcms.ir ====================
  def open_live_portal_captcha_modal(drv, after_op="issue"):
    st_lbl = ft.Text(
        "⏳ در حال دریافت تصویر کپچای زنده از barname.utcms.ir ...",
        size=11,
        color="#0369a1",
        weight="bold",
    )
    img_box = ft.Container(
        height=60,
        width=180,
        bgcolor="#f1f5f9",
        border_radius=8,
        alignment=ft.alignment.center,
        content=ft.Text("در حال بارگذاری کپچا...", size=10),
    )
    tf_cap = ft.TextField(
        label="کد کپچای تصویر (یا تشخیص خودکار AI)",
        text_size=13,
        height=44,
    )
    tf_api = ft.TextField(
        label="کلید Gemini AI (اختیاری - برای حل خودکار کپچا)",
        value=engine.data["settings"].get("gemini_api_key", ""),
        text_size=11,
        height=40,
    )

    def refresh_cap(e=None):
      engine.data["settings"]["gemini_api_key"] = tf_api.value.strip()
      engine.save_data()
      info = engine.fetch_login_page_and_captcha(drv)
      st_lbl.value = info["msg"]
      st_lbl.color = "#16a34a" if info["ok"] else "#dc2626"
      if info["captcha_b64"]:
        img_box.content = ft.Image(
            src_base64=info["captcha_b64"],
            width=170,
            height=55,
            fit=ft.ImageFit.CONTAIN,
        )
      else:
        img_box.content = ft.Text(
            "کپچا دریافت نشد (محدودیت شبکه)", size=10, color="#dc2626"
        )
      if info["auto_captcha"]:
        tf_cap.value = info["auto_captcha"]
        st_lbl.value += f" | حل خودکار AI: {info['auto_captcha']}"
      page.update()

    def do_submit_portal(e):
      st_lbl.value = "🚀 در حال ارسال لاگین و ثبت باربرگ در درگاه utcms.ir ..."
      page.update()
      ok_l, msg_l = engine.submit_real_portal_login(drv, tf_cap.value.strip())
      if ok_l:
        ok_op, msg_op = engine.execute_portal_operation(
            drv, after_op, tf_cap.value.strip()
        )
        dlg.open = False
        render_tab()
        show_popup("ثبت واقعی در درگاه", msg_op, is_err=not ok_op)
      else:
        st_lbl.value = msg_l
        st_lbl.color = "#dc2626"
        page.update()

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(
            f"🔐 اتصال زنده به درگاه: {drv['name']}", size=14, weight="bold"
        ),
        content=ft.Container(
            width=340,
            height=290,
            content=ft.Column(
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    st_lbl,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            img_box,
                            ft.IconButton(
                                icon=ft.icons.REFRESH,
                                icon_color="#0284c7",
                                tooltip="دریافت مجدد کپچا",
                                on_click=refresh_cap,
                            ),
                        ],
                    ),
                    tf_cap,
                    tf_api,
                ],
            ),
        ),
        actions=[
            ft.ElevatedButton(
                "ارسال به سایت و اجرای عملیات",
                bgcolor="#16a34a",
                color="white",
                on_click=do_submit_portal,
            ),
            ft.OutlinedButton(
                "بستن",
                on_click=lambda e: setattr(dlg, "open", False)
                or page.update(),
            ),
        ],
    )
    page.dialog = dlg
    dlg.open = True
    page.update()
    refresh_cap()

  # ==================== ۳. پنجره کلید 🔑 کد پیامکی (OTP دستی + تشخیص خودکار AI) ====================
  def open_otp_key_modal(drv):
    tf_otp = ft.TextField(
        label="کد تایید پیامکی (OTP)",
        value=drv.get("otp_code", ""),
        hint_text="مثال: 48291",
        text_size=15,
        text_align=ft.TextAlign.CENTER,
    )
    ai_status = ft.Text(
        "🤖 هوش مصنوعی آماده خواندن خودکار کد پیامک راننده است.",
        size=11,
        color="#0284c7",
        weight="bold",
    )

    def auto_ai_otp(e):
      ai_status.value = "⏳ در حال پایش پیامک‌های دریافتی و استخراج کد با AI..."
      page.update()
      ok, code = engine.auto_detect_otp_code(drv)
      tf_otp.value = code
      ai_status.value = f"✅ کد پیامکی «{to_fa(code)}» به صورت خودکار تشخیص و جایگذاری شد!"
      ai_status.color = "#16a34a"
      render_tab()
      page.update()

    def save_manual_otp(e):
      drv["otp_code"] = tf_otp.value.strip()
      drv["otp_needed"] = not bool(drv["otp_code"])
      drv["state_text"] = (
          f"کد {to_fa(drv['otp_code'])} ثبت شد (آماده صدور)"
          if drv["otp_code"]
          else "نیاز به کد پیامکی"
      )
      engine.save_data()
      dlg.open = False
      render_tab()
      show_popup(
          "ثبت کد پیامکی",
          f"کد تایید {to_fa(drv['otp_code'])} برای «{drv['name']}» فعال شد.",
      )

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            spacing=6,
            controls=[
                ft.Icon(ft.icons.VPN_KEY_ROUNDED, color="#d97706", size=22),
                ft.Text(
                    f"مدیریت کد پیامکی: {drv['name']}",
                    size=14,
                    weight="bold",
                ),
            ],
        ),
        content=ft.Container(
            width=330,
            height=210,
            content=ft.Column(
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    build_iran_plate(
                        drv["plate_left"],
                        drv["plate_letter"],
                        drv["plate_mid"],
                        drv["plate_iran"],
                        True,
                    ),
                    tf_otp,
                    ft.ElevatedButton(
                        "🤖 تشخیص و ثبت اتوماتیک کد با هوش مصنوعی",
                        bgcolor="#7c3aed",
                        color="white",
                        width=300,
                        on_click=auto_ai_otp,
                    ),
                    ai_status,
                ],
            ),
        ),
        actions=[
            ft.ElevatedButton(
                "ثبت کد و ادامه صدور",
                bgcolor="#16a34a",
                color="white",
                on_click=save_manual_otp,
            ),
            ft.OutlinedButton(
                "انصراف",
                on_click=lambda e: setattr(dlg, "open", False)
                or page.update(),
            ),
        ],
    )
    page.dialog = dlg
    dlg.open = True
    page.update()

  # ==================== ۴. پنجره ویرایش پیشرفته + نقشه واقعی ماهواره‌ای/خیابانی اسکرول‌شونده + بخش متحول‌شده بار ====================
  def open_edit_modal(drv):
    tf_nid = ft.TextField(
        label="کد ملی", value=drv["national_id"], text_size=12, expand=True
    )
    tf_pw = ft.TextField(
        label="رمز سامانه", value=drv["password"], text_size=12, expand=True
    )
    dd_grp = ft.Dropdown(
        label="گروه",
        value=str(drv["group"]),
        width=85,
        options=[
            ft.dropdown.Option("1", "گروه ۱"),
            ft.dropdown.Option("2", "گروه ۲"),
        ],
    )
    tf_mob = ft.TextField(
        label="موبایل", value=drv["mobile"], text_size=12, expand=True
    )
    tf_pl_l = ft.TextField(label="دو رقم", value=drv["plate_left"], width=62)
    tf_pl_c = ft.TextField(label="حرف", value=drv["plate_letter"], width=50)
    tf_pl_m = ft.TextField(label="سه رقم", value=drv["plate_mid"], width=72)
    tf_pl_i = ft.TextField(label="ایران", value=drv["plate_iran"], width=62)

    # وضعیت نقشه کاشی زنده (Satellite / OSM) با قابلیت اسکرول و زوم
    map_state = {
        "lat": float(drv.get("origin_lat", 26.5579)),
        "lon": float(drv.get("origin_lon", 54.8807)),
        "zoom": 13,
        "layer": "sat",  # sat | osm | street
        "target": "origin",
    }

    tf_olat = ft.TextField(
        label="عرض مبدأ",
        value=str(drv["origin_lat"]),
        text_size=11,
        expand=True,
    )
    tf_olon = ft.TextField(
        label="طول مبدأ",
        value=str(drv["origin_lon"]),
        text_size=11,
        expand=True,
    )
    tf_dlat = ft.TextField(
        label="عرض مقصد", value=str(drv["dest_lat"]), text_size=11, expand=True
    )
    tf_dlon = ft.TextField(
        label="طول مقصد", value=str(drv["dest_lon"]), text_size=11, expand=True
    )
    tf_orig_city = ft.TextField(
        label="شهر مبدأ",
        value=drv.get("origin_name", "بندر لنگه"),
        text_size=11,
        expand=True,
    )
    tf_dest_city = ft.TextField(
        label="شهر مقصد",
        value=drv.get("dest_name", "بندر کنگ"),
        text_size=11,
        expand=True,
    )

    tiles_grid = ft.Column(spacing=0)
    pin_orig = ft.Container(
        left=85,
        top=95,
        bgcolor="#dc2626",
        padding=ft.padding.symmetric(horizontal=6, vertical=2),
        border_radius=6,
        content=ft.Text("📍 مبدأ", color="white", size=9, weight="bold"),
    )
    pin_dest = ft.Container(
        left=210,
        top=55,
        bgcolor="#0f172a",
        padding=ft.padding.symmetric(horizontal=6, vertical=2),
        border_radius=6,
        content=ft.Text("🏁 مقصد", color="white", size=9, weight="bold"),
    )
    dist_badge = ft.Text(
        f"مسافت: {to_fa(drv['distance_km'])} km",
        color="white",
        size=10,
        weight="bold",
    )

    def get_tile_url(x, y, z, layer):
      if layer == "sat":
        return f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
      elif layer == "street":
        return f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}"
      return f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"

    def refresh_map_tiles():
      cx, cy = latlon_to_tile(
          map_state["lat"], map_state["lon"], map_state["zoom"]
      )
      z = map_state["zoom"]
      ly = map_state["layer"]
      rows_t = []
      for dy in (-1, 0):
        r_imgs = []
        for dx in (-1, 0, 1):
          u = get_tile_url(cx + dx, cy + dy, z, ly)
          r_imgs.append(
              ft.Image(
                  src=u, width=114, height=95, fit=ft.ImageFit.COVER
              )
          )
        rows_t.append(ft.Row(spacing=0, controls=r_imgs))
      tiles_grid.controls = rows_t

    refresh_map_tiles()

    def pan_map(dlat, dlon, dz=0):
      map_state["lat"] = round(map_state["lat"] + dlat, 6)
      map_state["lon"] = round(map_state["lon"] + dlon, 6)
      map_state["zoom"] = max(6, min(17, map_state["zoom"] + dz))
      refresh_map_tiles()
      page.update()

    def on_map_click(ev: ft.TapEvent):
      lx = max(10, min(320, int(ev.local_x)))
      ly = max(10, min(165, int(ev.local_y)))
      offset_lat = (95.0 - ly) * (0.04 / (2 ** (map_state["zoom"] - 11)))
      offset_lon = (lx - 170.0) * (0.04 / (2 ** (map_state["zoom"] - 11)))
      clicked_lat = round(map_state["lat"] + offset_lat, 6)
      clicked_lon = round(map_state["lon"] + offset_lon, 6)

      if map_state["target"] == "origin":
        pin_orig.left, pin_orig.top = lx - 18, ly - 12
        tf_olat.value, tf_olon.value = str(clicked_lat), str(clicked_lon)
      else:
        pin_dest.left, pin_dest.top = lx - 18, ly - 12
        tf_dlat.value, tf_dlon.value = str(clicked_lat), str(clicked_lon)

      try:
        km = engine.calculate_distance(
            float(tf_olat.value),
            float(tf_olon.value),
            float(tf_dlat.value),
            float(tf_dlon.value),
        )
        drv["distance_km"] = km
        dist_badge.value = f"مسافت: {to_fa(km)} km"
      except Exception:
        pass
      page.update()

    map_Interactive_stack = ft.Container(
        width=342,
        height=190,
        bgcolor="#0f172a",
        border_radius=12,
        border=ft.border.all(2, "#0284c7"),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.GestureDetector(
            on_tap_down=on_map_click,
            content=ft.Stack(
                width=342,
                height=190,
                controls=[
                    tiles_grid,
                    pin_orig,
                    pin_dest,
                    # نشانگر مسافت در بالای نقشه
                    ft.Container(
                        left=10,
                        top=8,
                        bgcolor="#0284c7",
                        padding=ft.padding.symmetric(
                            horizontal=10, vertical=4
                        ),
                        border_radius=8,
                        content=dist_badge,
                    ),
                    # دکمه‌های اسکرول (جهت‌نما) و زوم زنده روی نقشه
                    ft.Container(
                        right=6,
                        bottom=6,
                        bgcolor="#0f172a",
                        border_radius=8,
                        padding=2,
                        content=ft.Row(
                            spacing=0,
                            controls=[
                                ft.IconButton(
                                    icon=ft.icons.ARROW_FORWARD,
                                    icon_color="white",
                                    icon_size=16,
                                    on_click=lambda e: pan_map(0, 0.015),
                                ),
                                ft.IconButton(
                                    icon=ft.icons.ARROW_UPWARD,
                                    icon_color="white",
                                    icon_size=16,
                                    on_click=lambda e: pan_map(0.015, 0),
                                ),
                                ft.IconButton(
                                    icon=ft.icons.ARROW_DOWNWARD,
                                    icon_color="white",
                                    icon_size=16,
                                    on_click=lambda e: pan_map(-0.015, 0),
                                ),
                                ft.IconButton(
                                    icon=ft.icons.ARROW_BACK,
                                    icon_color="white",
                                    icon_size=16,
                                    on_click=lambda e: pan_map(0, -0.015),
                                ),
                                ft.IconButton(
                                    icon=ft.icons.ADD_CIRCLE_OUTLINE,
                                    icon_color="#38bdf8",
                                    icon_size=16,
                                    on_click=lambda e: pan_map(0, 0, 1),
                                ),
                                ft.IconButton(
                                    icon=ft.icons.REMOVE_CIRCLE_OUTLINE,
                                    icon_color="#f43f5e",
                                    icon_size=16,
                                    on_click=lambda e: pan_map(0, 0, -1),
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        ),
    )

    # بخش متحول‌شده و زیبای انتخاب بار، نوع بسته‌بندی، تناژ و کرایه هوشمند
    tf_cargo = ft.TextField(
        label="نام کالا / نوع بار",
        value=drv["cargo"],
        text_size=12,
        expand=True,
    )
    dd_pack = ft.Dropdown(
        label="بسته‌بندی",
        value=drv["pack"],
        expand=True,
        options=[
            ft.dropdown.Option(p, p)
            for p in [
                "گونی",
                "کیسه",
                "فله",
                "پالت",
                "کارتن",
                "جعبه",
                "جامبو",
                "بشکه",
                "رول",
                "عدل",
                "شاخه",
            ]
        ],
    )
    tf_weight = ft.TextField(
        label="وزن بار (تن)", value=drv["weight"], width=85, text_size=12
    )
    tf_count = ft.TextField(
        label="تعداد", value=drv.get("count", "1"), width=75, text_size=12
    )
    tf_value = ft.TextField(
        label="ارزش بار (ریال)",
        value=drv.get("value", "25000000"),
        text_size=12,
        expand=True,
    )
    tf_fare = ft.TextField(
        label="کرایه حمل (ریال)", value=drv["fare"], text_size=12, expand=True
    )

    cargo_presets = [
        ("🪨 ماسه", "ماسه", "فله", "5", "15000000"),
        ("🧱 سیمان", "سیمان", "کیسه", "5", "18000000"),
        ("⬜ گچ", "گچ", "گونی", "4", "16000000"),
        ("🏗️ بلوک", "بلوک", "پالت", "4", "17500000"),
        ("🐟 مواد دریایی", "مواد دریایی", "جعبه", "3", "26000000"),
        ("🥫 مواد غذایی", "مواد غذایی", "کارتن", "4", "22000000"),
        ("⛏️ مواد معدنی", "مواد معدنی", "جامبو", "6", "24000000"),
        ("🪵 چوب و تیرچه", "تیرچه", "شاخه", "5", "19500000"),
    ]

    def select_preset_cargo(c_name, p_name, w_val, f_val):
      tf_cargo.value = c_name
      dd_pack.value = p_name
      tf_weight.value = w_val
      tf_fare.value = f_val
      page.update()

    cargo_chips = ft.Row(
        wrap=True,
        spacing=5,
        run_spacing=5,
        controls=[
            ft.Container(
                bgcolor="#e0f2fe",
                border=ft.border.all(1, "#38bdf8"),
                border_radius=8,
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                on_click=lambda ev, cn=cn, pn=pn, wv=wv, fv=fv: (
                    select_preset_cargo(cn, pn, wv, fv)
                ),
                content=ft.Text(
                    lbl, size=10, weight="bold", color="#0369a1"
                ),
            )
            for lbl, cn, pn, wv, fv in cargo_presets
        ],
    )

    def save_u(e):
      drv["national_id"] = tf_nid.value.strip()
      drv["password"] = tf_pw.value.strip()
      drv["group"] = int(dd_grp.value or 1)
      drv["mobile"] = tf_mob.value.strip()
      drv["plate_left"] = tf_pl_l.value.strip()
      drv["plate_letter"] = tf_pl_c.value.strip()
      drv["plate_mid"] = tf_pl_m.value.strip()
      drv["plate_iran"] = tf_pl_i.value.strip()
      drv["origin_name"] = tf_orig_city.value.strip()
      drv["dest_name"] = tf_dest_city.value.strip()
      try:
        drv["origin_lat"] = float(tf_olat.value)
        drv["origin_lon"] = float(tf_olon.value)
        drv["dest_lat"] = float(tf_dlat.value)
        drv["dest_lon"] = float(tf_dlon.value)
      except Exception:
        pass
      drv["cargo"] = tf_cargo.value.strip()
      drv["pack"] = dd_pack.value
      drv["weight"] = tf_weight.value.strip()
      drv["count"] = tf_count.value.strip()
      drv["value"] = tf_value.value.strip()
      drv["fare"] = tf_fare.value.strip()
      engine.save_data()
      dlg.open = False
      render_tab()

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(
            f"ویرایش کاربر و نقشه ماهواره‌ای: {drv['name']}",
            size=14,
            weight="bold",
        ),
        content=ft.Container(
            width=365,
            height=490,
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                spacing=8,
                controls=[
                    ft.Row([tf_nid, tf_pw]),
                    ft.Row([dd_grp, tf_mob]),
                    ft.Row([tf_pl_i, tf_pl_m, tf_pl_c, tf_pl_l]),
                    ft.Divider(),
                    ft.Text(
                        "🛰️ نقشه زنده ماهواره‌ای و خیابانی (با اسکرول و زوم):",
                        size=12,
                        weight="bold",
                        color="#0284c7",
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.ElevatedButton(
                                "🛰️ ماهواره‌ای",
                                bgcolor="#0f172a",
                                color="white",
                                height=28,
                                on_click=lambda e: (
                                    map_state.__setitem__("layer", "sat"),
                                    refresh_map_tiles(),
                                    page.update(),
                                ),
                            ),
                            ft.ElevatedButton(
                                "🗺️ خیابانی OSM",
                                bgcolor="#0284c7",
                                color="white",
                                height=28,
                                on_click=lambda e: (
                                    map_state.__setitem__("layer", "osm"),
                                    refresh_map_tiles(),
                                    page.update(),
                                ),
                            ),
                            ft.ElevatedButton(
                                "🛣️ بزرگراه Esri",
                                bgcolor="#0d9488",
                                color="white",
                                height=28,
                                on_click=lambda e: (
                                    map_state.__setitem__("layer", "street"),
                                    refresh_map_tiles(),
                                    page.update(),
                                ),
                            ),
                        ],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                        controls=[
                            ft.ElevatedButton(
                                "📍 کلیک بعدی = مبدأ",
                                bgcolor="#dc2626",
                                color="white",
                                height=28,
                                on_click=lambda e: map_state.__setitem__(
                                    "target", "origin"
                                ),
                            ),
                            ft.ElevatedButton(
                                "🏁 کلیک بعدی = مقصد",
                                bgcolor="#0f172a",
                                color="white",
                                height=28,
                                on_click=lambda e: map_state.__setitem__(
                                    "target", "dest"
                                ),
                            ),
                        ],
                    ),
                    map_Interactive_stack,
                    ft.Row([tf_orig_city, tf_dest_city]),
                    ft.Row([tf_olat, tf_olon]),
                    ft.Row([tf_dlat, tf_dlon]),
                    ft.Divider(),
                    ft.Container(
                        bgcolor="#f8fafc",
                        padding=10,
                        border_radius=12,
                        border=ft.border.all(1.5, "#bae6fd"),
                        content=ft.Column(
                            spacing=8,
                            controls=[
                                ft.Text(
                                    "📦 انتخاب سریع و هوشمند نوع بار و بسته‌بندی:",
                                    size=12,
                                    weight="bold",
                                    color="#0369a1",
                                ),
                                cargo_chips,
                                ft.Row([tf_cargo, dd_pack]),
                                ft.Row([tf_weight, tf_count]),
                                ft.Row([tf_value, tf_fare]),
                            ],
                        ),
                    ),
                ],
            ),
        ),
        actions=[
            ft.ElevatedButton(
                "ذخیره تغییرات",
                bgcolor="#0284c7",
                color="white",
                on_click=save_u,
            ),
            ft.OutlinedButton(
                "انصراف",
                on_click=lambda e: setattr(dlg, "open", False)
                or page.update(),
            ),
        ],
    )
    page.dialog = dlg
    dlg.open = True
    page.update()

  # ==================== ۵. تنظیمات پیشرفته باربرگ (تغییر کدی / غیرکدی و فعال/غیرفعال کردن حمل) ====================
  def open_barbarg_settings_modal(g_num):
    rows_u = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, height=300)
    g_list = [
        d
        for d in engine.data["drivers"]
        if (g_num is None or d["group"] == g_num)
    ]

    for idx, drv in enumerate(g_list, start=1):

      def toggle_code_mode(ev, d=drv):
        d["code_mode"] = "بدون کد" if d.get("code_mode") == "کدی" else "کدی"
        d["otp_needed"] = d["code_mode"] == "کدی"
        engine.save_data()
        open_barbarg_settings_modal(g_num)
        render_tab()

      def toggle_trip_en(ev, d=drv):
        d["trip_enabled"] = ev.control.value
        engine.save_data()
        render_tab()

      is_code = drv.get("code_mode") == "کدی"
      rows_u.controls.append(
          ft.Container(
              bgcolor="#f8fafc",
              padding=8,
              border_radius=10,
              border=ft.border.all(1, "#cbd5e1"),
              content=ft.Row(
                  alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                  controls=[
                      ft.Column(
                          spacing=2,
                          controls=[
                              ft.Text(
                                  f"{to_fa(idx)}. {drv['name']}",
                                  size=12,
                                  weight="bold",
                              ),
                              ft.Text(
                                  f"پلاک: {to_fa(drv['plate_left'])}{drv['plate_letter']}{to_fa(drv['plate_mid'])}",
                                  size=10,
                                  color="#64748b",
                              ),
                          ],
                      ),
                      # دکمه تغییر کدی / غیرکدی
                      ft.ElevatedButton(
                          "🔑 کدی" if is_code else "🔓 بدون کد",
                          bgcolor="#fef3c7" if is_code else "#dcfce7",
                          color="#b45309" if is_code else "#15803d",
                          height=30,
                          on_click=toggle_code_mode,
                      ),
                      # سوییچ حمل فعال / غیرفعال
                      ft.Row(
                          spacing=2,
                          controls=[
                              ft.Text("حمل:", size=10, weight="bold"),
                              ft.Switch(
                                  value=drv.get("trip_enabled", True),
                                  active_color="#0284c7",
                                  on_change=toggle_trip_en,
                              ),
                          ],
                      ),
                  ],
              ),
          )
      )

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(
            "⚙️ تنظیمات پلاک‌ها (کدی/غیرکدی و وضعیت حمل)",
            size=14,
            weight="bold",
        ),
        content=ft.Container(
            width=360,
            height=350,
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Text(
                        "با زدن دکمه جلوی هر راننده، حالت «کدی / بدون کد» را"
                        " جابجا کنید و سوییچ «حمل» را فعال یا غیرفعال نمایید:",
                        size=11,
                        color="#475569",
                    ),
                    rows_u,
                ],
            ),
        ),
        actions=[
            ft.ElevatedButton(
                "ذخیره و بستن",
                bgcolor="#0284c7",
                color="white",
                on_click=lambda e: setattr(dlg, "open", False)
                or page.update(),
            )
        ],
    )
    page.dialog = dlg
    dlg.open = True
    page.update()

  # ==================== ۶. آنالیزور و پایشگر هوش مصنوعی (AI Analyzer) با هشدار قرمز ====================
  def open_ai_analyzer_modal(e=None):
    alerts = engine.run_ai_analyzer()
    danger_cnt = len([a for a in alerts if a["level"] == "danger"])
    ai_badge_Text.value = f"{to_fa(len(alerts))} هشدار"

    cards = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, height=310)
    for al in alerts:
      is_d = al["level"] == "danger"
      is_w = al["level"] == "warn"
      bg = "#fee2e2" if is_d else ("#fef9c3" if is_w else "#dcfce7")
      bd = "#ef4444" if is_d else ("#eab308" if is_w else "#22c55e")
      col = "#991b1b" if is_d else ("#854d0e" if is_w else "#166534")
      ic = (
          ft.icons.REPORT_GMAILERRORRED
          if is_d
          else (ft.icons.WARNING_AMBER if is_w else ft.icons.VERIFIED)
      )
      cards.controls.append(
          ft.Container(
              bgcolor=bg,
              padding=10,
              border_radius=10,
              border=ft.border.all(1.5, bd),
              content=ft.Row(
                  spacing=8,
                  controls=[
                      ft.Icon(ic, color=col, size=24),
                      ft.Column(
                          expand=True,
                          spacing=2,
                          controls=[
                              ft.Text(
                                  al["title"],
                                  size=12,
                                  weight="bold",
                                  color=col,
                              ),
                              ft.Text(
                                  al["desc"], size=10, color="#1e293b"
                              ),
                          ],
                      ),
                  ],
              ),
          )
      )

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            spacing=6,
            controls=[
                ft.Icon(ft.icons.PSYCHOLOGY, color="#dc2626", size=26),
                ft.Text(
                    f"رادار و آنالیزور هوشمند ({to_fa(danger_cnt)} اخطار مهم)",
                    size=14,
                    weight="bold",
                    color="#991b1b" if danger_cnt else "#0f172a",
                ),
            ],
        ),
        content=ft.Container(width=355, height=330, content=cards),
        actions=[
            ft.ElevatedButton(
                "رفع خودکار خطاهای OTP با AI",
                bgcolor="#dc2626",
                color="white",
                on_click=lambda ev: (
                    [
                        engine.auto_detect_otp_code(d)
                        for d in engine.data["drivers"]
                        if d.get("code_mode") == "کدی"
                    ],
                    setattr(dlg, "open", False),
                    render_tab(),
                    show_popup(
                        "تعمیر هوشمند انجام شد",
                        "کدهای پیامکی تمامی پلاک‌های کدی توسط هوش مصنوعی"
                        " بارگذاری و آماده صدور شدند.",
                    ),
                ),
            ),
            ft.OutlinedButton(
                "بستن",
                on_click=lambda ev: setattr(dlg, "open", False)
                or page.update(),
            ),
        ],
    )
    page.dialog = dlg
    dlg.open = True
    page.update()

  # ==================== ۷. تب‌های ۵ گانه برنامه ====================
  def build_users_tab():
    rows = ft.Column(spacing=6)
    rows.controls.append(
        ft.Container(
            bgcolor="#0f172a",
            padding=8,
            border_radius=8,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(
                        "ردیف",
                        size=11,
                        weight="bold",
                        color="white",
                        width=26,
                    ),
                    ft.Text(
                        "راننده / نوع بار",
                        size=11,
                        weight="bold",
                        color="white",
                        expand=True,
                    ),
                    ft.Text(
                        "پلاک",
                        size=11,
                        weight="bold",
                        color="white",
                        width=142,
                    ),
                    ft.Text(
                        "گروه",
                        size=11,
                        weight="bold",
                        color="white",
                        width=28,
                    ),
                    ft.Text(
                        "عملیات",
                        size=11,
                        weight="bold",
                        color="white",
                        width=56,
                    ),
                ],
            ),
        )
    )
    for idx, drv in enumerate(engine.data["drivers"], start=1):
      on = drv["active"]
      pill = ft.Container(
          width=52,
          height=22,
          bgcolor="#22c55e" if on else "#ef4444",
          border_radius=11,
          alignment=ft.alignment.center,
          on_click=lambda ev, d=drv: (
              setattr(d, "active", not d["active"]),
              engine.save_data(),
              render_tab(),
          ),
          content=ft.Text(
              "ON" if on else "OFF", color="white", size=9, weight="bold"
          ),
      )
      rows.controls.append(
          ft.Container(
              bgcolor="white" if on else "#fff1f2",
              padding=6,
              border_radius=10,
              border=ft.border.all(1, "#e2e8f0"),
              content=ft.Row(
                  alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                  controls=[
                      ft.Text(to_fa(idx), size=11, weight="bold", width=22),
                      ft.Column(
                          spacing=1,
                          expand=True,
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                          controls=[
                              ft.Text(drv["name"], size=12, weight="bold"),
                              ft.Text(
                                  to_fa(drv["national_id"]),
                                  size=10,
                                  color="#64748b",
                              ),
                              ft.Text(
                                  f"📦 {drv['cargo']} ({drv['pack']})",
                                  size=9,
                                  color="#0284c7",
                                  weight="bold",
                              ),
                          ],
                      ),
                      build_iran_plate(
                          drv["plate_left"],
                          drv["plate_letter"],
                          drv["plate_mid"],
                          drv["plate_iran"],
                          True,
                      ),
                      ft.Text(
                          to_fa(drv["group"]),
                          size=11,
                          weight="bold",
                          width=22,
                      ),
                      ft.Column(
                          spacing=3,
                          controls=[
                              pill,
                              ft.Container(
                                  width=52,
                                  height=22,
                                  bgcolor="#0284c7",
                                  border_radius=6,
                                  alignment=ft.alignment.center,
                                  on_click=lambda ev, d=drv: open_edit_modal(d),
                                  content=ft.Text(
                                      "ویرایش",
                                      color="white",
                                      size=9,
                                      weight="bold",
                                  ),
                              ),
                              ft.Container(
                                  width=52,
                                  height=20,
                                  bgcolor="#fef3c7",
                                  border_radius=6,
                                  alignment=ft.alignment.center,
                                  on_click=lambda ev, d=drv: (
                                      open_live_portal_captcha_modal(
                                          d, "issue"
                                      )
                                  ),
                                  content=ft.Text(
                                      "لاگین سایت",
                                      color="#b45309",
                                      size=8,
                                      weight="bold",
                                  ),
                              ),
                          ],
                      ),
                  ],
              ),
          )
      )
    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        controls=[
            ft.Container(
                bgcolor="white",
                padding=12,
                border_radius=14,
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(
                                    "مدیریت کاربران و ناوگان",
                                    size=16,
                                    weight="bold",
                                ),
                                ft.ElevatedButton(
                                    "⚙️ تنظیمات کدی / حمل",
                                    bgcolor="#6d28d9",
                                    color="white",
                                    height=32,
                                    on_click=lambda e: (
                                        open_barbarg_settings_modal(None)
                                    ),
                                ),
                            ],
                        ),
                        rows,
                    ],
                ),
            )
        ],
    )

  def build_amenities_tab():
    # ویجت فشرده آنالیزور هوش مصنوعی در بالای بخش امکانات
    ai_compact_banner = ft.Container(
        bgcolor="#1e1b4b",
        padding=12,
        border_radius=14,
        border=ft.border.all(1.5, "#ef4444"),
        on_click=open_ai_analyzer_modal,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Icon(
                            ft.icons.RADAR_ROUNDED, color="#f43f5e", size=28
                        ),
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text(
                                    "آنالیزور و پایشگر هوش مصنوعی (AI Analyzer)",
                                    size=12,
                                    weight="bold",
                                    color="white",
                                ),
                                ft.Text(
                                    "بررسی خودکار خطاهای پلاک، انقضای پروانه و"
                                    " وضعیت درگاه",
                                    size=10,
                                    color="#cbd5e1",
                                ),
                            ],
                        ),
                    ],
                ),
                ft.Container(
                    bgcolor="#ef4444",
                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                    border_radius=10,
                    content=ai_badge_Text,
                ),
            ],
        ),
    )

    items = [
        (
            "شروع و پایان حمل",
            ft.icons.LOCAL_SHIPPING,
            "#0284c7",
            lambda: switch_tab("باربرگ"),
        ),
        (
            "تعیین نوع بار و کالا",
            ft.icons.INVENTORY_2,
            "#16a34a",
            lambda: open_edit_modal(engine.data["drivers"][0]),
        ),
        (
            "نقشه ماهواره‌ای زنده",
            ft.icons.SATELLITE_ALT,
            "#0d9488",
            lambda: open_edit_modal(engine.data["drivers"][0]),
        ),
        (
            "تنظیمات کدی / غیرکدی",
            ft.icons.VPN_KEY,
            "#d97706",
            lambda: open_barbarg_settings_modal(None),
        ),
        (
            "لاگین زنده با کپچا",
            ft.icons.SECURITY,
            "#7c3aed",
            lambda: open_live_portal_captcha_modal(
                engine.data["drivers"][0], "issue"
            ),
        ),
        (
            "آنالیزور هوشمند AI",
            ft.icons.PSYCHOLOGY,
            "#dc2626",
            open_ai_analyzer_modal,
        ),
    ]
    grid = ft.GridView(
        expand=False, runs_count=3, max_extent=125, spacing=8, run_spacing=8
    )
    for t, ic, col, fn in items:
      grid.controls.append(
          ft.Container(
              bgcolor="white",
              padding=10,
              border_radius=12,
              border=ft.border.all(1, "#e2e8f0"),
              on_click=lambda ev, f=fn: f(),
              content=ft.Column(
                  alignment=ft.MainAxisAlignment.CENTER,
                  horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                  spacing=6,
                  controls=[
                      ft.Icon(ic, color=col, size=26),
                      ft.Text(
                          t,
                          size=11,
                          weight="bold",
                          text_align=ft.TextAlign.CENTER,
                      ),
                  ],
              ),
          )
      )
    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=10,
        controls=[
            ai_compact_banner,
            ft.Text("امکانات پیشرفته بارگو بندر", size=16, weight="bold"),
            grid,
        ],
    )

  # ==================== تب باربرگ (به همراه آیکون کلید 🔑 بغل اسم راننده، سوییچ حمل فعال/غیرفعال و تنظیمات گروه) ====================
  def build_barbarg_tab():
    nonlocal barbarg_grp
    if barbarg_grp is None:
      return ft.Column(
          scroll=ft.ScrollMode.AUTO,
          expand=True,
          controls=[
              ft.Container(
                  bgcolor="white",
                  padding=14,
                  border_radius=14,
                  content=ft.Column(
                      spacing=12,
                      controls=[
                          ft.Row(
                              alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                              controls=[
                                  ft.Text(
                                      "باربرگ (پنل اتوماسیون گروه‌ها)",
                                      size=16,
                                      weight="bold",
                                  ),
                                  ft.ElevatedButton(
                                      "⚙️ تنظیمات کدی و حمل",
                                      bgcolor="#ede9fe",
                                      color="#6d28d9",
                                      height=32,
                                      on_click=lambda e: (
                                          open_barbarg_settings_modal(None)
                                      ),
                                  ),
                              ],
                          ),
                          ft.Row(
                              spacing=10,
                              controls=[
                                  ft.Container(
                                      expand=True,
                                      bgcolor="#f8fafc",
                                      padding=16,
                                      border_radius=12,
                                      border=ft.border.all(2, "#0284c7"),
                                      on_click=lambda e: set_bgrp(1),
                                      content=ft.Column(
                                          horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                          controls=[
                                              ft.Text(
                                                  "● آماده صدور درگاه",
                                                  size=10,
                                                  color="#16a34a",
                                                  weight="bold",
                                              ),
                                              ft.Text(
                                                  "گروه ۱",
                                                  size=17,
                                                  weight="bold",
                                              ),
                                              ft.Text(
                                                  "ورود به گروه ←",
                                                  size=11,
                                                  color="#0284c7",
                                              ),
                                          ],
                                      ),
                                  ),
                                  ft.Container(
                                      expand=True,
                                      bgcolor="#f8fafc",
                                      padding=16,
                                      border_radius=12,
                                      border=ft.border.all(2, "#0284c7"),
                                      on_click=lambda e: set_bgrp(2),
                                      content=ft.Column(
                                          horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                          controls=[
                                              ft.Text(
                                                  "● آماده صدور درگاه",
                                                  size=10,
                                                  color="#16a34a",
                                                  weight="bold",
                                              ),
                                              ft.Text(
                                                  "گروه ۲",
                                                  size=17,
                                                  weight="bold",
                                              ),
                                              ft.Text(
                                                  "ورود به گروه ←",
                                                  size=11,
                                                  color="#0284c7",
                                              ),
                                          ],
                                      ),
                                  ),
                              ],
                          ),
                      ],
                  ),
              )
          ],
      )

    cards = ft.Column(spacing=8)
    g_drivers = [
        x for x in engine.data["drivers"] if x["group"] == barbarg_grp
    ]
    for idx, d in enumerate(g_drivers, 1):
      is_code = d.get("code_mode") == "کدی"
      has_otp = bool(d.get("otp_code"))
      trip_on = d.get("trip_enabled", True)

      # دکمه کلید 🔑 بغل اسم راننده (زرد/قرمز در صورت نیاز به کد، سبز در صورت ثبت شدن کد با AI)
      key_btn = ft.Container(
          bgcolor="#dcfce7"
          if has_otp
          else ("#fef3c7" if is_code else "#f1f5f9"),
          border=ft.border.all(
              1.5,
              "#16a34a" if has_otp else ("#f59e0b" if is_code else "#cbd5e1"),
          ),
          border_radius=8,
          padding=ft.padding.symmetric(horizontal=6, vertical=3),
          on_click=lambda ev, drv=d: open_otp_key_modal(drv),
          content=ft.Row(
              spacing=3,
              controls=[
                  ft.Icon(
                      ft.icons.VPN_KEY_ROUNDED,
                      size=14,
                      color="#15803d"
                      if has_otp
                      else ("#d97706" if is_code else "#64748b"),
                  ),
                  ft.Text(
                      to_fa(d["otp_code"])
                      if has_otp
                      else ("کد پیامک" if is_code else "بدون کد"),
                      size=9,
                      weight="bold",
                      color="#15803d"
                      if has_otp
                      else ("#b45309" if is_code else "#64748b"),
                  ),
              ],
          ),
      )

      # دکمه تغییر مستقیم وضعیت حمل فعال / غیرفعال جلوی پلاک
      trip_toggle_badge = ft.Container(
          bgcolor="#e0f2fe" if trip_on else "#fee2e2",
          border_radius=8,
          padding=ft.padding.symmetric(horizontal=7, vertical=4),
          on_click=lambda ev, drv=d: (
              setattr(drv, "trip_enabled", not drv.get("trip_enabled", True)),
              engine.save_data(),
              render_tab(),
          ),
          content=ft.Text(
              "🚚 حمل: فعال" if trip_on else "🚫 حمل: غیرفعال",
              size=9,
              weight="bold",
              color="#0369a1" if trip_on else "#dc2626",
          ),
      )

      cards.controls.append(
          ft.Container(
              bgcolor="white",
              padding=10,
              border_radius=12,
              border=ft.border.all(1, "#cbd5e1"),
              content=ft.Column(
                  spacing=6,
                  controls=[
                      ft.Row(
                          alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                          controls=[
                              ft.Row(
                                  spacing=6,
                                  controls=[
                                      ft.Text(
                                          f"{to_fa(idx)}. {d['name']}",
                                          size=12,
                                          weight="bold",
                                      ),
                                      key_btn,
                                  ],
                              ),
                              trip_toggle_badge,
                          ],
                      ),
                      ft.Row(
                          alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                          controls=[
                              ft.Row(
                                  spacing=4,
                                  controls=[
                                      ft.ElevatedButton(
                                          "صدور واقعی",
                                          bgcolor="#16a34a",
                                          color="white",
                                          height=28,
                                          on_click=lambda ev, drv=d: (
                                              open_live_portal_captcha_modal(
                                                  drv, "issue"
                                              )
                                          ),
                                      ),
                                      ft.ElevatedButton(
                                          "شروع/پایان",
                                          bgcolor="#0284c7",
                                          color="white",
                                          height=28,
                                          on_click=lambda ev, drv=d: show_popup(
                                              "وضعیت حمل",
                                              engine.execute_portal_operation(
                                                  drv, "start_trip"
                                              )[1],
                                              not drv.get(
                                                  "trip_enabled", True
                                              ),
                                          ),
                                      ),
                                  ],
                              ),
                              build_iran_plate(
                                  d["plate_left"],
                                  d["plate_letter"],
                                  d["plate_mid"],
                                  d["plate_iran"],
                                  True,
                              ),
                          ],
                      ),
                      ft.Text(
                          f"وضعیت: {d.get('state_text', 'آماده')} | بار:"
                          f" {d['cargo']} ({d['pack']})",
                          size=10,
                          color="#475569",
                      ),
                  ],
              ),
          )
      )

    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=8,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(
                        f"پنل باربرگ گروه {to_fa(barbarg_grp)}",
                        size=15,
                        weight="bold",
                    ),
                    ft.Row(
                        spacing=6,
                        controls=[
                            ft.ElevatedButton(
                                "⚙️ تنظیمات",
                                bgcolor="#ede9fe",
                                color="#6d28d9",
                                height=30,
                                on_click=lambda e: open_barbarg_settings_modal(
                                    barbarg_grp
                                ),
                            ),
                            ft.OutlinedButton(
                                "بازگشت",
                                height=30,
                                on_click=lambda e: set_bgrp(None),
                            ),
                        ],
                    ),
                ],
            ),
            cards,
        ],
    )

  def set_bgrp(g):
    nonlocal barbarg_grp
    barbarg_grp = g
    render_tab()

  def build_list_tab(mode):
    rows = ft.Column(spacing=8)
    for d in engine.data["drivers"]:
      sub_txt = (
          f"فعالیت: {d['fleet_lic_status']} | اشتغال:"
          f" {to_fa(d['driver_lic_days'])}"
          if mode == "license"
          else (
              f"اول: {to_fa(d['fuel_stage1'])} | دوم:"
              f" {to_fa(d['fuel_stage2'])}"
          )
      )

      def run_live_query(ev, drv=d):
        ok, msg = engine.execute_portal_operation(drv, mode)
        render_tab()
        show_popup("استعلام زنده از سایت utcms.ir", msg, is_err=not ok)

      rows.controls.append(
          ft.Container(
              bgcolor="white",
              padding=10,
              border_radius=12,
              border=ft.border.all(1, "#e2e8f0"),
              content=ft.Row(
                  alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                  controls=[
                      ft.Column([
                          ft.Text(d["name"], size=12, weight="bold"),
                          build_iran_plate(
                              d["plate_left"],
                              d["plate_letter"],
                              d["plate_mid"],
                              d["plate_iran"],
                              True,
                          ),
                      ]),
                      ft.Container(
                          width=115,
                          content=ft.Text(
                              sub_txt, size=10, weight="bold", color="#334155"
                          ),
                      ),
                      ft.Column(
                          spacing=4,
                          controls=[
                              ft.ElevatedButton(
                                  "استعلام سایت",
                                  bgcolor="#0284c7",
                                  color="white",
                                  height=28,
                                  on_click=run_live_query,
                              ),
                              ft.ElevatedButton(
                                  "لاگین کپچا",
                                  bgcolor="#fef3c7",
                                  color="#b45309",
                                  height=24,
                                  on_click=lambda ev, drv=d: (
                                      open_live_portal_captcha_modal(drv, mode)
                                  ),
                              ),
                          ],
                      ),
                  ],
              ),
          )
      )
    title_str = (
        "استعلام آنلاین پروانه فعالیت و اشتغال"
        if mode == "license"
        else "استعلام آنلاین سهمیه سوخت از سایت"
    )
    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=10,
        controls=[ft.Text(title_str, size=16, weight="bold"), rows],
    )

  # ==================== ۸. نوار پایین رنگی متمایز و هدر مشکی لوکس با خروج از اکانت ====================
  nav_items_meta = [
      ("کاربران", ft.icons.PEOPLE_ALT_ROUNDED, "#2563eb", "#dbeafe"),
      ("امکانات", ft.icons.WIDGETS_ROUNDED, "#9333ea", "#f3e8ff"),
      ("باربرگ", ft.icons.LOCAL_SHIPPING_ROUNDED, "#16a34a", "#dcfce7"),
      ("پروانه", ft.icons.VERIFIED_ROUNDED, "#ea580c", "#ffedd5"),
      ("سهمیه", ft.icons.LOCAL_GAS_STATION_ROUNDED, "#e11d48", "#ffe4e6"),
  ]
  colored_bottom_bar = ft.Container(
      bgcolor="white",
      padding=ft.padding.symmetric(horizontal=8, vertical=8),
      border=ft.border.only(top=ft.BorderSide(1.5, "#cbd5e1")),
  )

  def build_colored_nav():
    btns = []
    for name, ic, active_col, light_bg in nav_items_meta:
      is_sel = active_tab == name
      btns.append(
          ft.Container(
              expand=True,
              height=52,
              bgcolor=active_col if is_sel else light_bg,
              border_radius=12,
              border=ft.border.all(1.5, active_col),
              alignment=ft.alignment.center,
              on_click=lambda ev, tn=name: switch_tab(tn),
              content=ft.Column(
                  spacing=2,
                  alignment=ft.MainAxisAlignment.CENTER,
                  horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                  controls=[
                      ft.Icon(
                          ic,
                          color="white" if is_sel else active_col,
                          size=20,
                      ),
                      ft.Text(
                          name,
                          size=10,
                          weight="bold",
                          color="white" if is_sel else active_col,
                      ),
                  ],
              ),
          )
      )
    colored_bottom_bar.content = ft.Row(spacing=6, controls=btns)

  def render_tab():
    build_colored_nav()
    if active_tab == "کاربران":
      body_holder.content = build_users_tab()
    elif active_tab == "امکانات":
      body_holder.content = build_amenities_tab()
    elif active_tab == "باربرگ":
      body_holder.content = build_barbarg_tab()
    elif active_tab == "پروانه":
      body_holder.content = build_list_tab("license")
    elif active_tab == "سهمیه":
      body_holder.content = build_list_tab("fuel")
    page.update()

  def switch_tab(t_name):
    nonlocal active_tab
    active_tab = t_name
    render_tab()

  # پنجره پروفایل و خروج از حساب کاربری (با کلیک روی نام کاربری در کادر مشکی بالا)
  def open_account_logout_modal(e):
    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("حساب کاربری فعال", size=15, weight="bold"),
        content=ft.Container(
            width=300,
            height=130,
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Text(
                        f"👤 نام کاربر: {current_user['name']}",
                        size=13,
                        weight="bold",
                    ),
                    ft.Text(
                        f"📅 اعتبار باقی‌مانده: {to_fa(current_user['days_left'])} روز",
                        size=12,
                        color="#16a34a",
                        weight="bold",
                    ),
                    ft.Text(
                        f"🚛 ظرفیت پنل: {to_fa(current_user['plan_limit'])} پلاک",
                        size=12,
                    ),
                ],
            ),
        ),
        actions=[
            ft.ElevatedButton(
                "🚪 خروج از حساب کاربری",
                bgcolor="#dc2626",
                color="white",
                on_click=lambda ev: (
                    setattr(dlg, "open", False),
                    page.views.clear(),
                    page.views.append(build_login()),
                    page.update(),
                ),
            ),
            ft.OutlinedButton(
                "بستن",
                on_click=lambda ev: setattr(dlg, "open", False)
                or page.update(),
            ),
        ],
    )
    page.dialog = dlg
    dlg.open = True
    page.update()

  def build_scaffold():
    page.views.clear()
    # کادر بالای مشکی لوکس با فونت‌های سفید درخشان و قابلیت خروج با کلیک روی حساب کاربری
    top_bar = ft.Container(
        bgcolor="#090d16",
        padding=ft.padding.only(top=38, bottom=12, left=14, right=14),
        border=ft.border.only(bottom=ft.BorderSide(1.5, "#1e293b")),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Container(
                    bgcolor="#1e293b",
                    padding=ft.padding.symmetric(horizontal=10, vertical=6),
                    border_radius=10,
                    border=ft.border.all(1, "#38bdf8"),
                    on_click=open_account_logout_modal,
                    content=ft.Row(
                        spacing=6,
                        controls=[
                            ft.Icon(
                                ft.icons.ACCOUNT_CIRCLE,
                                color="white",
                                size=18,
                            ),
                            ft.Text(
                                f"{current_user['username']} ({to_fa(current_user['days_left'])} روز) ▾",
                                size=11,
                                weight="bold",
                                color="white",
                            ),
                        ],
                    ),
                ),
                ft.Text(
                    "بارگو بندر", size=18, weight="bold", color="white"
                ),
                ft.Row(
                    spacing=2,
                    controls=[
                        ft.IconButton(
                            icon=ft.icons.PSYCHOLOGY,
                            icon_color="#f43f5e",
                            tooltip="آنالیزور هوش مصنوعی",
                            on_click=open_ai_analyzer_modal,
                        ),
                        ft.IconButton(
                            icon=ft.icons.CLOUD_SYNC,
                            icon_color="#38bdf8",
                            tooltip="تست زنده درگاه",
                            on_click=lambda e: show_popup(
                                "وضعیت زنده درگاه utcms.ir",
                                engine.connect_utcms_session()["msg"],
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )

    page.views.append(
        ft.View(
            route="/app",
            bgcolor="#f1f5f9",
            padding=0,
            controls=[top_bar, body_holder, colored_bottom_bar],
        )
    )
    render_tab()

  page.views.append(build_login())
  page.update()


if __name__ == "__main__":
  ft.app(target=main)
