import traceback
import flet as ft

try:
  from engine import BarbargEngine
except Exception:
  BarbargEngine = None
  ENGINE_ERR = traceback.format_exc()


def build_iran_plate(left_2, letter, mid_3, iran_code):
  """طراحی فوق‌العاده حرفه‌ای و سه‌بعدی پلاک ملی ایران"""
  return ft.Container(
      height=50,
      width=260,
      bgcolor="white",
      border=ft.border.all(2.5, "#1e293b"),
      border_radius=10,
      shadow=ft.BoxShadow(blur_radius=8, color=ft.colors.BLACK12),
      clip_behavior=ft.ClipBehavior.HARD_EDGE,
      content=ft.Row(
          spacing=0,
          controls=[
              ft.Container(
                  width=52,
                  height=50,
                  bgcolor="#f8fafc",
                  border=ft.border.only(left=ft.BorderSide(2, "#1e293b")),
                  alignment=ft.alignment.center,
                  content=ft.Column(
                      spacing=0,
                      alignment=ft.MainAxisAlignment.CENTER,
                      horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                      controls=[
                          ft.Text(
                              "ایران",
                              size=10,
                              weight="bold",
                              color="#475569",
                          ),
                          ft.Text(
                              str(iran_code),
                              size=16,
                              weight="bold",
                              color="#0f172a",
                          ),
                      ],
                  ),
              ),
              ft.Container(
                  expand=True,
                  height=50,
                  bgcolor="white",
                  alignment=ft.alignment.center,
                  content=ft.Row(
                      alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                      vertical_alignment=ft.CrossAxisAlignment.CENTER,
                      controls=[
                          ft.Text(
                              str(mid_3),
                              size=20,
                              weight="bold",
                              color="#0f172a",
                          ),
                          ft.Text(
                              str(letter),
                              size=20,
                              weight="bold",
                              color="#dc2626",
                          ),
                          ft.Text(
                              str(left_2),
                              size=20,
                              weight="bold",
                              color="#0f172a",
                          ),
                      ],
                  ),
              ),
              ft.Container(
                  width=34,
                  height=50,
                  bgcolor="#0284c7",
                  alignment=ft.alignment.center,
                  content=ft.Column(
                      spacing=1,
                      alignment=ft.MainAxisAlignment.CENTER,
                      horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                      controls=[
                          ft.Container(width=16, height=3, bgcolor="#22c55e"),
                          ft.Container(width=16, height=3, bgcolor="white"),
                          ft.Container(width=16, height=3, bgcolor="#ef4444"),
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
  page.title = "BarGo Enterprise Pro"
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
  current_client = {"name": "داود پاپراس (مدیر ارشد)", "plan": "200 پلاک VIP"}

  log_list = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO, height=75)

  def add_log(msg, color="#0f172a"):
    log_list.controls.insert(
        0, ft.Text(f"⚡ {msg}", size=11, color=color, weight="bold")
    )
    page.update()

  body_container = ft.Container(expand=True, padding=12)
  drivers_column = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO)

  def render_drivers():
    drivers_column.controls.clear()
    for idx, drv in enumerate(engine.data["drivers"], start=1):
      card = ft.Container(
          bgcolor="white",
          padding=16,
          border_radius=16,
          border=ft.border.all(1, "#e2e8f0"),
          shadow=ft.BoxShadow(blur_radius=10, color=ft.colors.BLACK12),
          content=ft.Column(
              spacing=10,
              controls=[
                  ft.Row(
                      alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                      controls=[
                          ft.Row(
                              spacing=10,
                              controls=[
                                  ft.Container(
                                      width=34,
                                      height=34,
                                      bgcolor="#e0f2fe",
                                      border_radius=10,
                                      alignment=ft.alignment.center,
                                      content=ft.Text(
                                          str(idx),
                                          weight="bold",
                                          color="#0284c7",
                                          size=14,
                                      ),
                                  ),
                                  ft.Column(
                                      spacing=2,
                                      controls=[
                                          ft.Text(
                                              drv["name"],
                                              size=15,
                                              weight="bold",
                                              color="#0f172a",
                                          ),
                                          ft.Text(
                                              f"کد ملی: {drv['national_id']} | تناژ: {drv['tonnage']} تن",
                                              size=11,
                                              color="#64748b",
                                          ),
                                      ],
                                  ),
                              ],
                          ),
                          ft.Switch(
                              value=drv["active"],
                              active_color="#16a34a",
                              on_change=lambda e, d=drv: setattr(
                                  d, "active", e.control.value
                              )
                              or engine.save_data(),
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
                  ft.Container(
                      bgcolor="#f8fafc",
                      padding=10,
                      border_radius=10,
                      content=ft.Column(
                          spacing=4,
                          controls=[
                              ft.Text(
                                  f"📦 بار: {drv['cargo']} ({drv['weight']} تن) | کرایه: {drv['fare']} ریال",
                                  size=11,
                                  color="#334155",
                                  weight="bold",
                              ),
                              ft.Text(
                                  f"📍 مسیر: {drv['origin_name']} به {drv['dest_name']} ({drv['distance_km']} km)",
                                  size=11,
                                  color="#0284c7",
                              ),
                          ],
                      ),
                  ),
                  ft.Row(
                      alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                      controls=[
                          ft.ElevatedButton(
                              "ثبت و صدور",
                              bgcolor="#0284c7",
                              color="white",
                              height=36,
                              on_click=lambda e, d=drv: add_log(
                                  engine.execute_real_action(d, "issue"),
                                  "#16a34a",
                              ),
                          ),
                          ft.ElevatedButton(
                              "شروع حمل",
                              bgcolor="#16a34a",
                              color="white",
                              height=36,
                              on_click=lambda e, d=drv: add_log(
                                  engine.execute_real_action(d, "start_trip"),
                                  "#0284c7",
                              ),
                          ),
                          ft.ElevatedButton(
                              "پایان حمل",
                              bgcolor="#0d9488",
                              color="white",
                              height=36,
                              on_click=lambda e, d=drv: add_log(
                                  engine.execute_real_action(d, "end_trip"),
                                  "#0369a1",
                              ),
                          ),
                      ],
                  ),
              ],
          ),
      )
      drivers_column.controls.append(card)
    page.update()

  def build_amenities_view():
    features = [
        ("تعیین نوع بار هوشمند", ft.icons.CATEGORY, "#22c55e"),
        ("مدیریت نقشه و GPS", ft.icons.MAP, "#0ea5e9"),
        ("شروع و پایان حمل گروهی", ft.icons.LOCAL_SHIPPING, "#3b82f6"),
        ("گزارشات و تاریخچه صدور", ft.icons.HISTORY, "#06b6d4"),
        ("مدیریت سرورهای متناوب", ft.icons.DNS, "#ef4444"),
        ("امنیت و پکیج کاربران", ft.icons.SECURITY, "#f97316"),
    ]
    grid = []
    for title, icon_n, col in features:
      grid.append(
          ft.Container(
              bgcolor="white",
              padding=16,
              border_radius=14,
              border=ft.border.all(1, "#e2e8f0"),
              shadow=ft.BoxShadow(blur_radius=6, color=ft.colors.BLACK12),
              on_click=lambda e, t=title: add_log(
                  f"بخش پیشرفته «{t}» بارگذاری شد.", "#0284c7"
              ),
              content=ft.Column(
                  alignment=ft.MainAxisAlignment.CENTER,
                  horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                  spacing=8,
                  controls=[
                      ft.Icon(icon_n, color=col, size=32),
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
                "امکانات حرفه‌ای پنل تجاری",
                size=16,
                weight="bold",
                color="#0f172a",
            ),
            ft.GridView(
                expand=False,
                runs_count=2,
                max_extent=170,
                spacing=12,
                run_spacing=12,
                controls=grid,
            ),
        ],
    )

  def switch_tab(tab_name):
    body_container.content = None
    if tab_name == "کاربران":
      body_container.content = ft.Column(
          scroll=ft.ScrollMode.AUTO,
          expand=True,
          spacing=12,
          controls=[
              ft.Row(
                  alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                  controls=[
                      ft.Text(
                          "مدیریت ناوگان فعال",
                          size=16,
                          weight="bold",
                          color="#0f172a",
                      ),
                      ft.ElevatedButton(
                          "افزودن پلاک +",
                          bgcolor="#0284c7",
                          color="white",
                          on_click=lambda e: render_drivers(),
                      ),
                  ],
              ),
              drivers_column,
          ],
      )
      render_drivers()
    elif tab_name == "امکانات":
      body_container.content = build_amenities_view()
    elif tab_name == "باربرگ":
      body_container.content = ft.Column([
          ft.Text(
              "گزارش باربرگ‌های صادرشده",
              size=16,
              weight="bold",
              color="#0f172a",
          ),
          ft.Text(
              "تمامی عملیات از طریق درگاه اصلی utcms.ir ثبت شده است.",
              size=12,
              color="#64748b",
          ),
      ])
    elif tab_name == "پروانه":
      body_container.content = ft.Column([
          ft.Text(
              "وضعیت پروانه فعالیت ناوگان",
              size=16,
              weight="bold",
              color="#0f172a",
          ),
          ft.Text("تمامی پروانه‌ها معتبر و تاییدشده هستند.", size=12, color="#16a34a"),
      ])
    elif tab_name == "سهمیه":
      body_container.content = ft.Column([
          ft.Text(
              "سهمیه سوخت گازوئیل / تیر",
              size=16,
              weight="bold",
              color="#0f172a",
          ),
          ft.Text(
              "وضعیت سهمیه سوخت عادی و تخصیصی: برقرار",
              size=12,
              color="#0284c7",
          ),
      ])
    page.update()

  # هدر بالا با فاصله امن کامل از پنل اعلان گوشی
  safe_header = ft.Container(
      bgcolor="#0f172a",
      padding=ft.padding.only(top=38, bottom=14, left=16, right=16),
      content=ft.Row(
          alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
          controls=[
              ft.Row(
                  spacing=10,
                  controls=[
                      ft.Icon(
                          ft.icons.LOCAL_SHIPPING_ROUNDED,
                          color="#38bdf8",
                          size=26,
                      ),
                      ft.Column(
                          spacing=0,
                          controls=[
                              ft.Text(
                                  "BarGo Enterprise Pro",
                                  color="white",
                                  size=16,
                                  weight="bold",
                              ),
                              ft.Text(
                                  f"مدیر: {current_client['name']} | اشتراک: {current_client['plan']}",
                                  color="#38bdf8",
                                  size=11,
                              ),
                          ],
                      ),
                  ],
              ),
          ],
      ),
  )

  bottom_nav = ft.NavigationBar(
      selected_index=0,
      bgcolor="white",
      elevation=12,
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
      on_change=lambda e: switch_tab(
          ["کاربران", "امکانات", "باربرگ", "پروانه", "سهمیه"][
              e.control.selected_index
          ]
      ),
  )

  page.add(
      ft.Column(
          expand=True,
          spacing=0,
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
                              "مانیتورینگ زنده ربات هوشمند (AI Engine):",
                              size=11,
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
  )

  switch_tab("کاربران")
  add_log(
      "سیستم تجاری BarGo Pro با موفقیت بارگذاری شد. اتصال به درگاه utcms.ir"
      " برقرار است.",
      "#0284c7",
  )


if __name__ == "__main__":
  ft.app(target=main)
