import traceback
import flet as ft


def main(page: ft.Page):
  page.title = "BarGo"
  page.rtl = True
  page.bgcolor = "#0b0f19"

  try:
    t = ft.Text(
        "اتصال موفق به سامانه باربرگ", color="white", size=18, weight="bold"
    )

    def button_clicked(e):
      t.value = "دکمه فشرده شد - سیستم فعال است"
      page.update()

    b = ft.ElevatedButton(text="تست کلیک", on_click=button_clicked)

    page.add(
        ft.Column(
            [t, b],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        )
    )
  except Exception:
    err = traceback.format_exc()
    page.add(ft.Text(f"خطا:\n{err}", color="red", size=12, selectable=True))


if __name__ == "__main__":
  ft.app(target=main)
