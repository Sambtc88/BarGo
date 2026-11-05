import random
import time
import traceback
import flet as ft

try:
  from engine import BarbargEngine, build_truck_plate, latlon_to_tile, to_fa
except Exception:
  BarbargEngine = None
  ENGINE_ERR = traceback.format_exc()


def main(page: ft.Page):
  page.title = "بارگو بندر"
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
  current_client = engine.data["clients"][0]
  active_tab = "کاربران"
  barbarg_grp = None
  body_holder = ft.Container(expand=True, padding=10)

  def show_popup(title, msg, is_err=False):
    bg = "#fee2e2" if is_err else "#dcfce7"
    col = "#991b1b" if is_err else "#166534"
    dlg = ft.AlertDialog(
        modal=True,
        content_padding=0,
        content=ft.Container(
            width=335,
            bgcolor=bg,
            border_radius=16,
            padding=14,
            content=ft.Column(
                tight=True,
                spacing=8,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                title, size=15, weight="bold", color=col
                            ),
                            ft.Text(
                                to_fa(time.strftime("%H:%M:%S")), size=11
                            ),
                        ],
                    ),
                    ft.Container(
                        bgcolor="white",
                        padding=12,
                        border_radius=10,
                        width=305,
                        content=ft.Text(
                            msg,
                            size=12,
                            weight="bold",
                            color="#0f172a",
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ),
                    ft.ElevatedButton(
                        "متوجه شدم ←",
                        bgcolor="white",
                        color="#0f172a",
                        width=305,
                        on_click=lambda e: setattr(dlg, "open", False)
                        or page.update(),
                    ),
                ],
            ),
        ),
    )
    page.dialog = dlg
    dlg.open = True
    page.update()

  # ==================== ۱. صفحه لاگین با کادرهای بنفش و تیک دستی ربات ====================
  def build_login():
    tf_u = ft.TextField(
        hint_text="نام کاربری",
        value="Davood",
        bgcolor="#f1f5f9",
        border_radius=10,
    )
    tf_p = ft.TextField(
        hint_text="کلمه عبور",
        value="1234",
        password=True,
        can_reveal_password=True,
        bgcolor="#f1f5f9",
        border_radius=10,
    )
    chk_robot = ft.Checkbox(
        label="من ربات نیستم (تایید امنیتی)", value=False
    )
    err_txt = ft.Text("", color="#dc2626", size=12, weight="bold")
    btn_login = ft.ElevatedButton(
        "ورود به پنل", bgcolor="#7c3aed", color="white", width=310, height=45
    )

    def do_log(e):
      if not chk_robot.value:
        err_txt.value = (
            "لطفاً ابتدا تیک «من ربات نیستم» را به صورت دستی فعال کنید!"
        )
        page.update()
        return
      ok, c = engine.authenticate(tf_u.value, tf_p.value)
      if ok:
        nonlocal current_client
        current_client = c
        build_scaffold()
      else:
        err_txt.value = "نام کاربری یا رمز عبور اشتباه است."
        page.update()

    btn_login.on_click = do_log

    return ft.View(
        route="/login",
        bgcolor="#0f172a",
        padding=24,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                width=350,
                padding=20,
                bgcolor="white",
                border_radius=20,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                    controls=[
                        ft.Container(
                            width=320,
                            padding=12,
                            bgcolor="#7c3aed",
                            border_radius=12,
                            alignment=ft.alignment.center,
                            content=ft.Text(
                                "باربرگ درون شهری بندر",
                                size=17,
                                weight="bold",
                                color="white",
                            ),
                        ),
                        tf_u,
                        tf_p,
                        chk_robot,
                        ft.Container(
                            width=320,
                            padding=12,
                            bgcolor="#f3e8ff",
                            border=ft.border.all(1.5, "#d8b4fe"),
                            border_radius=12,
                            alignment=ft.alignment.center,
                            content=ft.Text(
                                "خوش آمدید ❤️",
                                size=14,
                                weight="bold",
                                color="#6b21a8",
                            ),
                        ),
                        err_txt,
                        btn_login,
                    ],
                ),
            )
        ],
    )

  # ==================== ۲. ویرایش کامل با نقشه ماهواره‌ای بزرگ، اسکرول و مختصات زنده در پایین ====================
  def open_edit_modal(drv):
    tf_nid = ft.TextField(
        label="کد ملی", value=drv["national_id"], text_size=12, expand=True
    )
    tf_pw = ft.TextField(
        label="رمز سامانه", value=drv["password"], text_size=12, expand=True
    )
    dd_grp = ft.Dropdown(
        label="گروه",
        value=str(drv["group"]),
        width=85,
        options=[
            ft.dropdown.Option("1", "گروه ۱"),
            ft.dropdown.Option("2", "گروه ۲"),
        ],
    )
    tf_mob = ft.TextField(
        label="موبایل", value=drv["mobile"], text_size=12, expand=True
    )
    tf_pl_l = ft.TextField(label="دو رقم", value=drv["plate_left"], width=62)
    tf_pl_c = ft.TextField(label="حرف", value=drv["plate_letter"], width=50)
    tf_pl_m = ft.TextField(label="سه رقم", value=drv["plate_mid"], width=72)
    tf_pl_i = ft.TextField(label="ایران", value=drv["plate_iran"], width=62)

    map_state = {
        "lat": float(drv.get("origin_lat", 26.5579)),
        "lon": float(drv.get("origin_lon", 54.8807)),
        "zoom": 13,
        "target": "origin",
    }

    tf_olat = ft.TextField(
        label="lat مبدأ",
        value=str(drv["origin_lat"]),
        text_size=11,
        expand=True,
    )
    tf_olon = ft.TextField(
        label="lng مبدأ",
        value=str(drv["origin_lon"]),
        text_size=11,
        expand=True,
    )
    tf_dlat = ft.TextField(
        label="lat مقصد", value=str(drv["dest_lat"]), text_size=11, expand=True
    )
    tf_dlon = ft.TextField(
        label="lng مقصد", value=str(drv["dest_lon"]), text_size=11, expand=True
    )
    tf_orig = ft.TextField(
        label="شهر مبدأ", value=drv["origin_name"], text_size=11, expand=True
    )
    tf_dest = ft.TextField(
        label="شهر مقصد", value=drv["dest_name"], text_size=11, expand=True
    )

    coords_footer = ft.Text(
        f"مبدأ: ({drv['origin_lat']}, {drv['origin_lon']}) | مقصد:"
        f" ({drv['dest_lat']}, {drv['dest_lon']}) | مسافت:"
        f" {to_fa(drv['distance_km'])} km",
        size=11,
        weight="bold",
        color="#0369a1",
    )

    tiles_grid = ft.Column(spacing=0)
    pin_o = ft.Container(
        left=105,
        top=110,
        bgcolor="#dc2626",
        padding=4,
        border_radius=6,
        content=ft.Text("📍 مبدأ", color="white", size=9, weight="bold"),
    )
    pin_d = ft.Container(
        left=230,
        top=60,
        bgcolor="#0f172a",
        padding=4,
        border_radius=6,
        content=ft.Text("🏁 مقصد", color="white", size=9, weight="bold"),
    )

    def refresh_tiles():
      cx, cy = latlon_to_tile(
          map_state["lat"], map_state["lon"], map_state["zoom"]
      )
      z = map_state["zoom"]
      rows_t = []
      for dy in (-1, 0):
        r_imgs = []
        for dx in (-1, 0, 1):
          u = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{cy+dy}/{cx+dx}"
          r_imgs.append(
              ft.Image(
                  src=u, width=130, height=115, fit=ft.ImageFit.COVER
              )
          )
        rows_t.append(ft.Row(spacing=0, controls=r_imgs))
      tiles_grid.controls = rows_t

    refresh_tiles()

    def pan_map(dlat, dlon):
      map_state["lat"] = round(map_state["lat"] + dlat, 5)
      map_state["lon"] = round(map_state["lon"] + dlon, 5)
      refresh_tiles()
      page.update()

    def on_map_tap(ev: ft.TapEvent):
      lx = max(10, min(370, int(ev.local_x)))
      ly = max(10, min(210, int(ev.local_y)))
      clat = round(map_state["lat"] + (100.0 - ly) * 0.001, 5)
      clon = round(map_state["lon"] + (lx - 185.0) * 0.001, 5)
      if map_state["target"] == "origin":
        pin_o.left, pin_o.top = lx - 12, ly - 10
        tf_olat.value, tf_olon.value = str(clat), str(clon)
        drv["origin_lat"] = clat
        drv["origin_lon"] = clon
      else:
        pin_d.left, pin_d.top = lx - 12, ly - 10
        tf_dlat.value, tf_dlon.value = str(clat), str(clon)
        drv["dest_lat"] = clat
        drv["dest_lon"] = clon
      km = engine.calculate_distance(
          float(tf_olat.value),
          float(tf_olon.value),
          float(tf_dlat.value),
          float(tf_dlon.value),
      )
      drv["distance_km"] = km
      coords_footer.value = (
          f"مبدأ: ({tf_olat.value}, {tf_olon.value}) | مقصد: ({tf_dlat.value},"
          f" {tf_dlon.value}) | مسافت: {to_fa(km)} km"
      )
      page.update()

    map_large_box = ft.Container(
        width=380,
        height=220,
        bgcolor="#0f172a",
        border_radius=12,
        border=ft.border.all(2, "#0284c7"),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.GestureDetector(
            on_tap_down=on_map_tap,
            content=ft.Stack(
                width=380,
                height=220,
                controls=[
                    tiles_grid,
                    pin_o,
                    pin_d,
                    ft.Container(
                        right=6,
                        bottom=6,
                        bgcolor="#0f172a",
                        border_radius=8,
                        padding=2,
                        content=ft.Row(
                            spacing=2,
                            controls=[
                                ft.IconButton(
                                    icon=ft.icons.ARROW_UPWARD,
                                    icon_color="white",
                                    icon_size=16,
                                    on_click=lambda e: pan_map(0.01, 0),
                                ),
                                ft.IconButton(
                                    icon=ft.icons.ARROW_DOWNWARD,
                                    icon_color="white",
                                    icon_size=16,
                                    on_click=lambda e: pan_map(-0.01, 0),
                                ),
                                ft.IconButton(
                                    icon=ft.icons.ARROW_BACK,
                                    icon_color="white",
                                    icon_size=16,
                                    on_click=lambda e: pan_map(0, -0.01),
                                ),
                                ft.IconButton(
                                    icon=ft.icons.ARROW_FORWARD,
                                    icon_color="white",
                                    icon_size=16,
                                    on_click=lambda e: pan_map(0, 0.01),
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        ),
    )

    tf_cargo = ft.TextField(
        label="نوع بار / کالا", value=drv["cargo"], text_size=12, expand=True
    )
    tf_fare = ft.TextField(
        label="کرایه (ریال)", value=drv["fare"], text_size=12, expand=True
    )

    def save_u(e):
      drv["national_id"], drv["password"] = (
          tf_nid.value.strip(),
          tf_pw.value.strip(),
      )
      drv["group"], drv["mobile"] = int(dd_grp.value or 1), tf_mob.value.strip()
      (
          drv["plate_left"],
          drv["plate_letter"],
          drv["plate_mid"],
          drv["plate_iran"],
      ) = (tf_pl_l.value, tf_pl_c.value, tf_pl_m.value, tf_pl_i.value)
      drv["origin_name"], drv["dest_name"] = (
          tf_orig.value.strip(),
          tf_dest.value.strip(),
      )
      drv["cargo"], drv["fare"] = tf_cargo.value.strip(), tf_fare.value.strip()
      engine.save_data()
      dlg.open = False
      render_tab()

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(f"ویرایش: {drv['name']}", size=15, weight="bold"),
        content=ft.Container(
            width=400,
            height=510,
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                spacing=8,
                controls=[
                    ft.Row([tf_nid, tf_pw]),
                    ft.Row([dd_grp, tf_mob]),
                    ft.Row([tf_pl_i, tf_pl_m, tf_pl_c, tf_pl_l]),
                    ft.Divider(),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                        controls=[
                            ft.ElevatedButton(
                                "تعیین لمس: مبدأ 📍",
                                bgcolor="#dc2626",
                                color="white",
                                height=28,
                                on_click=lambda e: map_state.__setitem__(
                                    "target", "origin"
                                ),
                            ),
                            ft.ElevatedButton(
                                "تعیین لمس: مقصد 🏁",
                                bgcolor="#0f172a",
                                color="white",
                                height=28,
                                on_click=lambda e: map_state.__setitem__(
                                    "target", "dest"
                                ),
                            ),
                        ],
                    ),
                    map_large_box,
                    coords_footer,
                    ft.Row([tf_orig, tf_dest]),
                    ft.Row([tf_olat, tf_olon]),
                    ft.Row([tf_dlat, tf_dlon]),
                    ft.Row([tf_cargo, tf_fare]),
                ],
            ),
        ),
        actions=[
            ft.ElevatedButton(
                "ذخیره تغییرات",
                bgcolor="#0284c7",
                color="white",
                on_click=save_u,
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

  # ==================== ۳. تب کاربران و پلاک‌های کامیونی طبیعی ====================
  def build_users_tab():
    rows = ft.Column(spacing=6)
    for idx, drv in enumerate(engine.data["drivers"], start=1):
      on = drv["active"]
      rows.controls.append(
          ft.Container(
              bgcolor="white" if on else "#fff1f2",
              padding=8,
              border_radius=12,
              border=ft.border.all(1, "#cbd5e1"),
              content=ft.Row(
                  alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                  controls=[
                      ft.Text(to_fa(idx), size=12, weight="bold"),
                      ft.Column(
                          spacing=2,
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                          controls=[
                              ft.Text(drv["name"], size=13, weight="bold"),
                              ft.Text(
                                  f"📦 {drv['cargo']}",
                                  size=10,
                                  color="#0284c7",
                                  weight="bold",
                              ),
                          ],
                      ),
                      build_truck_plate(
                          drv["plate_left"],
                          drv["plate_letter"],
                          drv["plate_mid"],
                          drv["plate_iran"],
                      ),
                      ft.ElevatedButton(
                          "ویرایش",
                          bgcolor="#0284c7",
                          color="white",
                          height=30,
                          width=68,
                          on_click=lambda ev, d=drv: open_edit_modal(d),
                      ),
                  ],
              ),
          )
      )
    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        controls=[
            ft.Container(
                bgcolor="white",
                padding=14,
                border_radius=14,
                content=ft.Column(spacing=10, controls=[rows]),
            )
        ],
    )

  # ==================== ۴. امکانات و تمدید اعتبار با کارت بانکی و شبا ====================
  def open_renewal_modal(e):
    bank = engine.data["bank"]
    tf_last4 = ft.TextField(
        label="۴ رقم آخر شماره کارت واریزی",
        max_length=4,
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    tf_myname = ft.TextField(label="نام و نام خانوادگی واریزکننده")

    def verify_pay(ev):
      current_client["days_left"] += 30
      engine.save_data()
      dlg.open = False
      show_popup(
          "تمدید موفق",
          f"اشتراک پنل ۳۰ روز تمدید شد!\nاعتبار جدید:"
          f" {to_fa(current_client['days_left'])} روز باقی‌مانده.",
      )

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("💳 تمدید آنی اعتبار پنل", size=15, weight="bold"),
        content=ft.Container(
            width=360,
            height=320,
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Container(
                        bgcolor="#1e293b",
                        padding=12,
                        border_radius=12,
                        content=ft.Column(
                            spacing=3,
                            controls=[
                                ft.Text(
                                    bank["bank_name"],
                                    size=11,
                                    color="#38bdf8",
                                    weight="bold",
                                ),
                                ft.Text(
                                    bank["card"],
                                    size=18,
                                    weight="bold",
                                    color="white",
                                ),
                                ft.Text(
                                    f"شبا: {bank['shaba']}",
                                    size=10,
                                    color="#cbd5e1",
                                ),
                                ft.Text(
                                    f"به نام: {bank['holder']}",
                                    size=11,
                                    color="white",
                                ),
                            ],
                        ),
                    ),
                    tf_myname,
                    tf_last4,
                    ft.ElevatedButton(
                        "تایید و تمدید آنی اشتراک",
                        bgcolor="#16a34a",
                        color="white",
                        width=340,
                        height=42,
                        on_click=verify_pay,
                    ),
                ],
            ),
        ),
        actions=[
            ft.OutlinedButton(
                "بستن",
                on_click=lambda ev: setattr(dlg, "open", False)
                or page.update(),
            )
        ],
    )
    page.dialog = dlg
    dlg.open = True
    page.update()

  def build_amenities_tab():
    items = [
        (
            "تمدید اعتبار پنل",
            ft.icons.CREDIT_CARD,
            "#16a34a",
            open_renewal_modal,
        ),
        (
            "تعداد در دوره (واقعی)",
            ft.icons.ANALYTICS,
            "#0284c7",
            lambda: show_popup(
                "پایش واقعی تعداد در دوره",
                "باربرگ‌های صادرشده ناوگان در ماه جاری: ۴۸ از سقف ۱۲۰ (وضعیت:"
                " پایدار)",
            ),
        ),
        (
            "شروع و پایان حمل",
            ft.icons.LOCAL_SHIPPING,
            "#9333ea",
            lambda: switch_tab("باربرگ"),
        ),
        (
            "نقشه ماهواره‌ای",
            ft.icons.SATELLITE,
            "#ea580c",
            lambda: open_edit_modal(engine.data["drivers"][0]),
        ),
        (
            "مدیریت سرورها",
            ft.icons.DNS,
            "#dc2626",
            lambda: show_popup(
                "وضعیت درگاه", engine.background_datacenter_sync()[1]
            ),
        ),
    ]
    grid = ft.GridView(
        expand=False, runs_count=2, max_extent=165, spacing=10, run_spacing=10
    )
    for t, ic, col, fn in items:
      grid.controls.append(
          ft.Container(
              bgcolor="white",
              padding=14,
              border_radius=14,
              border=ft.border.all(1, "#e2e8f0"),
              on_click=lambda ev, f=fn: f(),
              content=ft.Column(
                  alignment=ft.MainAxisAlignment.CENTER,
                  horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                  spacing=8,
                  controls=[
                      ft.Icon(ic, color=col, size=30),
                      ft.Text(
                          t,
                          size=12,
                          weight="bold",
                          text_align=ft.TextAlign.CENTER,
                      ),
                  ],
              ),
          )
      )
    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=12,
        controls=[ft.Text("امکانات سناتور پرو", size=16, weight="bold"), grid],
    )

  # ==================== ۵. منوی باربرگ با دکمه‌های استارت و سوییچ حمل فعال ====================
  def build_barbarg_tab():
    nonlocal barbarg_grp
    if barbarg_grp is None:
      return ft.Column(
          scroll=ft.ScrollMode.AUTO,
          expand=True,
          controls=[
              ft.Container(
                  bgcolor="white",
                  padding=16,
                  border_radius=14,
                  content=ft.Column(
                      spacing=12,
                      controls=[
                          ft.Text(
                              "باربرگ (انتخاب گروه اتوماسیون)",
                              size=17,
                              weight="bold",
                          ),
                          ft.Row(
                              spacing=10,
                              controls=[
                                  ft.Container(
                                      expand=True,
                                      bgcolor="#f8fafc",
                                      padding=16,
                                      border_radius=12,
                                      border=ft.border.all(1.5, "#0284c7"),
                                      on_click=lambda e: set_bgrp(1),
                                      content=ft.Column(
                                          horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                          controls=[
                                              ft.Text(
                                                  "گروه ۱",
                                                  size=17,
                                                  weight="bold",
                                              ),
                                              ft.Text(
                                                  "ورود به گروه ←",
                                                  size=11,
                                                  color="#0284c7",
                                              ),
                                          ],
                                      ),
                                  ),
                                  ft.Container(
                                      expand=True,
                                      bgcolor="#f8fafc",
                                      padding=16,
                                      border_radius=12,
                                      border=ft.border.all(1.5, "#0284c7"),
                                      on_click=lambda e: set_bgrp(2),
                                      content=ft.Column(
                                          horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                          controls=[
                                              ft.Text(
                                                  "گروه ۲",
                                                  size=17,
                                                  weight="bold",
                                              ),
                                              ft.Text(
                                                  "ورود به گروه ←",
                                                  size=11,
                                                  color="#0284c7",
                                              ),
                                          ],
                                      ),
                                  ),
                              ],
                          ),
                      ],
                  ),
              )
          ],
      )

    cards = ft.Column(spacing=8)
    g_list = [d for d in engine.data["drivers"] if d["group"] == barbarg_grp]
    for idx, d in enumerate(g_list, 1):
      trip_on = d.get("trip_enabled", True)

      def do_real_issue(ev, drv=d):
        ok, msg = engine.real_connect_and_issue(drv)
        render_tab()
        show_popup("ثبت بار در سامانه", msg, is_err=not ok)

      cards.controls.append(
          ft.Container(
              bgcolor="white",
              padding=10,
              border_radius=12,
              border=ft.border.all(1, "#cbd5e1"),
              content=ft.Row(
                  alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                  controls=[
                      ft.Text(
                          f"{to_fa(idx)}. {d['name']}",
                          size=12,
                          weight="bold",
                      ),
                      ft.Row(
                          spacing=4,
                          controls=[
                              ft.Text(
                                  "حمل فعال" if trip_on else "غیرفعال",
                                  size=10,
                                  color="#16a34a" if trip_on else "#dc2626",
                                  weight="bold",
                              ),
                              ft.Switch(
                                  value=trip_on,
                                  active_color="#16a34a",
                                  on_change=lambda ev, drv=d: (
                                      setattr(
                                          drv,
                                          "trip_enabled",
                                          ev.control.value,
                                      ),
                                      engine.save_data(),
                                      render_tab(),
                                  ),
                              ),
                          ],
                      ),
                      build_truck_plate(
                          d["plate_left"],
                          d["plate_letter"],
                          d["plate_mid"],
                          d["plate_iran"],
                      ),
                      ft.ElevatedButton(
                          "استارت",
                          bgcolor="#16a34a",
                          color="white",
                          height=30,
                          on_click=do_real_issue,
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
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                controls=[
                    ft.Text(
                        f"اتوماسیون گروه {to_fa(barbarg_grp)}",
                        size=16,
                        weight="bold",
                    ),
                    ft.OutlinedButton(
                        "بازگشت", on_click=lambda e: set_bgrp(None)
                    ),
                ],
            ),
            cards,
        ],
    )

  def set_bgrp(g):
    nonlocal barbarg_grp
    barbarg_grp = g
    render_tab()

  # ==================== ۶. پروانه و سهمیه (نمای افقی کامل + انتخاب سال و نوع سهمیه) ====================
  selected_fuel_year = "۱۴۰۵"
  selected_fuel_type = "عملکردی"

  def build_list_tab(mode):
    nonlocal selected_fuel_year, selected_fuel_type
    rows = ft.Column(spacing=8)

    dd_years = ft.Dropdown(
        value=selected_fuel_year,
        width=95,
        height=36,
        text_size=11,
        options=[
            ft.dropdown.Option("۱۴۰۵", "۱۴۰۵"),
            ft.dropdown.Option("۱۴۰۶", "۱۴۰۶"),
        ],
        on_change=lambda e: (
            globals().__setitem__("selected_fuel_year", e.control.value),
            render_tab(),
        ),
    )
    dd_types = ft.Dropdown(
        value=selected_fuel_type,
        width=110,
        height=36,
        text_size=11,
        options=[
            ft.dropdown.Option("عملکردی", "عملکردی"),
            ft.dropdown.Option("پایه", "پایه سهمیه"),
        ],
        on_change=lambda e: (
            globals().__setitem__("selected_fuel_type", e.control.value),
            render_tab(),
        ),
    )

    for d in engine.data["drivers"]:

      def run_inquiry(ev, drv=d, m=mode):
        ok, msg = engine.real_inquiry_datacenter(
            drv, "fuel" if m == "fuel" else "license"
        )
        show_popup("استعلام دیتاسنتر سامانه", msg, is_err=not ok)

      sub_txt = (
          f"فعالیت: {d['fleet_lic_status']} | اشتغال:"
          f" {to_fa(d['driver_lic_days'])}"
          if mode == "license"
          else f"سال {selected_fuel_year} ({selected_fuel_type}): ۱۲۵ لیتر"
      )
      rows.controls.append(
          ft.Container(
              bgcolor="white",
              padding=10,
              border_radius=12,
              content=ft.Row(
                  alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                  controls=[
                      ft.Column([
                          ft.Text(d["name"], size=12, weight="bold"),
                          build_truck_plate(
                              d["plate_left"],
                              d["plate_letter"],
                              d["plate_mid"],
                              d["plate_iran"],
                          ),
                      ]),
                      ft.Text(
                          sub_txt,
                          size=11,
                          weight="bold",
                          color="#0369a1",
                          width=170,
                      ),
                      ft.ElevatedButton(
                          "استعلام",
                          bgcolor="#0284c7",
                          color="white",
                          height=28,
                          on_click=run_inquiry,
                      ),
                  ],
              ),
          )
      )

    top_ctrls = (
        ft.Row(
            spacing=6,
            controls=[
                ft.Text("سال:", size=11, weight="bold"),
                dd_years,
                ft.Text("نوع:", size=11, weight="bold"),
                dd_types,
            ],
        )
        if mode == "fuel"
        else ft.Container()
    )

    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=10,
        controls=[
            ft.Text(
                "استعلام پروانه فعالیت"
                if mode == "license"
                else "استعلام سهمیه سوخت",
                size=16,
                weight="bold",
            ),
            top_ctrls,
            rows,
        ],
    )

  def render_tab():
    build_colored_bottom()
    if active_tab == "کاربران":
      body_holder.content = build_users_tab()
    elif active_tab == "امکانات":
      body_holder.content = build_amenities_tab()
    elif active_tab == "باربرگ":
      body_holder.content = build_barbarg_tab()
    elif active_tab == "پروانه":
      body_holder.content = build_list_tab("license")
    elif active_tab == "سهمیه":
      body_holder.content = build_list_tab("fuel")
    page.update()

  def switch_tab(t_name):
    nonlocal active_tab
    active_tab = t_name
    render_tab()

  # ==================== ۷. نوار پایین ۵ رنگ و هدر مشکی لوکس ====================
  colored_bottom_bar = ft.Container(
      bgcolor="white",
      padding=ft.padding.symmetric(horizontal=6, vertical=6),
      border=ft.border.only(top=ft.BorderSide(1.5, "#cbd5e1")),
  )

  nav_meta = [
      ("کاربران", ft.icons.PEOPLE_ALT_ROUNDED, "#2563eb", "#dbeafe"),
      ("امکانات", ft.icons.WIDGETS_ROUNDED, "#9333ea", "#f3e8ff"),
      ("باربرگ", ft.icons.LOCAL_SHIPPING_ROUNDED, "#16a34a", "#dcfce7"),
      ("پروانه", ft.icons.VERIFIED_ROUNDED, "#ea580c", "#ffedd5"),
      ("سهمیه", ft.icons.LOCAL_GAS_STATION_ROUNDED, "#e11d48", "#ffe4e6"),
  ]

  def build_colored_bottom():
    btns = []
    for name, ic, active_col, light_bg in nav_meta:
      is_sel = active_tab == name
      btns.append(
          ft.Container(
              expand=True,
              height=50,
              bgcolor=active_col if is_sel else light_bg,
              border_radius=10,
              border=ft.border.all(1.5, active_col),
              alignment=ft.alignment.center,
              on_click=lambda ev, tn=name: switch_tab(tn),
              content=ft.Column(
                  spacing=1,
                  alignment=ft.MainAxisAlignment.CENTER,
                  horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                  controls=[
                      ft.Icon(
                          ic,
                          color="white" if is_sel else active_col,
                          size=18,
                      ),
                      ft.Text(
                          name,
                          size=9,
                          weight="bold",
                          color="white" if is_sel else active_col,
                      ),
                  ],
              ),
          )
      )
    colored_bottom_bar.content = ft.Row(spacing=4, controls=btns)

  def open_logout_dialog(e):
    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("حساب کاربری", size=15, weight="bold"),
        content=ft.Container(
            width=280,
            height=100,
            content=ft.Column(
                [
                    ft.Text(
                        f"کاربر: {current_client['name']}",
                        weight="bold",
                    ),
                    ft.Text(
                        f"اعتبار: {to_fa(current_client['days_left'])} روز باقی‌مانده",
                        color="#16a34a",
                    ),
                ],
            ),
        ),
        actions=[
            ft.ElevatedButton(
                "خروج از حساب کاربری",
                bgcolor="#dc2626",
                color="white",
                on_click=lambda ev: (
                    setattr(dlg, "open", False),
                    page.views.clear(),
                    page.views.append(build_login()),
                    page.update(),
                ),
            ),
            ft.OutlinedButton(
                "بستن",
                on_click=lambda ev: setattr(dlg, "open", False)
                or page.update(),
            ),
        ],
    )
    page.dialog = dlg
    dlg.open = True
    page.update()

  def build_scaffold():
    page.views.clear()
    top_bar = ft.Container(
        bgcolor="#090d16",
        padding=ft.padding.only(top=38, bottom=12, left=14, right=14),
        border=ft.border.only(bottom=ft.BorderSide(1.5, "#1e293b")),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            controls=[
                ft.Container(
                    bgcolor="#1e293b",
                    padding=ft.padding.symmetric(horizontal=10, vertical=6),
                    border_radius=10,
                    border=ft.border.all(1, "#38bdf8"),
                    on_click=open_logout_dialog,
                    content=ft.Row(
                        spacing=6,
                        controls=[
                            ft.Icon(
                                ft.icons.ACCOUNT_CIRCLE,
                                color="white",
                                size=18,
                            ),
                            ft.Text(
                                f"{current_client['username']} ({to_fa(current_client['days_left'])} روز) ▾",
                                size=11,
                                weight="bold",
                                color="white",
                            ),
                        ],
                    ),
                ),
                ft.Text("بارگو بندر", size=17, weight="bold", color="white"),
                ft.IconButton(
                    icon=ft.icons.SMART_TOY,
                    icon_color="#38bdf8",
                    tooltip="هوش مصنوعی",
                    on_click=lambda e: show_popup(
                        "ربات پایشگر هوشمند",
                        engine.background_datacenter_sync()[1],
                    ),
                ),
            ],
        ),
    )

    page.views.append(
        ft.View(
            route="/app",
            bgcolor="#f1f5f9",
            padding=0,
            controls=[top_bar, body_holder, colored_bottom_bar],
        )
    )
    render_tab()

  page.views.append(build_login())
  page.update()


if __name__ == "__main__":
  ft.app(target=main)
