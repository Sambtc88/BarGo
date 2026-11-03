import asyncio
import flet as ft


def main(page: ft.Page):
  page.title = "پنل جامع ثبت باربرگ بندر (نسخه تجاری سناتور)"
  page.rtl = True
  page.vertical_alignment = ft.MainAxisAlignment.START
  page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
  page.bgcolor = "#0b0f19"  # پس‌زمینه تیره مدرن و فوق‌العاده شیک

  # کامپوننت پلاک گرافیکی واقعی ایرانی
  def create_iran_plate(part1, code, part2):
    return ft.Container(
        content=ft.Row(
            [
                # بخش شماره‌های پلاک
                ft.Row(
                    [
                        ft.Text(
                            part2,
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color="black",
                        ),
                        ft.Text(
                            code,
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color="black",
                        ),
                        ft.Text(
                            part1,
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color="black",
                        ),
                    ],
                    spacing=4,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                # نوار آبی کنار پلاک (ایران)
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "I.R.",
                                size=7,
                                color="white",
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "IRAN",
                                size=7,
                                color="white",
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                    ),
                    bgcolor="#1d4ed8",
                    width=22,
                    height=36,
                    alignment=ft.alignment.center,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=5,
        ),
        bgcolor="#f8fafc",
        border=ft.border.all(2, "#0f172a"),
        border_radius=6,
        padding=2,
        width=115,
        height=40,
        alignment=ft.alignment.center,
    )

  # هدر اصلی پنل با اطلاعات کاربر و وضعیت اعتبار
  header = ft.Container(
      content=ft.Row(
          [
              ft.Row(
                  [
                      ft.Container(
                          content=ft.Icon(
                              ft.icons.ADMIN_PANEL_SETTINGS,
                              color="#38bdf8",
                              size=22,
                          ),
                          bgcolor="#1e293b",
                          padding=8,
                          border_radius=8,
                      ),
                      ft.Column(
                          [
                              ft.Text(
                                  "کاربر: احمد (مدیر ناوگان)",
                                  color="white",
                                  weight=ft.FontWeight.BOLD,
                                  size=13,
                              ),
                              ft.Text(
                                  "اعتبار پنل: ۵۹ روز (فعال و پایدار)",
                                  color="#4ade80",
                                  size=11,
                              ),
                          ],
                          spacing=2,
                      ),
                  ],
                  spacing=10,
              ),
              ft.ElevatedButton(
                  "خروج امن",
                  icon=ft.icons.LOGOUT,
                  color="white",
                  bgcolor="#ef4444",
                  style=ft.ButtonStyle(
                      shape=ft.RoundedRectangleBorder(radius=8)
                  ),
              ),
          ],
          alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
      ),
      bgcolor="#111827",
      padding=12,
      border_radius=12,
      border=ft.border.all(1, "#1f2937"),
  )

  # وضعیت هوشمند سرور و دور زدن اختلال سامانه
  server_status = ft.Container(
      content=ft.Row(
          [
              ft.Icon(ft.icons.SHIELD_CHECK, color="#4ade80", size=20),
              ft.Text(
                  "وضعیت موتور: اتصال پایدار به سرور کمکی سامانه درون‌شهری",
                  color="#d1d5db",
                  size=12,
                  weight=ft.FontWeight.W_500,
              ),
          ],
          alignment=ft.MainAxisAlignment.CENTER,
      ),
      bgcolor="#064e3b",
      padding=10,
      border_radius=10,
      border=ft.border.all(1, "#059669"),
  )

  # منوی آبشاری انتخاب نقشه زنده / آفلاین (سناتور مپ)
  map_dropdown = ft.Dropdown(
      label="انتخاب موتور نقشه و مسیریاب زنده",
      label_style=ft.TextStyle(color="#9ca3af", size=12),
      border_color="#374151",
      focused_border_color="#38bdf8",
      color="white",
      bgcolor="#1f2937",
      options=[
          ft.dropdown.Option("osm_fast", "نقشه سریع OSM (پیش‌فرض / آنلاین)"),
          ft.dropdown.Option(
              "senator_offline", "نقشه اختصاصی سناتور (مسیریابی آفلاین)"
          ),
          ft.dropdown.Option(
              "hybrid_gps", "مسیریاب هوشمند مختصات بندر (ضد اختلال)"
          ),
      ],
      value="osm_fast",
  )

  map_section = ft.Container(
      content=ft.Column(
          [
              ft.Row(
                  [
                      ft.Icon(ft.icons.MAP, color="#38bdf8", size=18),
                      ft.Text(
                          "سیستم ناوبری و نقشه زنده",
                          color="white",
                          weight=ft.FontWeight.BOLD,
                          size=13,
                      ),
                  ],
                  spacing=8,
              ),
              map_dropdown,
          ],
          spacing=10,
      ),
      bgcolor="#111827",
      padding=15,
      border_radius=12,
      border=ft.border.all(1, "#1f2937"),
  )

  # جدول مدیریت وضعیت صدور و رانندگان همراه با پلاک گرافیکی
  def create_driver_row(name, phone, part1, code, part2, tonnage):
    plate_widget = create_iran_plate(part1, code, part2)
    return ft.Container(
        content=ft.Row(
            [
                # اطلاعات راننده
                ft.Column(
                    [
                        ft.Text(
                            name,
                            color="white",
                            weight=ft.FontWeight.BOLD,
                            size=12,
                        ),
                        ft.Text(phone, color="#9ca3af", size=10),
                    ],
                    spacing=2,
                    width=85,
                ),
                # پلاک گرافیکی واقعی
                plate_widget,
                # تناژ
                ft.Text(tonnage, color="#38bdf8", size=11, width=45),
                # دکمه‌های عملیاتی صدور و حمل
                ft.Column(
                    [
                        ft.ElevatedButton(
                            "صدور باربرگ",
                            color="white",
                            bgcolor="#10b981",
                            height=26,
                            style=ft.ButtonStyle(
                                text_style=ft.TextStyle(size=10),
                                shape=ft.RoundedRectangleBorder(radius=6),
                                padding=2,
                            ),
                        ),
                        ft.ElevatedButton(
                            "پایان/شروع حمل",
                            color="white",
                            bgcolor="#3b82f6",
                            height=26,
                            style=ft.ButtonStyle(
                                text_style=ft.TextStyle(size=9),
                                shape=ft.RoundedRectangleBorder(radius=6),
                                padding=2,
                            ),
                        ),
                    ],
                    spacing=4,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor="#1f2937",
        padding=10,
        border_radius=8,
        border=ft.border.all(1, "#374151"),
    )

  drivers_section = ft.Container(
      content=ft.Column(
          [
              ft.Row(
                  [
                      ft.Icon(
                          ft.icons.LOCAL_SHIPPING, color="#38bdf8", size=18
                      ),
                      ft.Text(
                          "مدیریت ناوگان و صدور خودکار باربرگ",
                          color="white",
                          weight=ft.FontWeight.BOLD,
                          size=13,
                      ),
                  ],
                  spacing=8,
              ),
              ft.Divider(color="#374151", height=1),
              create_driver_row(
                  "راشد کندرانی", "3430156696", "ع", "755", "94", "19 تن"
              ),
              create_driver_row(
                  "فرزانه استادی", "3440842517", "ع", "666", "93", "40 تن"
              ),
          ],
          spacing=10,
      ),
      bgcolor="#111827",
      padding=15,
      border_radius=12,
      border=ft.border.all(1, "#1f2937"),
  )

  # بخش دکمه فرمان اصلی صدور تصادفی / انبوه
  action_btn = ft.ElevatedButton(
      content=ft.Row(
          [
              ft.Icon(ft.icons.FLASH_ON, color="white", size=18),
              ft.Text(
                  "صدور هوشمند باربرگ با گیرنده تصادفی (بای پس اختلال)",
                  color="white",
                  weight=ft.FontWeight.BOLD,
                  size=12,
              ),
          ],
          alignment=ft.MainAxisAlignment.CENTER,
      ),
      bgcolor="#0284c7",
      style=ft.ButtonStyle(
          shape=ft.RoundedRectangleBorder(radius=10), padding=12
      ),
      width=400,
  )

  # اطلاعات واریز و اشتراک
  billing_section = ft.Container(
      content=ft.Column(
          [
              ft.Text(
                  "تمدید اشتراک و اطلاعات واریز آنی",
                  color="white",
                  weight=ft.FontWeight.BOLD,
                  size=12,
              ),
              ft.Container(
                  content=ft.Column(
                      [
                          ft.Text(
                              "شماره کارت: ۶۲۱۹۸۶۱۹۸۶۵۸۹۱۳۲",
                              color="#38bdf8",
                              size=12,
                              weight=ft.FontWeight.BOLD,
                          ),
                          ft.Text(
                              "شبا: IR530560611828005783056501",
                              color="#9ca3af",
                              size=10,
                          ),
                      ],
                      spacing=4,
                      horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                  ),
                  bgcolor="#1f2937",
                  padding=10,
                  border_radius=8,
                  alignment=ft.alignment.center,
              ),
          ],
          spacing=8,
      ),
      bgcolor="#111827",
      padding=15,
      border_radius=12,
      border=ft.border.all(1, "#1f2937"),
  )

  # چیدمان اصلی صفحه در یک اسکرول‌ویو منظم
  page.add(
      ft.ListView(
          controls=[header, server_status, action_btn, map_section, drivers_section, billing_section],
          spacing=12,
          padding=10,
          expand=True,
      )
  )


ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=2727)
