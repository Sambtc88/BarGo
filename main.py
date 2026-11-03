import flet as ft


def main(page: ft.Page):
  page.title = "BarGo"
  page.rtl = True
  page.bgcolor = "#0b0f19"

  # ایجاد یک متن ساده برای تست لود شدن
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


    ft.app(target=main)
