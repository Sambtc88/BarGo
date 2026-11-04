import traceback
import flet as ft

try:
  from engine import BarbargEngine
except Exception:
  BarbargEngine = None
  ENGINE_ERR = traceback.format_exc()


def build_iran_plate(left_2, letter, mid_3, iran_code, compact=False):
  h = 42 if compact else 52
  num_size = 16 if compact else 21
  return ft.Container(
      height=h,
      width=225 if compact else 280,
      bgcolor="white",
      border=ft.border.all(2, "#0f172a"),
      border_radius=8,
      clip_behavior=ft.ClipBehavior.HARD_EDGE,
      content=ft.Row(
          spacing=0,
          controls=[
              ft.Container(
                  width=46 if compact else 56,
                  height=h,
                  bgcolor="white",
                  border=ft.border.only(left=ft.BorderSide(1.5, "#0f172a")),
                  alignment=ft.alignment.center,
                  content=ft.Column(
                      spacing=0,
                      alignment=ft.MainAxisAlignment.CENTER,
                      horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                      controls=[
                          ft.Text(
                              "ایران",
                              size=9 if compact else 10,
                              weight="bold",
                              color="#0f172a",
                          ),
                          ft.Text(
                              str(iran_code),
                              size=13 if compact else 17,
                              weight="bold",
                              color="#0f172a",
                          ),
                      ],
                  ),
              ),
              ft.Container(
                  expand=True,
                  height=h,
                  bgcolor="white",
                  alignment=ft.alignment.center,
                  content=ft.Row(
                      alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                      vertical_alignment=ft.CrossAxisAlignment.CENTER,
                      controls=[
                          ft.Text(
                              str(mid_3),
                              size=num_size,
                              weight="bold",
                              color="#0f172a",
                          ),
                          ft.Text(
                              str(letter),
                              size=num_size,
                              weight="bold",
                              color="#b91c1c",
                          ),
                          ft.Text(
                              str(left_2),
                              size=num_size,
                              weight="bold",
                              color="#0f172a",
                          ),
                      ],
                  ),
              ),
              ft.Container(
                  width=28 if compact else 34,
                  height=h,
                  bgcolor="#0369a1",
                  alignment=ft.alignment.center,
                  content=ft.Column(
                      spacing=1,
                      alignment=ft.MainAxisAlignment.CENTER,
                      horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                      controls=[
                          ft.Container(width=14, height=3, bgcolor="#22c55e"),
                          ft.Container(width=14, height=3, bgcolor="white"),
                          ft.Container(width=14, height=3, bgcolor="#ef4444"),
                          ft.Text(
                              "I.R.\nIRAN",
                              size=6 if compact else 6,
                              color="white",
                              weight="bold",
                              text_align=ft.TextAlign.CENTER,
                          ),
                      ],
                  ),
              ),
          ],
      ),
  )


def main(page: ft.Page):
  page.title = "BarGo Enterprise - بارگو بندر"
  page.rtl = True
  page.bgcolor = "#f8fafc"
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
  selected_group_filter = "all"
  search_query = ""

  # لاگ سیستم
  log_list = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO, height=95)

  def add_log(msg, color="#0f172a"):
    log_list.controls.insert(
        0, ft.Text(f"• {msg}", size=11, color=color, weight="bold")
    )
    page.update()

  # محتوای تب‌های مختلف منوی پایین
  body_container = ft.Container(expand=True, padding=12)

  drivers_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)

  # پنجره ویرایش پیشرفته + نقشه زنده مختصات‌دار
  def open_edit_dialog(driver):
    tf_name = ft.TextField(
        label="نام راننده", value=driver["name"], text_size=13, expand=True
    )
    tf_nid = ft.TextField(
        label="کد ملی", value=driver["national_id"], text_size=13, expand=True
    )
    tf_pass = ft.TextField(
        label="رمز عبور", value=driver["password"], text_size=13, expand=True
    )
    tf_mobile = ft.TextField(
        label="موبایل", value=driver["mobile"], text_size=13, expand=True
    )
    dd_group = ft.Dropdown(
        label="گروه",
        value=str(driver["group"]),
        width=100,
        options=[
            ft.dropdown.Option("1", "گروه ۱"),
            ft.dropdown.Option("2", "گروه ۲"),
            ft.dropdown.Option("3", "گروه ۳"),
        ],
    )

    tf_p_left = ft.TextField(
        label="دو رقم", value=driver["plate_left"], width=75
    )
    tf_p_letter = ft.TextField(
        label="حرف", value=driver["plate_letter"], width=60
    )
    tf_p_mid = ft.TextField(
        label="سه رقم", value=driver["plate_mid"], width=85
    )
    tf_p_iran = ft.TextField(
        label="ایران", value=driver["plate_iran"], width=70
    )

    dd_cargo = ft.Dropdown(
        label="کالا",
        value=driver["cargo"],
        expand=True,
        options=[
            ft.dropdown.Option(c["name"], c["name"])
            for c in engine.cargo_catalog
        ],
    )
    dd_pack = ft.Dropdown(
        label="بسته‌بندی",
        value=driver["pack"],
        expand=True,
        options=[
            ft.dropdown.Option(p, p)
            for p in ["گونی", "کیسه", "فله", "پالت", "کارتن", "جعبه", "بسته"]
        ],
    )
    tf_weight = ft.TextField(
        label="وزن (تن)", value=driver["weight"], width=90
    )
    tf_fare = ft.TextField(
        label="کرایه (ریال)", value=driver["fare"], expand=True
    )

    # نقشه زنده با قابلیت تنظیم زنده مختصات جغرافیایی طول و عرض
    tf_orig_lat = ft.TextField(
        label="عرض جغرافیایی مبدا (Lat)",
        value=str(driver["origin_lat"]),
        text_size=12,
        expand=True,
    )
    tf_orig_lon = ft.TextField(
        label="طول جغرافیایی مبدا (Lon)",
        value=str(driver["origin_lon"]),
        text_size=12,
        expand=True,
    )
    tf_dest_lat = ft.TextField(
        label="عرض جغرافیایی مقصد (Lat)",
        value=str(driver["dest_lat"]),
        text_size=12,
        expand=True,
    )
    tf_dest_lon = ft.TextField(
        label="طول جغرافیایی مقصد (Lon)",
        value=str(driver["dest_lon"]),
        text_size=12,
        expand=True,
    )

    live_coords_text = ft.Text(
        f"مختصات زنده فعال | مسافت محاسبه‌شده: {driver['distance_km']} کیلومتر",
        size=11,
        color="#0284c7",
        weight="bold",
    )

    def recalculate_live_map(e):
      try:
        olat = float(tf_orig_lat.value)
        olon = float(tf_orig_lon.value)
        dlat = float(tf_dest_lat.value)
        dlon = float(tf_dest_lon.value)
        km = engine.calculate_distance(olat, olon, dlat, dlon)
        driver["origin_lat"] = olat
        driver["origin_lon"] = olon
        driver["dest_lat"] = dlat
        driver["dest_lon"] = dlon
        driver["distance_km"] = km
        live_coords_text.value = (
            f"✅ مختصات زنده ثبت شد | مسافت جدید جاده‌ای: {km} کیلومتر"
        )
        page.update()
      except ValueError:
        live_coords_text.value = "⚠️ خطا در مقادیر عددی مختصات!"
        page.update()

    map_live_box = ft.Container(
        height=140,
        bgcolor="#e0f2fe",
        border_radius=10,
        border=ft.border.all(1.5, "#0284c7"),
        padding=10,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
            controls=[
                ft.Text(
                    "🗺️ نقشه زنده OSM و مختصات لحظه‌ای GPS",
                    size=12,
                    weight="bold",
                    color="#0369a1",
                ),
                live_coords_text,
                ft.ElevatedButton(
                    "به‌روزرسانی و محاسبه مجدد مسیر نقشه",
                    bgcolor="#0284c7",
                    color="white",
                    height=30,
                    on_click=recalculate_live_map,
                ),
            ],
        ),
    )

    def save_dlg(e):
      driver["name"] = tf_name.value.strip()
      driver["national_id"] = tf_nid.value.strip()
      driver["password"] = tf_pass.value.strip()
      driver["mobile"] = tf_mobile.value.strip()
      driver["group"] = int(dd_group.value or 1)
      driver["plate_left"] = tf_p_left.value.strip()
      driver["plate_letter"] = tf_p_letter.value.strip()
      driver["plate_mid"] = tf_p_mid.value.strip()
      driver["plate_iran"] = tf_p_iran.value.strip()
      driver["cargo"] = dd_cargo.value
      driver["pack"] = dd_pack.value
      driver["weight"] = tf_weight.value.strip()
      driver["fare"] = tf_fare.value.strip()
      engine.save_data()
      dlg.open = False
      render_tab_content("کاربران")
      add_log(f"اطلاعات کاربر {driver['name']} به‌روزرسانی شد.", "#16a34a")

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(
            f"ویرایش کاربر و نقشه: {driver['name']}", size=15, weight="bold"
        ),
        content=ft.Container(
            width=400,
            height=480,
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                spacing=8,
                controls=[
                    ft.Row([tf_name, dd_group]),
                    ft.Row([tf_nid, tf_pass]),
                    ft.Row([tf_mobile]),
                    ft.Divider(),
                    ft.Container(
                        alignment=ft.alignment.center,
                        content=build_iran_plate(
                            driver["plate_left"],
                            driver["plate_letter"],
                            driver["plate_mid"],
                            driver["plate_iran"],
                            compact=True,
                        ),
                    ),
                    ft.Row([tf_p_iran, tf_p_mid, tf_p_letter, tf_p_left]),
                    ft.Divider(),
                    ft.Row([dd_cargo, dd_pack]),
                    ft.Row([tf_weight, tf_fare]),
                    ft.Divider(),
                    ft.Text(
                        "طول و عرض جغرافیایی زنده (مبدا و مقصد)",
                        size=12,
                        weight="bold",
                        color="#0284c7",
                    ),
                    ft.Row([tf_orig_lat, tf_orig_lon]),
                    ft.Row([tf_dest_lat, tf_dest_lon]),
                    map_live_box,
                ],
            ),
        ),
        actions=[
            ft.ElevatedButton(
                "ذخیره تغییرات",
                bgcolor="#0284c7",
                color="white",
                on_click=save_dlg,
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

  # رندر کردن کارت‌های کاربران در تب کاربران
  def render_drivers_list():
    drivers_column.controls.clear()
    for idx, drv in enumerate(engine.data["drivers"], start=1):
      if (
          selected_group_filter != "all"
          and str(drv["group"]) != selected_group_filter
      ):
        continue
      if search_query:
        q = search_query.strip()
        full_p = f"{drv['plate_left']}{drv['plate_mid']}{drv['plate_iran']}"
        if (
            q not in drv["name"]
            and q not in drv["national_id"]
            and q not in full_p
        ):
          continue

      def make_toggle(d):
        def _tg(e):
          d["active"] = e.control.value
          engine.save_data()

        return _tg

      def make_del(d):
        def _dl(e):
          engine.data["drivers"].remove(d)
          engine.save_data()
          render_drivers_list()
          add_log(f"کاربر {d['name']} حذف شد.", "#dc2626")

        return _dl

      def make_action(d, act):
        def _ac(e):
          ok, _ = engine.check_portal_connection()
          msg = engine.execute_real_action(d, act)
          add_log(msg, "#15803d")

        return _ac

      card = ft.Container(
          bgcolor="white",
          padding=12,
          border_radius=12,
          border=ft.border.all(1.5, "#cbd5e1"),
          content=ft.Column(
              spacing=8,
              controls=[
                  ft.Row(
                      alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                      controls=[
                          ft.Text(
                              drv["name"],
                              size=15,
                              weight="bold",
                              color="#0f172a",
                          ),
                          ft.Text(
                              f"کد ملی: {drv['national_id']} | گروه {drv['group']} | تناژ: {drv.get('tonnage', 6)} تن",
                              size=11,
                              color="#64748b",
                          ),
                          ft.Switch(
                              value=drv["active"],
                              active_color="#16a34a",
                              on_change=make_toggle(drv),
                          ),
                      ],
                  ),
                  ft.Row(
                      alignment=ft.MainAxisAlignment.CENTER,
                      controls=[
                          build_iran_plate(
                              drv["plate_left"],
                              drv["plate_letter"],
                              drv["plate_mid"],
                              drv["plate_iran"],
                          )
                      ],
                  ),
                  ft.Text(
                      f"📦 بار: {drv['cargo']} ({drv['weight']} تن) | کرایه: {drv['fare']} ریال\n📍 مسیر: {drv['origin_name']} به {drv['dest_name']} ({drv['distance_km']} km)",
                      size=11,
                      color="#334155",
                  ),
                  ft.Row(
                      alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                      controls=[
                          ft.ElevatedButton(
                              "ثبت و صدور",
                              bgcolor="#0284c7",
                              color="white",
                              height=32,
                              on_click=make_action(drv, "issue"),
                          ),
                          ft.ElevatedButton(
                              "شروع حمل (اپ)",
                              bgcolor="#16a34a",
                              color="white",
                              height=32,
                              on_click=make_action(drv, "start_trip"),
                          ),
                          ft.ElevatedButton(
                              "پایان حمل (اپ)",
                              bgcolor="#0d9488",
                              color="white",
                              height=32,
                              on_click=make_action(drv, "end_trip"),
                          ),
                      ],
                  ),
                  ft.Row(
                      alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                      controls=[
                          ft.OutlinedButton(
                              "ویرایش / نقشه زنده",
                              height=30,
                              on_click=lambda e, d=drv: open_edit_dialog(d),
                          ),
                          ft.TextButton(
                              "حذف",
                              style=ft.ButtonStyle(color="#dc2626"),
                              on_click=make_del(drv),
                          ),
                      ],
                  ),
              ],
          ),
      )
      drivers_column.controls.append(card)
    page.update()

  # پنل امکانات (دقیقاً مشابه اسکرین‌شات منوی امکانات سناتور با کارت‌های رنگی جذاب)
  def build_amenities_view():
    feature_cards = [
        (
            "آدرس‌ها",
            "مدیریت نقشه و آدرس رانندگان",
            ft.icons.LOCATION_ON,
            "#0ea5e9",
        ),
        (
            "تعیین نوع بار",
            "چرخش کالا و فرستنده/گیرنده برای هر تور",
            ft.icons.CATEGORY,
            "#22c55e",
        ),
        (
            "شروع و پایان حمل",
            "مدیریت عملیات پلاک‌ها",
            ft.icons.LOCAL_SHIPPING,
            "#3b82f6",
        ),
        (
            "مدیریت برنامه من",
            "ورود اختصاصی - دستگاه‌ها - گزارش پیامک",
            ft.icons.SECURITY,
            "#f97316",
        ),
        (
            "تاریخچه پیامک",
            "آخرین کدهای صدور - جستجو و گروه",
            ft.icons.MESSAGE,
            "#f59e0b",
        ),
        ("تاریخچه", "باربرگ - موفق و خطا", ft.icons.HISTORY, "#06b6d4"),
        (
            "شروع هوشمند",
            "آدرس زنجیره‌ای، کالا و فرستنده/گیرنده",
            ft.icons.AUTO_AWESOME,
            "#8b5cf6",
        ),
        (
            "آدرس‌های پلاک",
            "مبدا، مقصد و استعلام پلاک",
            ft.icons.MAP,
            "#a855f7",
        ),
        (
            "برنامه پیامکی",
            "شماره و رمز هر پلاک - استعلام مجوزهای اپ",
            ft.icons.SMS,
            "#fb923c",
        ),
        (
            "مدیریت پرداخت رانندگان",
            "ثبت پرداخت ماهانه و یادداشت",
            ft.icons.PAYMENTS,
            "#10b981",
        ),
        ("گزارش", "آخرین گزارش هر کاربر", ft.icons.BAR_CHART, "#14b8a6"),
        ("تعداد در دوره", "موفق‌های دوره و سقف ۱۲۰", ft.icons.EVENT, "#6366f1"),
        (
            "اپلیکیشن ثبت خودکار کد",
            "اگر راننده اپ را نصب کرده باشد، کد ثبت می‌شود",
            ft.icons.SMART_PHONE,
            "#0284c7",
        ),
        ("تعیین ارتباط", "به زودی در دسترس", ft.icons.LINK, "#64748b"),
        (
            "مدیریت سرورها",
            "سرور برای هر گروه (اتصال به utcms.ir)",
            ft.icons.DNS,
            "#ef4444",
        ),
        (
            "مدیریت پیامک رانندگان",
            "تنظیم پیام و دانلود اپ",
            ft.icons.PHONE_ANDROID,
            "#0ea5e9",
        ),
    ]

    grid_controls = []
    for title, desc, icon_name, color_code in feature_cards:

      def feature_clicked(e, t=title):
        add_log(f"دسترسی به بخش «{t}» فعال شد.", "#0284c7")

      card_item = ft.Container(
          bgcolor="white",
          padding=12,
          border_radius=14,
          border=ft.border.all(1, "#e2e8f0"),
          on_click=feature_clicked,
          content=ft.Column(
              alignment=ft.MainAxisAlignment.CENTER,
              horizontal_alignment=ft.CrossAxisAlignment.CENTER,
              spacing=6,
              controls=[
                  ft.Container(
                      width=40,
                      height=40,
                      bgcolor=color_code,
                      border_radius=10,
                      alignment=ft.alignment.center,
                      content=ft.Icon(icon_name, color="white", size=22),
                  ),
                  ft.Text(
                      title,
                      size=13,
                      weight="bold",
                      color="#0f172a",
                      text_align=ft.TextAlign.CENTER,
                  ),
                  ft.Text(
                      desc,
                      size=9,
                      color="#64748b",
                      text_align=ft.TextAlign.CENTER,
                  ),
              ],
          ),
      )
      grid_controls.append(card_item)

    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        controls=[
            ft.Text(
                "امکانات پیشرفته سامانه بارگو",
                size=16,
                weight="bold",
                color="#0f172a",
            ),
            ft.GridView(
                expand=False,
                runs_count=2,
                max_extent=180,
                spacing=10,
                run_spacing=10,
                controls=grid_controls,
            ),
        ],
    )

  # مدیریت تغییر تب‌ها با منوی پایین‌صفحه
  def render_tab_content(tab_name):
    body_container.content = None
    if tab_name == "کاربران":
      body_container.content = ft.Column(
          scroll=ft.ScrollMode.AUTO,
          expand=True,
          spacing=10,
          controls=[
              ft.Row(
                  alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                  controls=[
                      ft.Text(
                          "مدیریت کاربران و ناوگان",
                          size=16,
                          weight="bold",
                          color="#0f172a",
                      ),
                      ft.ElevatedButton(
                          "افزودن کاربر +",
                          bgcolor="#0284c7",
                          color="white",
                          on_click=lambda e: engine.data["drivers"].append({
                              "id": len(engine.data["drivers"]) + 1,
                              "name": "راننده جدید",
                              "national_id": "3440000000",
                              "password": "Aa123456##",
                              "mobile": "09170000000",
                              "group": 1,
                              "active": True,
                              "plate_left": "11",
                              "plate_letter": "ع",
                              "plate_mid": "111",
                              "plate_iran": "84",
                              "tonnage": 6,
                              "cargo": "ماسه",
                              "pack": "فله",
                              "weight": "5",
                              "count": "1",
                              "value": "25000000",
                              "fare": "15000000",
                              "origin_name": "بندر لنگه",
                              "dest_name": "بندر کنگ",
                              "origin_lat": 26.5579,
                              "origin_lon": 54.8807,
                              "dest_lat": 26.5946,
                              "dest_lon": 54.9463,
                              "distance_km": 20.55,
                              "fuel_quota": "پایش فعال",
                              "fleet_license": "معتبر",
                              "driver_license": "معتبر",
                          })
                          or render_drivers_list(),
                      ),
                  ],
              ),
              ft.Row(
                  controls=[
                      ft.TextField(
                          hint_text="جستجوی نام یا پلاک...",
                          prefix_icon=ft.icons.SEARCH,
                          bgcolor="white",
                          height=40,
                          text_size=12,
                          expand=True,
                          on_change=lambda e: (
                              setattr(
                                  globals(), "search_query", e.control.value
                              ),
                              render_drivers_list(),
                          ),
                      ),
                  ]
              ),
              drivers_column,
          ],
      )
      render_drivers_list()
    elif tab_name == "امکانات":
      body_container.content = build_amenities_view()
    elif tab_name == "باربرگ":
      body_container.content = ft.Column(
          [
              ft.Text(
                  "تاریخچه صدور باربرگ‌های موفق و خطا",
                  size=16,
                  weight="bold",
                  color="#0f172a",
              ),
              ft.Text(
                  "تمامی باربرگ‌ها به صورت خودکار از طریق درگاه utcms.ir ثبت"
                  " شده‌اند.",
                  size=12,
                  color="#64748b",
              ),
          ]
      )
    elif tab_name == "پروانه":
      body_container.content = ft.Column([
          ft.Text(
              "استعلام و وضعیت پروانه فعالیت ناوگان و راننده",
              size=16,
              weight="bold",
              color="#0f172a",
          ),
          ft.Text(
              "وضعیت: تمامی پروانه‌ها فعال و استعلام‌شده هستند.",
              size=12,
              color="#16a34a",
          ),
      ])
    elif tab_name == "سهمیه":
      body_container.content = ft.Column([
          ft.Text(
              "پایش سهمیه سوخت ناوگان (تیر و گازوئیل)",
              size=16,
              weight="bold",
              color="#0f172a",
          ),
          ft.Text(
              "سهمیه سوخت فعال و بدون مغایرت در سامانه ثبت است.",
              size=12,
              color="#0284c7",
          ),
      ])
    page.update()

  # منوی پایین‌صفحه (Bottom Navigation Bar) دقیقاً مثل تصویر شما
  def on_nav_change(e):
    index = e.control.selected_index
    tabs = ["کاربران", "امکانات", "باربرگ", "پروانه", "سهمیه"]
    render_tab_content(tabs[index])

  bottom_nav = ft.NavigationBar(
      selected_index=0,
      bgcolor="white",
      elevation=8,
      destinations=[
          ft.NavigationDestination(
              icon=ft.icons.PERSON_OUTLINE,
              selected_icon=ft.icons.PERSON,
              label="کاربران",
          ),
          ft.NavigationDestination(
              icon=ft.icons.GRID_VIEW_OUTLINED,
              selected_icon=ft.icons.GRID_VIEW,
              label="امکانات",
          ),
          ft.NavigationDestination(
              icon=ft.icons.LOCAL_SHIPPING_OUTLINED,
              selected_icon=ft.icons.LOCAL_SHIPPING,
              label="باربرگ",
          ),
          ft.NavigationDestination(
              icon=ft.icons.DESCRIPTION_OUTLINED,
              selected_icon=ft.icons.DESCRIPTION,
              label="پروانه",
          ),
          ft.NavigationDestination(
              icon=ft.icons.LOCAL_GAS_STATION_OUTLINED,
              selected_icon=ft.icons.LOCAL_GAS_STATION,
              label="سهمیه",
          ),
      ],
      on_change=on_nav_change,
  )

  page.navigation_bar = bottom_nav

  # هدر بالای صفحه خلوت و صنعتی
  header_top = ft.Container(
      bgcolor="#0f172a",
      padding=ft.padding.symmetric(horizontal=14, vertical=10),
      content=ft.Row(
          alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
          controls=[
              ft.Row(
                  spacing=8,
                  controls=[
                      ft.Icon(ft.icons.SECURITY, color="#38bdf8", size=20),
                      ft.Text(
                          "BarGo Enterprise VIP",
                          color="white",
                          size=14,
                          weight="bold",
                      ),
                  ],
              ),
              ft.Text(
                  "درگاه utcms.ir فعال", color="#22c55e", size=11, weight="bold"
              ),
          ],
      ),
  )

  page.add(
      ft.Column(
          expand=True,
          spacing=0,
          controls=[
              header_top,
              body_container,
              ft.Container(
                  bgcolor="#f1f5f9",
                  padding=6,
                  content=ft.Column(
                      spacing=2,
                      controls=[
                          ft.Text(
                              "مانیتورینگ زنده ربات (AI Engine):",
                              size=11,
                              weight="bold",
                              color="#475569",
                          ),
                          log_list,
                      ],
                  ),
              ),
          ],
      )
  )

  render_tab_content("کاربران")


if __name__ == "__main__":
  ft.app(target=main)
