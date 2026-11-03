import time
import traceback
import flet as ft

# ایمپورت کردن موتور اصلی برنامه
try:
  from engine import BarbargEngine
except Exception as import_err:
  BarbargEngine = None
  ENGINE_IMPORT_ERROR = traceback.format_exc()


def main(page: ft.Page):
  page.title = "بارگو بندر - BarGo"
  page.rtl = True
  page.bgcolor = "#0b0f19"
  page.padding = 20
  page.scroll = ft.ScrollMode.AUTO

  # اگر در فایل engine.py خطای تایپی مثل Import با حرف بزرگ باشد، اینجا روی صفحه نشان می‌دهد
  if BarbargEngine is None:
    page.add(
        ft.Container(
            content=ft.Text(
                f"خطا در بارگذاری فایل engine.py:\n{ENGINE_IMPORT_ERROR}",
                color="red",
                size=13,
                selectable=True,
            ),
            padding=15,
            bgcolor="#1e1b2e",
            border_radius=10,
        )
    )
    return

  try:
    engine = BarbargEngine()

    # هدر برنامه
    header = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "سامانه هوشمند باربرگ درون‌شهری (بارگو)",
                    size=20,
                    weight="bold",
                    color="#38bdf8",
                ),
                ft.Text(
                    "پایش خودکار سرور و ثبت پلاک ناوگان",
                    size=13,
                    color="#94a3b8",
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        ),
        alignment=ft.alignment.center,
        padding=ft.padding.only(bottom=10),
    )

    # نشانگر وضعیت سرور
    status_icon = ft.Icon(name=ft.icons.CLOUD_DONE, color="#22c55e", size=28)
    server_title = ft.Text(
        "سرور فعال: سامانه درون‌شهری (اصلی)",
        size=14,
        weight="bold",
        color="white",
    )
    health_subtitle = ft.Text(
        "وضعیت شبکه: آماده به کار", size=12, color="#94a3b8"
    )

    status_card = ft.Container(
        content=ft.Row(
            [
                status_icon,
                ft.Column([server_title, health_subtitle], spacing=3, expand=True),
            ],
            alignment=ft.MainAxisAlignment.START,
        ),
        bgcolor="#1e293b",
        padding=15,
        border_radius=12,
        border=ft.border.all(1, "#334155"),
    )

    # فیلدهای ورودی پلاک و گروه
    plate_input = ft.TextField(
        label="مشخصات پلاک خودرو",
        hint_text="مثال: 84 ع 365 - ایران 84",
        bgcolor="#0f172a",
        color="white",
        border_color="#38bdf8",
        focused_border_color="#22c55e",
        border_radius=10,
        text_size=15,
    )

    group_dropdown = ft.Dropdown(
        label="انتخاب گروه ناوگان",
        bgcolor="#0f172a",
        color="white",
        border_color="#38bdf8",
        border_radius=10,
        value="1",
        options=[
            ft.dropdown.Option("1", "گروه ۱ - ناوگان عمومی درون‌شهری"),
            ft.dropdown.Option("2", "گروه ۲ - کامیونت و خاور"),
            ft.dropdown.Option("3", "گروه ۳ - کشنده و سنگین"),
        ],
    )

    # بخش نمایش گزارش عملیات (لاگ‌ها)
    log_column = ft.Column(spacing=6)
    log_container = ft.Container(
        content=log_column,
        bgcolor="#0f172a",
        padding=12,
        border_radius=10,
        border=ft.border.all(1, "#1e293b"),
        height=180,
    )

    def add_log(msg, color="#e2e8f0"):
      current_time = time.strftime("%H:%M:%S")
      log_column.controls.insert(
          0, ft.Text(f"[{current_time}] {msg}", size=12, color=color)
      )
      page.update()

    # تابع بررسی دستی وضعیت سرور
    def check_health_clicked(e):
      check_btn.disabled = True
      health_subtitle.value = "در حال تست پکت‌های سرور utcms.ir..."
      health_subtitle.color = "#eab308"
      page.update()

      mode = engine.auto_switch_server()
      if engine.server_status == "active":
        status_icon.name = ft.icons.CLOUD_DONE
        status_icon.color = "#22c55e"
        server_title.value = "سرور فعال: سامانه درون‌شهری (utcms.ir)"
        health_subtitle.value = "پاسخگویی سرور عالی و بدون اختلال است"
        health_subtitle.color = "#22c55e"
        add_log("تست سلامت: سرور اصلی سامانه پایدار است.", "#22c55e")
      else:
        status_icon.name = ft.icons.CELL_TOWER
        status_icon.color = "#f97316"
        server_title.value = "سرور فعال: آنتن موبایل (هات‌اسپات هوشمند)"
        health_subtitle.value = "اختلال در سرور اصلی! سوییچ خودکار انجام شد"
        health_subtitle.color = "#f97316"
        add_log(
            "هشدار: قطعی در سرور اصلی! سوییچ هوشمند روی آنتن موبایل.", "#f97316"
        )

      check_btn.disabled = False
      page.update()

    # تابع ثبت پلاک با استفاده از موتور اصلی
    def register_clicked(e):
      if not plate_input.value or not plate_input.value.strip():
        add_log("خطا: لطفاً ابتدا شماره پلاک خودرو را وارد کنید!", "#ef4444")
        return

      submit_btn.disabled = True
      submit_btn.text = "در حال پایش سرور و ثبت پلاک..."
      page.update()

      try:
        res = engine.register_plate_task(
            plate_input.value.strip(), group_dropdown.value
        )

        # بروزرسانی وضعیت کارت سرور بر اساس نتیجه موتور
        if engine.active_server == "urban_main":
          status_icon.name = ft.icons.CLOUD_DONE
          status_icon.color = "#22c55e"
          server_title.value = f"سرور فعال: {res['server']}"
          health_subtitle.value = "ارتباط پایدار با سامانه"
          health_subtitle.color = "#22c55e"
        else:
          status_icon.name = ft.icons.CELL_TOWER
          status_icon.color = "#f97316"
          server_title.value = f"سرور فعال: {res['server']}"
          health_subtitle.value = "ثبت از طریق مسیر جایگزین (سوییچ هوشمند)"
          health_subtitle.color = "#f97316"

        add_log(f"✅ {res['message']} (پلاک: {plate_input.value})", "#4ade80")
        plate_input.value = ""

      except Exception as ex:
        add_log(f"خطا در ثبت: {str(ex)}", "#ef4444")

      submit_btn.disabled = False
      submit_btn.text = "ثبت هوشمند باربرگ"
      page.update()

    submit_btn = ft.ElevatedButton(
        text="ثبت هوشمند باربرگ",
        icon=ft.icons.SEND_ROUNDED,
        bgcolor="#0284c7",
        color="white",
        height=48,
        width=400,
        on_click=register_clicked,
    )

    check_btn = ft.OutlinedButton(
        text="بررسی سلامت سرور و سوییچ خودکار",
        icon=ft.icons.NETWORK_CHECK,
        height=44,
        width=400,
        on_click=check_health_clicked,
    )

    add_log("موتور هوشمند باربرگ بندر آماده عملیات است.", "#38bdf8")

    # چیدمان صفحه
    page.add(
        ft.Column(
            [
                header,
                status_card,
                ft.Container(height=5),
                plate_input,
                group_dropdown,
                ft.Container(height=5),
                submit_btn,
                check_btn,
                ft.Divider(color="#1e293b", height=20),
                ft.Text(
                    "گزارش زنده عملیات (AI Monitor):",
                    size=13,
                    weight="bold",
                    color="#94a3b8",
                ),
                log_container,
            ],
            spacing=12,
        )
    )

  except Exception:
    err = traceback.format_exc()
    page.add(
        ft.Text(f"خطای اجرا:\n{err}", color="red", size=12, selectable=True)
    )


if __name__ == "__main__":
  ft.app(target=main)
