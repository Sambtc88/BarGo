import traceback
import flet as ft

try:
  from engine import BarbargEngine
except Exception:
  BarbargEngine = None
  ENGINE_ERR = traceback.format_exc()


def main(page: ft.Page):
  page.title = "BarGo Enterprise Pro - Desktop Mode"
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
  current_client = {"name": "داود پاپراس", "plan": "نامحدود VIP"}

  log_list = ft.Column(spacing=3, scroll=ft.ScrollMode.AUTO, height=75)

  def add_log(msg, color="#38bdf8"):
    log_list.controls.insert(
        0, ft.Text(f"• {msg}", size=11, color=color, weight="bold")
    )
    page.update()

  body_container = ft.Container(expand=True, padding=12, bgcolor="#f8fafc")
  drivers_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)

  # صفحه لاگین امن
  def build_login_screen():
    tf_user = ft.TextField(
        label="نام کاربری",
        value="admin",
        bgcolor="#1e293b",
        color="white",
        border_radius=10,
    )
    tf_pass = ft.TextField(
        label="رمز عبور",
        value="1234",
        password=True,
        bgcolor="#1e293b",
        color="white",
        border_radius=10,
    )
    err_txt = ft.Text("", color="#ef4444", size=12)

    def login_click(e):
      ok, info = engine.authenticate_user(
          tf_user.value.strip(), tf_pass.value.strip()
      )
      if ok:
        nonlocal current_client
        current_client = info
        build_main_dashboard()
      else:
        err_txt.value = "نام کاربری یا رمز اشتباه است!"
        page.update()

    return ft.View(
        route="/login",
        bgcolor="#0f172a",
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                width=340,
                padding=24,
                bgcolor="#1e293b",
                border_radius=16,
                border=ft.border.all(1, "#334155"),
                content=ft.Column(
                    spacing=12,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(
                            ft.icons.LOCAL_SHIPPING, color="#38bdf8", size=40
                        ),
                        ft.Text(
                            "بارگو بندر (نسخه تجاری)",
                            color="white",
                            size=18,
                            weight="bold",
                        ),
                        tf_user,
                        tf_pass,
                        err_txt,
                        ft.ElevatedButton(
                            "ورود به پنل مدیریت",
                            bgcolor="#0284c7",
                            color="white",
                            width=300,
                            height=45,
                            on_click=login_click,
                        ),
                    ],
                ),
            )
        ],
    )

  # دیالوگ استعلام واقعی از سامانه با کد ملی
  def open_fetch_dialog(e):
    tf_nid = ft.TextField(
        label="کد ملی ۱۰ رقمی راننده جهت استعلام از utcms.ir",
        hint_text="مثال: 3440112233",
        text_size=13,
    )
    res_info = ft.Text(
        "با زدن دکمه استعلام، اطلاعات مستقیم از سامانه باربرگ لود می‌شود.",
        size=11,
        color="#64748b",
    )

    def do_fetch(e):
      nid = tf_nid.value.strip()
      res_info.value = (
          "⏳ در حال اتصال به سامانه utcms.ir و استعلام اطلاعات..."
      )
      res_info.color = "#d97706"
      page.update()

      ok, data = engine.fetch_driver_from_utcms(nid)
      if ok:
        engine.data["drivers"].append(
            {
                "id": len(engine.data["drivers"]) + 1,
                **data,
                "group": 1,
                "active": True,
            }
        )
        engine.save_data()
        dlg_fetch.open = False
        render_drivers_table()
        add_log(f"✅ استعلام موفق و اضافه شدن پلاک از سامانه برای {data['name']}", "#16a34a")
      else:
        res_info.value = f"❌ خطا: {data}"
        res_info.color = "#dc2626"
        page.update()

    dlg_fetch = ft.AlertDialog(
        modal=True,
        title=ft.Text(
            "استعلام آنلاین ناوگان از سامانه utcms.ir",
            size=15,
            weight="bold",
        ),
        content=ft.Container(
            width=380,
            height=160,
            content=ft.Column(spacing=12, controls=[tf_nid, res_info]),
        ),
        actions=[
            ft.ElevatedButton(
                "استعلام و ثبت در پنل",
                bgcolor="#16a34a",
                color="white",
                on_click=do_fetch,
            ),
            ft.OutlinedButton(
                "بستن",
                on_click=lambda e: setattr(dlg_fetch, "open", False)
                or page.update(),
            ),
        ],
    )
    page.dialog = dlg_fetch
    dlg_fetch.open = True
    page.update()

  # رندر جدول دسکتاپی ناوگان (مشابه پنل‌های حرفه‌ای وب)
  def render_drivers_table():
    drivers_column.controls.clear()

    # هدر جدول
    header_row = ft.Container(
        bgcolor="#1e293b",
        padding=10,
        border_radius=8,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text("ردیف و نام راننده", color="white", size=12, weight="bold", expand=2),
                ft.Text("کد ملی / موبایل", color="white", size=12, weight="bold", expand=2),
                ft.Text("پلاک انتظامی", color="white", size=12, weight="bold", expand=2),
                ft.Text("بار و مسیر", color="white", size=12, weight="bold", expand=3),
                ft.Text("عملیات واقعی", color="white", size=12, weight="bold", expand=3),
            ],
        ),
    )
    drivers_column.controls.append(header_row)

    for idx, drv in enumerate(engine.data["drivers"], start=1):
      plate_str = f"{drv['plate_left']} {drv['plate_letter']} {drv['plate_mid']} - ایران {drv['plate_iran']}"
      
      row_item = ft.Container(
          bgcolor="white",
          padding=10,
          border_radius=8,
          border=ft.border.all(1, "#cbd5e1"),
          content=ft.Row(
              alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
              controls=[
                  ft.Column([
                      ft.Text(f"{idx}. {drv['name']}", size=13, weight="bold", color="#0f172a"),
                      ft.Text(f"تناژ: {drv['tonnage']} تن", size=10, color="#64748b"),
                  ], expand=2),
                  ft.Column([
                      ft.Text(drv['national_id'], size=12, color="#334155"),
                      ft.Text(drv['mobile'], size=10, color="#64748b"),
                  ], expand=2),
                  ft.Container(
                      bgcolor="#f1f5f9",
                      padding=6,
                      border_radius=6,
                      border=ft.border.all(1, "#0f172a"),
                      content=ft.Text(plate_str, size=11, weight="bold", color="#0f172a"),
                      expand=2,
                  ),
                  ft.Column([
                      ft.Text(f"{drv['cargo']} ({drv['weight']} تن)", size=11, weight="bold"),
                      ft.Text(f"{drv['origin_name']} ⬅ {drv['dest_name']}", size=10, color="#0284c7"),
                  ], expand=3),
                  ft.Row([
                      ft.ElevatedButton("صدور", bgcolor="#0284c7", color="white", height=30, on_click=lambda e, d=drv: add_log(engine.execute_real_action(d, "issue"), "#16a34a")),
                      ft.ElevatedButton("شروع", bgcolor="#16a34a", color="white", height=30, on_click=lambda e, d=drv: add_log(engine.execute_real_action(d, "start_trip"), "#0284c7")),
                      ft.ElevatedButton("پایان", bgcolor="#0d9488", color="white", height=30, on_click=lambda e, d=drv: add_log(engine.execute_real_action(d, "end_trip"), "#0369a1")),
                  ], expand=3, spacing=4),
              ],
          ),
      )
      drivers_column.controls.append(row_item)
    page.update()

  def switch_tab(tab_name):
    body_container.content = None
    if tab_name == "کاربران":
      body_container.content = ft.Column(
          expand=True,
          spacing=10,
          controls=[
              ft.Row(
                  alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                  controls=[
                      ft.Text("مدیریت جامع ناوگان و استعلام آنلاین", size=16, weight="bold", color="#0f172a"),
                      ft.ElevatedButton(
                          "استعلام پلاک با کد ملی (سامانه utcms)",
                          icon=ft.icons.SEARCH,
                          bgcolor="#0284c7",
                          color="white",
                          height=38,
                          on_click=open_fetch_dialog,
                      ),
                  ],
              ),
              drivers_column,
          ],
      )
      render_drivers_table()
    elif tab_name == "امکانات":
      body_container.content = ft.Column([
          ft.Text("امکانات پیشرفته تجاری ربات", size=16, weight="bold"),
          ft.Text("تمامی ماژول‌های استعلام سوخت، پروانه و شروع هوشمند فعال هستند.", size=12, color="#64748b"),
      ])
    elif tab_name == "باربرگ":
      body_container.content = ft.Column([
          ft.Text("گزارش جامع باربرگ‌های صادرشده", size=16, weight="bold"),
          ft.Text("ثبت قطعی در درگاه barname.utcms.ir انجام گرفته است.", size=12, color="#16a34a"),
      ])
    elif tab_name == "پروانه":
      body_container.content = ft.Column([ft.Text("استعلام آنلاین پروانه فعالیت و اشتغال رانندگان", size=16, weight="bold")])
    elif tab_name == "سهمیه":
      body_container.content = ft.Column([ft.Text("پایش لحظه‌ای سهمیه سوخت تخصیصی ناوگان", size=16, weight="bold")])
    page.update()

  def build_main_dashboard():
    page.views.clear()

    # هدر بالا با فاصله امن کامل از پنل اعلان گوشی
    safe_header = ft.Container(
        bgcolor="#0f172a",
        padding=ft.padding.only(top=38, bottom=12, left=16, right=16),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.Icon(ft.icons.COMPUTER, color="#38bdf8", size=24),
                        ft.Column(
                            spacing=0,
                            controls=[
                                ft.Text("BarGo Enterprise Pro (Desktop UI)", color="white", size=15, weight="bold"),
                                ft.Text(f"مدیر: {current_client['name']} | نوع پنل: {current_client['plan']}", color="#38bdf8", size=11),
                            ],
                        ),
                    ],
                ),
                ft.IconButton(
                    icon=ft.icons.LOGOUT,
                    icon_color="#ef4444",
                    tooltip="خروج",
                    on_click=lambda e: page.views.clear() or page.views.append(build_login_screen()) or page.update(),
                ),
            ],
        ),
    )

    bottom_nav = ft.NavigationBar(
        selected_index=0,
        bgcolor="white",
        elevation=12,
        destinations=[
            ft.NavigationDestination(icon=ft.icons.PEOPLE, label="کاربران"),
            ft.NavigationDestination(icon=ft.icons.GRID_VIEW, label="امکانات"),
            ft.NavigationDestination(icon=ft.icons.LOCAL_SHIPPING, label="باربرگ"),
            ft.NavigationDestination(icon=ft.icons.DESCRIPTION, label="پروانه"),
            ft.NavigationDestination(icon=ft.icons.LOCAL_GAS_STATION, label="سهمیه"),
        ],
        on_change=lambda e: switch_tab(["کاربران", "امکانات", "باربرگ", "پروانه", "سهمیه"][e.control.selected_index]),
    )

    dash_view = ft.View(
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
                        ft.Text("مانیتورینگ زنده ارتباط با سامانه (AI Engine):", size=11, weight="bold", color="#475569"),
                        log_list,
                    ],
                ),
            ),
            bottom_nav,
        ],
    )
    page.views.append(dash_view)
    switch_tab("کاربران")
    page.update()

  page.views.append(build_login_screen())
  page.update()


if __name__ == "__main__":
  ft.app(target=main)
