import flet as ft


def main(page: ft.Page):
  page.title = "BarGo Test"
  page.rtl = True
  page.bgcolor = "#0b0f19"

  page.add(
      ft.Column(
          [
              ft.Text(
                  "پنل باربرگ بندر - اتصال موفق",
                  color="white",
                  size=20,
                  weight=ft.FontWeight.BOLD,
              ),
              ft.ElevatedButton("تست ارتباط", bgcolor="#10b981", color="white"),
          ],
          alignment=ft.MainAxisAlignment.CENTER,
          horizontal_alignment=ft.CrossAxisAlignment.CENTER,
          expand=True,
      )
  )


ft.app(target=main)
