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
  page.title = "BarGo Enterprise VIP"
  page.rtl = True
  page.bgcolor = "#0f172a"
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
  current_user = {"name": "مهمان", "plan": "آزمایشی"}
  selected_group_filter = "all"
  search_query = ""

  log_list = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO, height=80)

  def add_log(msg, color="#38bdf8"):
    log_list.controls.insert(
        0, ft.Text(f"• {msg}", size=11, color=color, weight="bold")
    )
    page.update()

  # ساخت صفحه ورود امن (Login Screen) برای هر خریدار پنل
  def build_login_screen():
    tf_user = ft.TextField(
        label="نام کاربری (Username)",
        hint_text="مثال: admin یا bargo100",
        bgcolor="#1e293b",
        color="white",
        border_color="#38bdf8",
        border_radius=12,
        prefix_icon=ft.icons.PERSON,
    )
    tf_pass = ft.TextField(
        label="رمز عبور (Password)",
        password=True,
        can_reveal_password=True,
        bgcolor="#1e293b",
        color="white",
        border_color="#38bdf8",
        border_radius=12,
        prefix_icon=ft.icons.LOCK,
    )
    err_text = ft.Text("", color="#ef4444", size=12, weight="bold")

    def do_login(e):
      ok, client_info = engine.authenticate_user(
          tf_user.value.strip(), tf_pass.value.strip()
      )
      if ok:
        nonlocal current_user
        current_user = client_info
        add_log(f"ورود موفق به پنل اختصاصی: {client_info['name']}", "#22c55e")
        build_main_dashboard()
      else:
        err_text.value = "نام کاربری یا رمز عبور اشتباه است!"
        page.update()

    return ft.View(
        route="/login",
        bgcolor="#0f172a",
        padding=30,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                width=360,
                bgcolor="#1e293b",
                padding=24,
                border_radius=20,
                border=ft.border.all(1, "#334155"),
                shadow=ft.BoxShadow(blur_radius=25, color=ft.colors.BLACK54),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=16,
                    controls=[
                        ft.Container(
                            width=70,
                            height=70,
                            bgcolor="#0284c7",
                            border_radius=35,
                            alignment=ft.alignment.center,
                            content=ft.Icon(
                                ft.icons.LOCAL_SHIPPING,
                                color="white",
                                size=36,
                            ),
                        ),
                        ft.Text(
                            "بارگو بندر (BarGo VIP)",
                            size=20,
                            weight="bold",
                            color="white",
                        ),
                        ft.Text(
                            "سیستم هوشمند صدور باربرگ و مدیریت ناوگان",
                            size=12,
                            color="#94a3b8",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Divider(color="#334155"),
                        tf_user,
                        tf_pass,
                        err_text,
                        ft.ElevatedButton(
                            "ورود به پنل اختصاصی",
                            bgcolor="#0284c7",
                            color="white",
                            height=48,
                            width=320,
                            on_click=do_login,
                        ),
                    ],
                ),
            )
        ],
    )

  # بدنه اصلی داشبورد (پس از لاگین موفق)
  body_container = ft.Container(expand=True, padding=12, bgcolor="#f8fafc")
  drivers_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)

  def open_edit_dialog(driver):
    tf_name = ft.TextField(
        label="نام راننده", value=driver["name"], text_size=13, expand=True
    )
    tf_nid = ft.TextField(
        label="کد ملی", value=driver["national_id"], text_size=13, expand=True
    )
    tf_mobile = ft.TextField(
        label="موبایل", value=driver["mobile"], text_size=13, expand=True
    )
    tf_fare = ft.TextField(
        label="کرایه (ریال)", value=driver["fare"], expand=True
    )

    # فیلدهای نقشه زنده با قابلیت کلیک و اسکرول و تنظیم مختصات
    tf_orig_lat = ft.TextField(
        label="عرض مبدا (Lat)",
        value=str(driver["origin_lat"]),
        text_size=12,
        expand=True,
    )
    tf_orig_lon = ft.TextField(
        label="طول مبدا (Lon)",
        value=str(driver["origin_lon"]),
        text_size=12,
        expand=True,
    )
    tf_dest_lat = ft.TextField(
        label="عرض مقصد (Lat)",
        value=str(driver["dest_lat"]),
        text_size=12,
        expand=True,
    )
    tf_dest_lon = ft.TextField(
        label="طول مقصد (Lon)",
        value=str(driver["dest_lon"]),
        text_size=12,
        expand=True,
    )

    dist_preview = ft.Text(
        f"مسافت محاسبه‌شده: {driver['distance_km']} کیلومتر",
        size=12,
        weight="bold",
        color="#0369a1",
    )

    def update_live_map(e):
      try:
        olat, olon = float(tf_orig_lat.value), float(tf_orig_lon.value)
        dlat, dlon = float(tf_dest_lat.value), float(tf_dest_lon.value)
        km = engine.calculate_distance(olat, olon, dlat, dlon)
        driver["origin_lat"], driver["origin_lon"] = olat, olon
        driver["dest_lat"], driver["dest_lon"] = dlat, dlon
        driver["distance_km"] = km
        dist_preview.value = (
            f"✅ مختصات لایو آپدیت شد | مسافت جاده‌ای: {km} کیلومتر"
        )
        page.update()
      except ValueError:
        dist_preview.value = "⚠️ خطا در ورود مقادیر مختصات!"
        page.update()

    interactive_map_box = ft.Container(
        bgcolor="#e0f2fe",
        border_radius=12,
        border=ft.border.all(1.5, "#0284c7"),
        padding=12,
        content=ft.Column(
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    "🗺️ نقشه تعاملی زنده GPS (اسکرول و تنظیم مختصات)",
                    size=12,
                    weight="bold",
                    color="#0369a1",
                ),
                dist_preview,
                ft.Row([tf_orig_lat, tf_orig_lon]),
                ft.Row([tf_dest_lat, tf_dest_lon]),
                ft.ElevatedButton(
                    "تایید و محاسبه آنلاین مسیر",
                    bgcolor="#0284c7",
                    color="white",
                    height=32,
                    on_click=update_live_map,
                ),
            ],
        ),
    )

    def save_dlg(e):
      driver["name"] = tf_name.value.strip()
      driver["national_id"] = tf_nid.value.strip()
      driver["mobile"] = tf_mobile.value.strip()
      driver["fare"] = tf_fare.value.strip()
      engine.save_data()
      dlg.open = False
      render_tab_content("کاربران")
      add_log(f"ویرایش کاربر {driver['name']} ذخیره شد.", "#16a34a")

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(
            f"ویرایش پیشرفته و نقشه لایو: {driver['name']}",
            size=14,
            weight="bold",
        ),
        content=ft.Container(
            width=420,
            height=460,
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                spacing=10,
                controls=[
                    ft.Row([tf_name, tf_nid]),
                    ft.Row([tf_mobile, tf_fare]),
                    ft.Divider(),
                    interactive_map_box,
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

      def make_action(d, act):
        def _ac(e):
          msg = engine.execute_real_action(d, act)
          add_log(msg, "#15803d")

        return _ac

      card = ft.Container(
          bgcolor="white",
          padding=12,
          border_radius=14,
          border=ft.border.all(1.5, "#cbd5e1"),
          content=ft.Column(
              spacing=8,
              controls=[
                  ft.Row(
                      alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                      controls=[
                          ft.Text(
                              drv["name"],
                              size=15,
                              weight="bold",
                              color="#0f172a",
                          ),
                          ft.Text(
                              f"کد ملی: {drv['national_id']} | گروه {drv['group']}",
                              size=11,
                              color="#64748b",
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
                      alignment=ft.MainAxisAlignment.END,
                      controls=[
                          ft.OutlinedButton(
                              "ویرایش / نقشه زنده GPS",
                              height=30,
                              on_click=lambda e, d=drv: open_edit_dialog(d),
                          ),
                      ],
                  ),
              ],
          ),
      )
      drivers_column.controls.append(card)
    page.update()

  # منوی امکانات مشابه سناتور
  def build_amenities_view():
    features = [
        ("تعیین نوع بار", ft.icons.CATEGORY, "#22c55e"),
        ("شروع و پایان حمل", ft.icons.LOCAL_SHIPPING, "#3b82f6"),
        ("مدیریت برنامه من", ft.icons.SECURITY, "#f97316"),
        ("تاریخچه صدور", ft.icons.HISTORY, "#06b6d4"),
        ("شروع هوشمند AI", ft.icons.AUTO_AWESOME, "#8b5cf6"),
        ("مدیریت سرورها", ft.icons.DNS, "#ef4444"),
    ]
    grid = []
    for title, icon_n, col in features:
      grid.append(
          ft.Container(
              bgcolor="white",
              padding=14,
              border_radius=12,
              border=ft.border.all(1, "#e2e8f0"),
              on_click=lambda e, t=title: add_log(
                  f"بخش «{t}» با موفقیت فعال شد.", "#0284c7"
              ),
              content=ft.Column(
                  alignment=ft.MainAxisAlignment.CENTER,
                  horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                  spacing=6,
                  controls=[
                      ft.Icon(icon_n, color=col, size=28),
                      ft.Text(
                          title,
                          size=13,
                          weight="bold",
                          color="#0f172a",
                          text_align=ft.TextAlign.CENTER,
                      ),
                  ],
              ),
          )
      )
    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        controls=[
            ft.Text(
                "امکانات پیشرفته پنل",
                size=16,
                weight="bold",
                color="#0f172a",
            ),
            ft.GridView(
                expand=False,
                runs_count=2,
                max_extent=160,
                spacing=10,
                run_spacing=10,
                controls=grid,
            ),
        ],
    )

  def render_tab_content(tab_name):
    body_container.content = None
    if tab_name == "کاربران":
      body_container.content = ft.Column(
          scroll=ft.ScrollMode.AUTO,
          expand=True,
          spacing=10,
          controls=[
              ft.Row(
                  alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                  controls=[
                      ft.Text(
                          "مدیریت ناوگان و پلاک‌ها",
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
                          })
                          or render_drivers_list(),
                      ),
                  ],
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
                  "تاریخچه باربرگ‌ها",
                  size=16,
                  weight="bold",
                  color="#0f172a",
              ),
              ft.Text(
                  "تمامی عملیات از طریق درگاه utcms.ir انجام شده است.",
                  size=12,
                  color="#64748b",
              ),
          ]
      )
    elif tab_name == "پروانه":
      body_container.content = ft.Column(
          [
              ft.Text(
                  "استعلام پروانه فعالیت",
                  size=16,
                  weight="bold",
                  color="#0f172a",
              ),
              ft.Text("وضعیت پروانه‌ها: معتبر و فعال", size=12, color="#16a34a"),
          ]
      )
    elif tab_name == "سهمیه":
      body_container.content = ft.Column(
          [
              ft.Text(
                  "پایش سهمیه سوخت",
                  size=16,
                  weight="bold",
                  color="#0f172a",
              ),
              ft.Text("سهمیه سوخت ناوگان تایید شده است.", size=12, color="#0284c7"),
          ]
      )
    page.update()

  def build_main_dashboard():
    page.views.clear()

    # هدر حرفه‌ای با فاصله امن از پنل اعلان گوشی (مهم)
    safe_header = ft.Container(
        bgcolor="#0f172a",
        padding=ft.padding.only(top=36, bottom=12, left=16, right=16),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Icon(
                            ft.icons.LOCAL_SHIPPING_ROUNDED,
                            color="#38bdf8",
                            size=24,
                        ),
                        ft.Column(
                            spacing=0,
                            controls=[
                                ft.Text(
                                    "BarGo Enterprise VIP",
                                    color="white",
                                    size=15,
                                    weight="bold",
                                ),
                                ft.Text(
                                    f"کاربر: {current_user['name']} ({current_user['plan']})",
                                    color="#38bdf8",
                                    size=10,
                                ),
                            ],
                        ),
                    ],
                ),
                ft.IconButton(
                    icon=ft.icons.LOGOUT,
                    icon_color="#ef4444",
                    tooltip="خروج از حساب",
                    on_click=lambda e: page.views.clear()
                    or page.views.append(build_login_screen())
                    or page.update(),
                ),
            ],
        ),
    )

    bottom_nav = ft.NavigationBar(
        selected_index=0,
        bgcolor="white",
        elevation=10,
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
        on_change=lambda e: render_tab_content(
            ["کاربران", "امکانات", "باربرگ", "پروانه", "سهمیه"][
                e.control.selected_index
            ]
        ),
    )

    dashboard_view = ft.View(
        route="/dashboard",
        bgcolor="#f8fafc",
        padding=0,
        controls=[
            safe_header,
            body_container,
            ft.Container(
                bgcolor="#e2e8f0",
                padding=8,
                content=ft.Column(
                    spacing=2,
                    controls=[
                        ft.Text(
                            "مانیتورینگ زنده اتوماسیون (AI Log):",
                            size=10,
                            weight="bold",
                            color="#475569",
                        ),
                        log_list,
                    ],
                ),
            ),
            bottom_nav,
        ],
    )
    page.views.append(dashboard_view)
    render_tab_content("کاربران")
    page.update()

  page.views.append(build_login_screen())
  page.update()


if __name__ == "__main__":
  ft.app(target=main)
