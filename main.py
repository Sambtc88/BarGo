import flet as ft


def main(page: ft.Page):
  page.title = "پنل مدیریت باربرگ بندر"
  page.rtl = True
  page.vertical_alignment = ft.MainAxisAlignment.START
  page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
  page.bgcolor = "#0f172a"  # پس‌زمینه تیره مدرن (سبک سناتور)

  # هدر پنل با طراحی لوکس
  header = ft.Container(
      content=ft.Row(
          [
              ft.Row(
                  [
                      ft.Icon(ft.icons.SHIELD_ROUNDED, color="#38bdf8", size=24),
                      ft.Text(
                          "کاربر: Ahmad | اعتبار: ۵۹ روز",
                          color="white",
                          weight=ft.FontWeight.BOLD,
                      ),
                  ],
                  spacing=10,
              ),
              ft.ElevatedButton(
                  "خروج",
                  color="white",
                  bgcolor="#ef4444",
                  style=ft.ButtonStyle(
                      shape=ft.RoundedRectangleBorder(radius=8)
                  ),
              ),
          ],
          alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
      ),
      bgcolor="#1e293b",
      padding=15,
      border_radius=12,
      margin=ft.margin.only(top=10, bottom=10),
  )

  # وضعیت سرور هوشمند
  server_status = ft.Container(
      content=ft.Row(
          [
              ft.Icon(ft.icons.CHECK_CIRCLE, color="#4ade80", size=20),
              ft.Text(
                  "وضعیت سرور هوشمند: سرور اصلی سامانه درون‌شهری (پایدار)",
                  color="#f1f5f9",
                  weight=ft.FontWeight.W_500,
              ),
          ],
          alignment=ft.MainAxisAlignment.CENTER,
      ),
      bgcolor="#064e3b",
      padding=12,
      border_radius=10,
      border=ft.border.all(1, "#059669"),
  )

  # بخش سرورهای اختصاصی با استایل کارتی مدرن
  def create_ip_card(ip, group, status_text):
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    ip, color="white", weight=ft.FontWeight.BOLD, size=16
                ),
                ft.Text(group, color="#94a3b8", size=12),
                ft.Container(
                    content=ft.Text(
                        status_text, color="#38bdf8", size=11, text_align="center"
                    ),
                    bgcolor="#0f172a",
                    padding=4,
                    border_radius=6,
                    margin=ft.margin.only(top=5),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor="#1e293b",
        padding=15,
        border_radius=12,
        border=ft.border.all(1, "#334155"),
        alignment=ft.alignment.center,
    )

  ip_grid = ft.GridView(
      expand=False,
      runs_count=3,
      max_extent=110,
      child_aspect_ratio=1.1,
      spacing=10,
      run_spacing=10,
      controls=[
          create_ip_card("IP 391", "گروه ۱", "فعال"),
          create_ip_card("IP 003", "گروه ۲", "فعال"),
          create_ip_card("IP 001", "آماده انتخاب", "آماده"),
          create_ip_card("IP 391", "گروه ۱", "فعال"),
          create_ip_card("IP 003", "گروه ۲", "فعال"),
          create_ip_card("IP 001", "آماده انتخاب", "آماده"),
      ],
  )

  servers_section = ft.Container(
      content=ft.Column(
          [
              ft.Text(
                  "وضعیت سرورهای فعال اختصاصی",
                  color="white",
                  weight=ft.FontWeight.BOLD,
                  size=14,
              ),
              ft.Divider(color="#334155"),
              ip_grid,
          ]
      ),
      bgcolor="#1e293b",
      padding=15,
      border_radius=12,
      border=ft.border.all(1, "#334155"),
  )

  page.add(
      ft.Container(
          content=ft.Column(
              [header, server_status, servers_section], spacing=15
          ),
          padding=15,
          width=400,
      )
  )


ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=2727)
