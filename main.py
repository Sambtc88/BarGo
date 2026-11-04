import traceback
import flet as ft

try:
  from engine import BarbargEngine
except Exception:
  BarbargEngine = None
  ENGINE_ERR = traceback.format_exc()


def build_iran_plate(left_2, letter, mid_3, iran_code):
  return ft.Container(
      height=44,
      width=220,
      bgcolor="white",
      border=ft.border.all(2, "#0f172a"),
      border_radius=8,
      clip_behavior=ft.ClipBehavior.HARD_EDGE,
      content=ft.Row(
          spacing=0,
          controls=[
              ft.Container(
                  width=44,
                  height=44,
                  bgcolor="white",
                  border=ft.border.only(left=ft.BorderSide(1.5, "#0f172a")),
                  alignment=ft.alignment.center,
                  content=ft.Column(
                      spacing=0,
                      alignment=ft.MainAxisAlignment.CENTER,
                      horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                      controls=[
                          ft.Text(
                              "ایران", size=9, weight="bold", color="#0f172a"
                          ),
                          ft.Text(
                              str(iran_code),
                              size=15,
                              weight="bold",
                              color="#0f172a",
                          ),
                      ],
                  ),
              ),
              ft.Container(
                  expand=True,
                  height=44,
                  bgcolor="white",
                  alignment=ft.alignment.center,
                  content=ft.Row(
                      alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                      vertical_alignment=ft.CrossAxisAlignment.CENTER,
                      controls=[
                          ft.Text(
                              str(mid_3),
                              size=18,
                              weight="bold",
                              color="#0f172a",
                          ),
                          ft.Text(
                              str(letter),
                              size=18,
                              weight="bold",
                              color="#dc2626",
                          ),
                          ft.Text(
                              str(left_2),
                              size=18,
                              weight="bold",
                              color="#0f172a",
                          ),
                      ],
                  ),
              ),
              ft.Container(
                  width=30,
                  height=44,
                  bgcolor="#0284c7",
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
                              size=6,
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
  page.title = "سناتور - بارگو پرو"
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
  current_user = {"name": "Davood", "plan": "VIP", "days_left": 27}

  log_box = ft.Column(spacing=3, scroll=ft.ScrollMode.AUTO, height=65)

  def add_log(msg, color="#0f172a"):
    log_box.controls.insert(
        0, ft.Text(f"• {msg}", size=11, color=color, weight="bold")
    )
    page.update()

  body_view = ft.Container(expand=True, padding=12)

  # ۱. صفحه ورود (Login Screen) دقیقاً مشابه سناتور
  def build_login_view():
    tf_user = ft.TextField(
        label="نام کاربری",
        value="Davood",
        bgcolor="white",
        border_radius=10,
        prefix_icon=ft.icons.PERSON,
    )
    tf_pass = ft.TextField(
        label="کلمه عبور",
        value="1234",
        password=True,
        can_reveal_password=True,
        bgcolor="white",
        border_radius=10,
        prefix_icon=ft.icons.LOCK,
    )
    chk_robot = ft.Checkbox(
        label="من ربات نیستم (تایید هوش مصنوعی)", value=True
    )
    err_txt = ft.Text("", color="#dc2626", size=12)

    def do_login(e):
      if not chk_robot.value:
        err_txt.value = "لطفاً تایید من ربات نیستم را فعال کنید."
        page.update()
        return
      ok, client = engine.authenticate(tf_user.value.strip(), tf_pass.value)
      if ok:
        nonlocal current_user
        current_user = client
        build_main_app()
      else:
        err_txt.value = "نام کاربری یا کلمه عبور اشتباه است."
        page.update()

    return ft.View(
        route="/login",
        bgcolor="white",
        padding=30,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                width=340,
                padding=20,
                bgcolor="white",
                border_radius=16,
                border=ft.border.all(1, "#cbd5e1"),
                shadow=ft.BoxShadow(blur_radius=15, color=ft.colors.BLACK12),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=14,
                    controls=[
                        ft.Container(
                            width=60,
                            height=60,
                            bgcolor="#14b8a6",
                            border_radius=30,
                            alignment=ft.alignment.center,
                            content=ft.Icon(
                                ft.icons.SHIELD, color="white", size=30
                            ),
                        ),
                        ft.Text(
                            "سناتور",
                            size=24,
                            weight="bold",
                            color="#0f172a",
                        ),
                        tf_user,
                        tf_pass,
                        chk_robot,
                        err_txt,
                        ft.ElevatedButton(
                            "ورود",
                            bgcolor="#0284c7",
                            color="white",
                            width=300,
                            height=45,
                            on_click=do_login,
                        ),
                    ],
                ),
            )
        ],
    )

  # دیالوگ ویرایش پیشرفته کاربر + نقشه لایو و اطلاعات بار
  def open_edit_dialog(drv):
    tf_name = ft.TextField(
        label="نام راننده", value=drv["name"], text_size=12, expand=True
    )
    tf_nid = ft.TextField(
        label="کد ملی", value=drv["national_id"], text_size=12, expand=True
    )
    tf_mobile = ft.TextField(
        label="موبایل", value=drv["mobile"], text_size=12, expand=True
    )
    tf_pass = ft.TextField(
        label="رمز عبور", value=drv["password"], text_size=12, expand=True
    )

    dd_pack = ft.Dropdown(
        label="نوع بسته‌بندی",
        value=drv["pack"],
        expand=True,
        options=[
            ft.dropdown.Option(p, p)
            for p in ["کارتن", "جعبه", "کیسه", "گونی", "جامبو", "فله", "پالت"]
        ],
    )
    tf_weight = ft.TextField(
        label="وزن (تن)", value=drv["weight"], width=90, text_size=12
    )
    tf_fare = ft.TextField(
        label="کرایه (ریال)", value=drv["fare"], text_size=12, expand=True
    )

    # بخش نقشه پیشرفته OSM مشابه ویدئوی سناتور
    map_box = ft.Container(
        height=150,
        bgcolor="#e2e8f0",
        border_radius=10,
        padding=10,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    "🗺️ سناتور OSM (نقشه زنده با قابلیت کلیک و اسکرول)",
                    size=11,
                    weight="bold",
                    color="#0f172a",
                ),
                ft.Text(
                    f"مبدا: {drv['origin_name']} ⬅ مقصد: {drv['dest_name']} ({drv['distance_km']} km)",
                    size=11,
                    color="#0284c7",
                ),
                ft.ElevatedButton(
                    "انتخاب نقطه روی نقشه",
                    bgcolor="#0284c7",
                    color="white",
                    height=30,
                    on_click=lambda e: add_log(
                        "نقشه لایو فعال شد: مختصات مبدا و مقصد تنظیم گشت.",
                        "#0284c7",
                    ),
                ),
            ],
        ),
    )

    def save_changes(e):
      drv["name"] = tf_name.value.strip()
      drv["national_id"] = tf_nid.value.strip()
      drv["mobile"] = tf_mobile.value.strip()
      drv["pack"] = dd_pack.value
      drv["weight"] = tf_weight.value.strip()
      drv["fare"] = tf_fare.value.strip()
      engine.save_data()
      dlg.open = False
      switch_tab("کاربران")
      add_log(f"کاربر {drv['name']} با موفقیت ویرایش شد.", "#16a34a")

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(
            f"ویرایش کاربر: {drv['name']}", size=14, weight="bold"
        ),
        content=ft.Container(
            width=400,
            height=440,
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                spacing=10,
                controls=[
                    ft.Text("مشخصات راننده", weight="bold", color="#0284c7"),
                    ft.Row([tf_name, tf_nid]),
                    ft.Row([tf_mobile, tf_pass]),
                    ft.Divider(),
                    ft.Text("پلاک انتظامی ناوگان", weight="bold", color="#0284c7"),
                    ft.Container(
                        alignment=ft.alignment.center,
                        content=build_iran_plate(
                            drv["plate_left"],
                            drv["plate_letter"],
                            drv["plate_mid"],
                            drv["plate_iran"],
                        ),
                    ),
                    ft.Divider(),
                    ft.Text("اطلاعات بار و کرایه", weight="bold", color="#0284c7"),
                    ft.Row([dd_pack, tf_weight]),
                    ft.Row([tf_fare]),
                    ft.Divider(),
                    ft.Text("آدرس و مختصات نقشه", weight="bold", color="#0284c7"),
                    map_box,
                ],
            ),
        ),
        actions=[
            ft.ElevatedButton(
                "ذخیره تغییرات",
                bgcolor="#0284c7",
                color="white",
                on_click=save_changes,
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

  # تب ۱: کاربران (مدیریت ناوگان دقیقاً مثل ویدئو)
  def build_users_view():
    drivers_list = ft.Column(spacing=10)
    for idx, drv in enumerate(engine.data["drivers"], start=1):
      d_card = ft.Container(
          bgcolor="white",
          padding=12,
          border_radius=12,
          border=ft.border.all(1, "#cbd5e1"),
          content=ft.Column(
              spacing=8,
              controls=[
                  ft.Row(
                      alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                      controls=[
                          ft.Row(
                              spacing=8,
                              controls=[
                                  ft.Switch(
                                      value=drv["active"],
                                      active_color="#16a34a",
                                      on_change=lambda e, d=drv: setattr(
                                          d, "active", e.control.value
                                      )
                                      or engine.save_data(),
                                  ),
                                  ft.Column(
                                      spacing=0,
                                      controls=[
                                          ft.Text(
                                              drv["name"],
                                              size=15,
                                              weight="bold",
                                              color="#0f172a",
                                          ),
                                          ft.Text(
                                              drv["national_id"],
                                              size=11,
                                              color="#64748b",
                                          ),
                                      ],
                                  ),
                              ],
                          ),
                          build_iran_plate(
                              drv["plate_left"],
                              drv["plate_letter"],
                              drv["plate_mid"],
                              drv["plate_iran"],
                          ),
                      ],
                  ),
                  ft.Row(
                      alignment=ft.MainAxisAlignment.END,
                      spacing=6,
                      controls=[
                          ft.ElevatedButton(
                              "ویرایش",
                              bgcolor="#0284c7",
                              color="white",
                              height=32,
                              on_click=lambda e, d=drv: open_edit_dialog(d),
                          ),
                          ft.OutlinedButton(
                              "حذف",
                              height=32,
                              style=ft.ButtonStyle(color="#dc2626"),
                              on_click=lambda e, d=drv: engine.data[
                                  "drivers"
                              ].remove(d)
                              or engine.save_data()
                              or switch_tab("کاربران"),
                          ),
                      ],
                  ),
              ],
          ),
      )
      drivers_list.controls.append(d_card)

    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=10,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.ElevatedButton(
                        "افزودن کاربر",
                        bgcolor="#0284c7",
                        color="white",
                        icon=ft.icons.ADD,
                    ),
                    ft.ElevatedButton(
                        "افزودن گروهی", bgcolor="#14b8a6", color="white"
                    ),
                ],
            ),
            drivers_list,
        ],
    )

  # تب ۲: امکانات (منوی کارت‌های رنگی سناتور)
  def build_amenities_view():
    items = [
        ("آدرس‌ها", ft.icons.LOCATION_ON, "#0ea5e9"),
        ("تعیین نوع بار", ft.icons.CATEGORY, "#22c55e"),
        ("شروع و پایان حمل", ft.icons.LOCAL_SHIPPING, "#3b82f6"),
        ("مدیریت برنامه من", ft.icons.SECURITY, "#f97316"),
        ("تاریخچه پیامک", ft.icons.MESSAGE, "#f59e0b"),
        ("تاریخچه صدور", ft.icons.HISTORY, "#06b6d4"),
        ("شروع هوشمند AI", ft.icons.AUTO_AWESOME, "#8b5cf6"),
        ("مدیریت سرورها", ft.icons.DNS, "#ef4444"),
    ]
    grid = []
    for title, icon_n, col in items:
      grid.append(
          ft.Container(
              bgcolor="white",
              padding=14,
              border_radius=12,
              border=ft.border.all(1, "#e2e8f0"),
              on_click=lambda e, t=title: add_log(
                  f"بخش پیشرفته «{t}» بارگذاری شد.", "#0284c7"
              ),
              content=ft.Column(
                  alignment=ft.MainAxisAlignment.CENTER,
                  horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                  spacing=6,
                  controls=[
                      ft.Icon(icon_n, color=col, size=28),
                      ft.Text(
                          title,
                          size=12,
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
            ft.GridView(
                expand=False,
                runs_count=3,
                max_extent=120,
                spacing=10,
                run_spacing=10,
                controls=grid,
            ),
        ],
    )

  # تب ۳: باربرگ (گروه‌بندی گروه ۱ و گروه ۲)
  def build_barbarg_view():
    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=12,
        controls=[
            ft.Text(
                "گروه را انتخاب کنید تا پنل اتوماسیون رانندگان، پلاک‌ها و عملیات"
                " شروع/پایان نمایش داده شود.",
                size=12,
                color="#64748b",
            ),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                controls=[
                    ft.Container(
                        bgcolor="white",
                        padding=16,
                        border_radius=12,
                        border=ft.border.all(1.5, "#14b8a6"),
                        width=170,
                        alignment=ft.alignment.center,
                        on_click=lambda e: add_log(
                            "ورود به پنل اتوماسیون گروه ۱", "#14b8a6"
                        ),
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=4,
                            controls=[
                                ft.Text(
                                    "گروه ۱",
                                    size=16,
                                    weight="bold",
                                    color="#14b8a6",
                                ),
                                ft.Text(
                                    "۱۹ پلاک | در حال اجرا",
                                    size=11,
                                    color="#64748b",
                                ),
                            ],
                        ),
                    ),
                    ft.Container(
                        bgcolor="white",
                        padding=16,
                        border_radius=12,
                        border=ft.border.all(1.5, "#0284c7"),
                        width=170,
                        alignment=ft.alignment.center,
                        on_click=lambda e: add_log(
                            "ورود به پنل اتوماسیون گروه ۲", "#0284c7"
                        ),
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=4,
                            controls=[
                                ft.Text(
                                    "گروه ۲",
                                    size=16,
                                    weight="bold",
                                    color="#0284c7",
                                ),
                                ft.Text(
                                    "۱۸ پلاک | در حال اجرا",
                                    size=11,
                                    color="#64748b",
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        ],
    )

  # تب ۴: پروانه (استعلام پروانه فعالیت و اشتغال)
  def build_parvaneh_view():
    p_rows = []
    for drv in engine.data["drivers"]:
      p_rows.append(
          ft.Container(
              bgcolor="white",
              padding=10,
              border_radius=10,
              border=ft.border.all(1, "#cbd5e1"),
              content=ft.Row(
                  alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                  controls=[
                      ft.Column(
                          [
                              ft.Text(
                                  drv["name"],
                                  size=13,
                                  weight="bold",
                                  color="#0f172a",
                              ),
                              ft.Text(
                                  f"پروانه فعالیت: {drv['fleet_status']}",
                                  size=11,
                                  color="#16a34a",
                              ),
                              ft.Text(
                                  f"پروانه اشتغال: {drv['driver_status']}",
                                  size=11,
                                  color="#d97706",
                              ),
                          ],
                      ),
                      ft.ElevatedButton(
                          "استعلام",
                          bgcolor="#0284c7",
                          color="white",
                          height=32,
                          on_click=lambda e, d=drv: add_log(
                              engine.query_utcms_action(d, "license"),
                              "#0284c7",
                          ),
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
            ft.Text(
                "استعلام پروانه‌ها (لیست رانندگان، پلاک گروه و وضعیت پروانه‌ها)",
                size=12,
                color="#64748b",
            ),
            ft.ElevatedButton(
                "استعلام گروهی پروانه‌ها", bgcolor="#14b8a6", color="white"
            ),
            ft.Column(spacing=8, controls=p_rows),
        ],
    )

  # تب ۵: سهمیه (استعلام سهمیه سوخت مرحله اول و دوم)
  def build_sahmieh_view():
    s_rows = []
    for drv in engine.data["drivers"]:
      s_rows.append(
          ft.Container(
              bgcolor="white",
              padding=10,
              border_radius=10,
              border=ft.border.all(1, "#cbd5e1"),
              content=ft.Row(
                  alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                  controls=[
                      ft.Column(
                          [
                              ft.Text(
                                  drv["name"],
                                  size=13,
                                  weight="bold",
                                  color="#0f172a",
                              ),
                              ft.Text(
                                  f"عملکرد اول: {drv['fuel_quota_1']} | عملکرد دوم:"
                                  f" {drv['fuel_quota_2']}",
                                  size=11,
                                  color="#334155",
                              ),
                          ],
                      ),
                      ft.ElevatedButton(
                          "استعلام سوخت",
                          bgcolor="#16a34a",
                          color="white",
                          height=32,
                          on_click=lambda e, d=drv: add_log(
                              engine.query_utcms_action(d, "fuel"), "#16a34a"
                          ),
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
            ft.Text(
                "استعلام سهمیه سوخت (لیست رانندگان، پلاک و سهمیه مرحله اول و دوم)",
                size=12,
                color="#64748b",
            ),
            ft.ElevatedButton(
                "استعلام گروهی سهمیه", bgcolor="#0284c7", color="white"
            ),
            ft.Column(spacing=8, controls=s_rows),
        ],
    )

  def switch_tab(tab_name):
    body_view.content = None
    if tab_name == "کاربران":
      body_view.content = build_users_view()
    elif tab_name == "امکانات":
      body_view.content = build_amenities_view()
    elif tab_name == "باربرگ":
      body_view.content = build_barbarg_view()
    elif tab_name == "پروانه":
      body_view.content = build_parvaneh_view()
    elif tab_name == "سهمیه":
      body_view.content = build_sahmieh_view()
    page.update()

  # منوی کشویی پروفایل (Drawer) و هدر استاندارد با فاصله ایمن
  def build_main_app():
    page.views.clear()

    # منوی کشویی کناری (Drawer) درست مثل ویدئوی سناتور
    drawer_content = ft.NavigationDrawer(
        bgcolor="white",
        controls=[
            ft.Container(
                padding=20,
                bgcolor="#0f172a",
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.CircleAvatar(
                            radius=35,
                            bgcolor="#14b8a6",
                            content=ft.Icon(
                                ft.icons.PERSON, size=40, color="white"
                            ),
                        ),
                        ft.Text(
                            current_user["name"],
                            color="white",
                            size=16,
                            weight="bold",
                        ),
                        ft.Text(
                            f"روزهای باقی‌مانده اشتراک: {current_user['days_left']} روز",
                            color="#38bdf8",
                            size=11,
                        ),
                    ],
                ),
            ),
            ft.NavigationDrawerDestination(
                icon=ft.icons.PEOPLE, label="کاربران"
            ),
            ft.NavigationDrawerDestination(
                icon=ft.icons.GRID_VIEW, label="امکانات"
            ),
            ft.NavigationDrawerDestination(
                icon=ft.icons.LOCAL_SHIPPING, label="باربرگ"
            ),
            ft.NavigationDrawerDestination(
                icon=ft.icons.DESCRIPTION, label="پروانه"
            ),
            ft.NavigationDrawerDestination(
                icon=ft.icons.LOCAL_GAS_STATION, label="سهمیه"
            ),
            ft.Divider(),
            ft.NavigationDrawerDestination(
                icon=ft.icons.LOGOUT, label="خروج از حساب"
            ),
        ],
        on_change=lambda e: page.close(drawer_content)
        or (
            switch_tab(
                ["کاربران", "امکانات", "باربرگ", "پروانه", "سهمیه"][
                    e.control.selected_index
                ]
            )
            if e.control.selected_index < 5
            else (
                page.views.clear()
                or page.views.append(build_login_view())
                or page.update()
            )
        ),
    )

    safe_header = ft.Container(
        bgcolor="#0f172a",
        padding=ft.padding.only(top=38, bottom=12, left=16, right=16),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            controls=[
                ft.IconButton(
                    icon=ft.icons.MENU,
                    icon_color="white",
                    on_click=lambda e: page.open(drawer_content),
                ),
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Icon(ft.icons.SHIELD, color="#14b8a6", size=22),
                        ft.Text(
                            "سناتور پرو (بارگو)",
                            color="white",
                            size=16,
                            weight="bold",
                        ),
                    ],
                ),
                ft.IconButton(icon=ft.icons.NOTIFICATIONS, icon_color="white"),
            ],
        ),
    )

    bottom_nav = ft.NavigationBar(
        selected_index=0,
        bgcolor="white",
        elevation=10,
        destinations=[
            ft.NavigationDestination(icon=ft.icons.PEOPLE, label="کاربران"),
            ft.NavigationDestination(icon=ft.icons.GRID_VIEW, label="امکانات"),
            ft.NavigationDestination(
                icon=ft.icons.LOCAL_SHIPPING, label="باربرگ"
            ),
            ft.NavigationDestination(
                icon=ft.icons.DESCRIPTION, label="پروانه"
            ),
            ft.NavigationDestination(
                icon=ft.icons.LOCAL_GAS_STATION, label="سهمیه"
            ),
        ],
        on_change=lambda e: switch_tab(
            ["کاربران", "امکانات", "باربرگ", "پروانه", "سهمیه"][
                e.control.selected_index
            ]
        ),
    )

    app_view = ft.View(
        route="/dashboard",
        bgcolor="#f8fafc",
        padding=0,
        controls=[
            safe_header,
            body_view,
            ft.Container(
                bgcolor="#e2e8f0",
                padding=6,
                content=ft.Column(
                    spacing=2,
                    controls=[
                        ft.Text(
                            "مانیتورینگ زنده ربات (AI Engine):",
                            size=10,
                            weight="bold",
                            color="#475569",
                        ),
                        log_box,
                    ],
                ),
            ),
            bottom_nav,
        ],
    )
    page.views.append(app_view)
    switch_tab("کاربران")
    page.update()

  page.views.append(build_login_view())
  page.update()


if __name__ == "__main__":
  ft.app(target=main)
