import random
import time
import traceback
import flet as ft

try:
  from engine import BarbargEngine, build_iran_plate, to_fa
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
  current_user = engine.data["clients"][0]
  active_tab = "کاربران"
  barbarg_grp = None
  amen_sub = None
  body_holder = ft.Container(expand=True, padding=10)

  def show_popup(title, msg, is_err=False):
    bg = "#fee2e2" if is_err else "#dcfce7"
    col = "#991b1b" if is_err else "#166534"
    dlg = ft.AlertDialog(
        modal=True,
        content_padding=0,
        content=ft.Container(
            width=320,
            bgcolor=bg,
            border_radius=14,
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
                        padding=10,
                        border_radius=8,
                        width=290,
                        content=ft.Text(
                            msg,
                            size=12,
                            weight="bold",
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ),
                    ft.ElevatedButton(
                        "متوجه شدم ←",
                        bgcolor="white",
                        color="#0f172a",
                        width=290,
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
    err = ft.Text("", color="#dc2626", size=12)

    def do_log(e):
      ok, c = engine.authenticate(tf_u.value, tf_p.value)
      if ok:
        nonlocal current_user
        current_user = c
        build_scaffold()
      else:
        err.value = "نام کاربری یا رمز اشتباه است!"
        page.update()

    return ft.View(
        route="/login",
        bgcolor="white",
        padding=24,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                width=330,
                padding=16,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                    controls=[
                        ft.Icon(
                            ft.icons.LOCAL_SHIPPING_ROUNDED,
                            color="#0d9488",
                            size=52,
                        ),
                        ft.Text(
                            "بارگو بندر",
                            size=24,
                            weight="bold",
                            color="#0d9488",
                        ),
                        tf_u,
                        tf_p,
                        ft.Container(
                            padding=10,
                            bgcolor="#f0fdf4",
                            border=ft.border.all(1.5, "#86efac"),
                            border_radius=10,
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(
                                        "✓ من ربات نیستم (تأیید شد)",
                                        size=12,
                                        weight="bold",
                                        color="#166534",
                                    ),
                                    ft.Icon(
                                        ft.icons.VERIFIED_USER,
                                        color="#0284c7",
                                        size=20,
                                    ),
                                ],
                            ),
                        ),
                        err,
                        ft.ElevatedButton(
                            "ورود به پنل",
                            bgcolor="#38bdf8",
                            color="white",
                            width=300,
                            height=44,
                            on_click=do_log,
                        ),
                    ],
                ),
            )
        ],
    )

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

    target_mode = ["origin"]
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
    pin_o = ft.Container(
        left=55,
        top=105,
        bgcolor="#be123c",
        padding=4,
        border_radius=6,
        content=ft.Text("📍 مبدأ", color="white", size=9, weight="bold"),
    )
    pin_d = ft.Container(
        left=185,
        top=35,
        bgcolor="#0f172a",
        padding=4,
        border_radius=6,
        content=ft.Text("🏁 مقصد", color="white", size=9, weight="bold"),
    )
    dist_txt = ft.Text(
        f"{drv['distance_km']} km", color="white", size=10, weight="bold"
    )
    map_box = ft.Container(
        width=330,
        height=160,
        bgcolor="#e0f2fe",
        border_radius=10,
        border=ft.border.all(1.5, "#0284c7"),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )

    def on_map_tap(ev: ft.TapEvent):
      lx = max(10, min(280, int(ev.local_x)))
      ly = max(10, min(130, int(ev.local_y)))
      clat = round(26.8500 - (ly / 160.0) * 0.3500, 5)
      clon = round(54.8000 + (lx / 330.0) * 0.2500, 5)
      if target_mode[0] == "origin":
        pin_o.left, pin_o.top = lx - 12, ly - 10
        tf_olat.value, tf_olon.value = str(clat), str(clon)
      else:
        pin_d.left, pin_d.top = lx - 12, ly - 10
        tf_dlat.value, tf_dlon.value = str(clat), str(clon)
      km = engine.calculate_distance(
          float(tf_olat.value),
          float(tf_olon.value),
          float(tf_dlat.value),
          float(tf_dlon.value),
      )
      drv["distance_km"] = km
      dist_txt.value = f"{km} km"
      page.update()

    map_box.content = ft.GestureDetector(
        on_tap_down=on_map_tap,
        content=ft.Stack(
            width=330,
            height=160,
            controls=[
                ft.Container(
                    left=0, top=125, width=330, height=35, bgcolor="#7dd3fc"
                ),
                ft.Container(
                    left=15, top=70, width=300, height=4, bgcolor="#fde047"
                ),
                ft.Container(
                    left=15,
                    top=12,
                    content=ft.Text(
                        "نقشه زنده OSM بارگو بندر (روی نقشه کلیک کنید)",
                        size=9,
                        weight="bold",
                    ),
                ),
                ft.Container(
                    left=110,
                    top=65,
                    bgcolor="#0284c7",
                    padding=5,
                    border_radius=8,
                    content=dist_txt,
                ),
                pin_o,
                pin_d,
            ],
        ),
    )

    dd_pack = ft.Dropdown(
        label="بسته‌بندی",
        value=drv["pack"],
        expand=True,
        options=[
            ft.dropdown.Option(p, p)
            for p in [
                "کارتن",
                "جعبه",
                "کیسه",
                "گونی",
                "جامبو",
                "بشکه",
                "رول",
                "فله",
                "عدل",
                "پالت",
            ]
        ],
    )
    tf_fare = ft.TextField(
        label="کرایه (ریال)", value=drv["fare"], expand=True
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
      drv["pack"], drv["fare"] = dd_pack.value, tf_fare.value
      engine.save_data()
      dlg.open = False
      render_tab()

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(f"ویرایش: {drv['name']}", size=15, weight="bold"),
        content=ft.Container(
            width=350,
            height=440,
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                spacing=8,
                controls=[
                    ft.Row([tf_nid, tf_pw]),
                    ft.Row([dd_grp, tf_mob]),
                    ft.Row([tf_pl_i, tf_pl_m, tf_pl_c, tf_pl_l]),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                        controls=[
                            ft.ElevatedButton(
                                "ثبت مبدأ",
                                bgcolor="#be123c",
                                color="white",
                                height=28,
                                on_click=lambda e: target_mode.__setitem__(
                                    0, "origin"
                                ),
                            ),
                            ft.ElevatedButton(
                                "ثبت مقصد",
                                bgcolor="#0f172a",
                                color="white",
                                height=28,
                                on_click=lambda e: target_mode.__setitem__(
                                    0, "dest"
                                ),
                            ),
                        ],
                    ),
                    map_box,
                    ft.Row([tf_olat, tf_olon]),
                    ft.Row([tf_dlat, tf_dlon]),
                    ft.Row([dd_pack, tf_fare]),
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

  def open_add_user(e):
    tf_nid = ft.TextField(label="کد ملی راننده")
    tf_pw = ft.TextField(label="رمز درگاه utcms.ir", value="Aa13611361##")
    tf_nm = ft.TextField(label="نام و نام خانوادگی")

    def save_new(ev):
      if not tf_nid.value.strip():
        return
      nd = dict(engine.data["drivers"][0])
      nd["id"] = len(engine.data["drivers"]) + 1
      nd["name"] = tf_nm.value.strip() or f"راننده {tf_nid.value[-4:]}"
      nd["national_id"] = tf_nid.value.strip()
      nd["password"] = tf_pw.value.strip()
      nd["plate_mid"] = str(random.randint(111, 989))
      engine.data["drivers"].insert(0, nd)
      engine.save_data()
      dlg.open = False
      render_tab()

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("افزودن کاربر به بارگو بندر", size=14, weight="bold"),
        content=ft.Container(
            width=320,
            height=190,
            content=ft.Column([tf_nid, tf_pw, tf_nm]),
        ),
        actions=[
            ft.ElevatedButton(
                "ثبت کاربر",
                bgcolor="#0284c7",
                color="white",
                on_click=save_new,
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

  def build_users_tab():
    rows = ft.Column(spacing=6)
    rows.controls.append(
        ft.Container(
            bgcolor="#f1f5f9",
            padding=8,
            border_radius=8,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("ردیف", size=11, weight="bold", width=26),
                    ft.Text("راننده", size=11, weight="bold", expand=True),
                    ft.Text("پلاک", size=11, weight="bold", width=145),
                    ft.Text("گروه", size=11, weight="bold", width=28),
                    ft.Text("عملیات", size=11, weight="bold", width=56),
                ],
            ),
        )
    )
    for idx, drv in enumerate(engine.data["drivers"], start=1):
      on = drv["active"]
      pill = ft.Container(
          width=52,
          height=22,
          bgcolor="#22c55e" if on else "#ef4444",
          border_radius=11,
          alignment=ft.alignment.center,
          on_click=lambda ev, d=drv: (
              setattr(d, "active", not d["active"]),
              engine.save_data(),
              render_tab(),
          ),
          content=ft.Text(
              "ON" if on else "OFF", color="white", size=9, weight="bold"
          ),
      )
      rows.controls.append(
          ft.Container(
              bgcolor="white" if on else "#fff1f2",
              padding=6,
              border_radius=10,
              border=ft.border.all(1, "#e2e8f0"),
              content=ft.Row(
                  alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                  controls=[
                      ft.Text(to_fa(idx), size=11, weight="bold", width=22),
                      ft.Column(
                          spacing=1,
                          expand=True,
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                          controls=[
                              ft.Text(drv["name"], size=12, weight="bold"),
                              ft.Text(
                                  to_fa(drv["national_id"]),
                                  size=10,
                                  color="#64748b",
                              ),
                          ],
                      ),
                      build_iran_plate(
                          drv["plate_left"],
                          drv["plate_letter"],
                          drv["plate_mid"],
                          drv["plate_iran"],
                          True,
                      ),
                      ft.Text(
                          to_fa(drv["group"]),
                          size=11,
                          weight="bold",
                          width=22,
                      ),
                      ft.Column(
                          spacing=3,
                          controls=[
                              pill,
                              ft.Container(
                                  width=52,
                                  height=22,
                                  bgcolor="#0284c7",
                                  border_radius=6,
                                  alignment=ft.alignment.center,
                                  on_click=lambda ev, d=drv: open_edit_modal(d),
                                  content=ft.Text(
                                      "ویرایش",
                                      color="white",
                                      size=9,
                                      weight="bold",
                                  ),
                              ),
                              ft.Container(
                                  width=52,
                                  height=20,
                                  bgcolor="#fff1f2",
                                  border_radius=6,
                                  alignment=ft.alignment.center,
                                  on_click=lambda ev, d=drv: (
                                      engine.data["drivers"].remove(d),
                                      engine.save_data(),
                                      render_tab(),
                                  ),
                                  content=ft.Text(
                                      "حذف",
                                      color="#e11d48",
                                      size=9,
                                      weight="bold",
                                  ),
                              ),
                          ],
                      ),
                  ],
              ),
          )
      )
    tot = len(engine.data["drivers"])
    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        controls=[
            ft.Container(
                bgcolor="white",
                padding=12,
                border_radius=14,
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.Text("مدیریت کاربران", size=17, weight="bold"),
                        ft.Row(
                            spacing=6,
                            controls=[
                                ft.OutlinedButton(
                                    "افزودن دستی",
                                    expand=True,
                                    on_click=open_add_user,
                                ),
                                ft.ElevatedButton(
                                    "افزودن کاربر",
                                    bgcolor="#0284c7",
                                    color="white",
                                    expand=True,
                                    on_click=open_add_user,
                                ),
                                ft.OutlinedButton(
                                    "افزودن گروهی",
                                    expand=True,
                                    on_click=open_add_user,
                                ),
                            ],
                        ),
                        ft.Text(
                            f"نمایش: {to_fa(tot)} از {to_fa(tot)} | سقف: ۵۰ |"
                            f" باقی‌مانده: {to_fa(50-tot)}",
                            size=11,
                            color="#475569",
                            weight="bold",
                        ),
                        rows,
                    ],
                ),
            )
        ],
    )

  def build_amenities_tab():
    nonlocal amen_sub
    if amen_sub == "trip":
      rows = ft.Column(spacing=8)
      for d in engine.data["drivers"]:
        rows.controls.append(
            ft.Container(
                bgcolor="white",
                padding=10,
                border_radius=12,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column([
                            ft.Text(d["name"], size=12, weight="bold"),
                            build_iran_plate(
                                d["plate_left"],
                                d["plate_letter"],
                                d["plate_mid"],
                                d["plate_iran"],
                                True,
                            ),
                        ]),
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.ElevatedButton(
                                    "شروع حمل",
                                    bgcolor="#0284c7",
                                    color="white",
                                    height=28,
                                    on_click=lambda ev, drv=d: show_popup(
                                        "موفق",
                                        engine.real_login_and_action(
                                            drv, "start_trip"
                                        )[1],
                                    ),
                                ),
                                ft.ElevatedButton(
                                    "پایان حمل",
                                    bgcolor="#0d9488",
                                    color="white",
                                    height=28,
                                    on_click=lambda ev, drv=d: show_popup(
                                        "موفق",
                                        engine.real_login_and_action(
                                            drv, "end_trip"
                                        )[1],
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
            )
        )
      return ft.Column(
          scroll=ft.ScrollMode.AUTO,
          expand=True,
          controls=[
              ft.Row(
                  alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                  controls=[
                      ft.Text(
                          "شروع و پایان حمل", size=16, weight="bold"
                      ),
                      ft.ElevatedButton(
                          "← بازگشت",
                          bgcolor="#0ea5e9",
                          color="white",
                          on_click=lambda e: set_amen(None),
                      ),
                  ],
              ),
              rows,
          ],
      )

    items = [
        (
            "شروع و پایان حمل",
            ft.icons.LOCAL_SHIPPING,
            "#0284c7",
            lambda: set_amen("trip"),
        ),
        (
            "تعیین نوع بار",
            ft.icons.INVENTORY_2,
            "#16a34a",
            lambda: open_edit_modal(engine.data["drivers"][0]),
        ),
        (
            "آدرس‌ها و نقشه",
            ft.icons.LOCATION_ON,
            "#0369a1",
            lambda: open_edit_modal(engine.data["drivers"][0]),
        ),
        (
            "تاریخچه صدور",
            ft.icons.HISTORY,
            "#0f172a",
            lambda: switch_tab("باربرگ"),
        ),
        (
            "شروع هوشمند",
            ft.icons.BOLT,
            "#6d28d9",
            lambda: switch_tab("باربرگ"),
        ),
        (
            "مدیریت سرورها",
            ft.icons.DNS,
            "#dc2626",
            lambda: show_popup(
                "وضعیت درگاه", engine.connect_utcms_session()["msg"]
            ),
        ),
    ]
    grid = ft.GridView(
        expand=False, runs_count=3, max_extent=125, spacing=8, run_spacing=8
    )
    for t, ic, col, fn in items:
      grid.controls.append(
          ft.Container(
              bgcolor="white",
              padding=10,
              border_radius=12,
              border=ft.border.all(1, "#e2e8f0"),
              on_click=lambda ev, f=fn: f(),
              content=ft.Column(
                  alignment=ft.MainAxisAlignment.CENTER,
                  horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                  spacing=6,
                  controls=[
                      ft.Icon(ic, color=col, size=26),
                      ft.Text(
                          t,
                          size=11,
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
        controls=[
            ft.Text("امکانات بارگو بندر", size=17, weight="bold"),
            grid,
        ],
    )

  def set_amen(v):
    nonlocal amen_sub
    amen_sub = v
    render_tab()

  def build_barbarg_tab():
    nonlocal barbarg_grp
    if barbarg_grp is None:
      return ft.Column(
          scroll=ft.ScrollMode.AUTO,
          expand=True,
          controls=[
              ft.Container(
                  bgcolor="white",
                  padding=14,
                  border_radius=14,
                  content=ft.Column(
                      spacing=12,
                      controls=[
                          ft.Text("باربرگ (انتخاب گروه)", size=17, weight="bold"),
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
                                                  "● در حال اجرا",
                                                  size=10,
                                                  color="#16a34a",
                                                  weight="bold",
                                              ),
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
                                                  "● در حال اجرا",
                                                  size=10,
                                                  color="#16a34a",
                                                  weight="bold",
                                              ),
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
    for idx, d in enumerate(
        [x for x in engine.data["drivers"] if x["group"] == barbarg_grp], 1
    ):
      cards.controls.append(
          ft.Container(
              bgcolor="white",
              padding=10,
              border_radius=12,
              content=ft.Row(
                  alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                  controls=[
                      ft.Column([
                          ft.Text(
                              f"{to_fa(idx)}. {d['name']}",
                              size=12,
                              weight="bold",
                          ),
                          ft.Text(
                              d.get("state_text", "آماده"),
                              size=10,
                              color="#16a34a",
                          ),
                      ]),
                      ft.IconButton(
                          icon=ft.icons.PLAY_CIRCLE_FILL,
                          icon_color="#16a34a",
                          on_click=lambda ev, drv=d: show_popup(
                              "موفق",
                              engine.real_login_and_action(drv, "issue")[1],
                          ),
                      ),
                      build_iran_plate(
                          d["plate_left"],
                          d["plate_letter"],
                          d["plate_mid"],
                          d["plate_iran"],
                          True,
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
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
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
            ft.Row(
                spacing=6,
                controls=[
                    ft.ElevatedButton(
                        "▶ شروع گروهی",
                        bgcolor="#dcfce7",
                        color="#15803d",
                        on_click=lambda e: show_popup(
                            "شروع گروهی",
                            engine.connect_utcms_session()["msg"],
                        ),
                    ),
                    ft.ElevatedButton(
                        "⏹ توقف",
                        bgcolor="#fee2e2",
                        color="#dc2626",
                        on_click=lambda e: show_popup(
                            "توقف", "عملیات گروه متوقف شد.", True
                        ),
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

  def build_list_tab(mode):
    rows = ft.Column(spacing=8)
    for d in engine.data["drivers"]:
      sub_txt = (
          f"فعالیت: {d['fleet_lic_status']} | اشتغال: {to_fa(d['driver_lic_days'])}"
          if mode == "license"
          else f"اول: {to_fa(d['fuel_stage1'])} | دوم: {to_fa(d['fuel_stage2'])}"
      )
      rows.controls.append(
          ft.Container(
              bgcolor="white",
              padding=10,
              border_radius=12,
              content=ft.Row(
                  alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                  controls=[
                      ft.Column([
                          ft.Text(d["name"], size=12, weight="bold"),
                          build_iran_plate(
                              d["plate_left"],
                              d["plate_letter"],
                              d["plate_mid"],
                              d["plate_iran"],
                              True,
                          ),
                      ]),
                      ft.Text(sub_txt, size=10, weight="bold"),
                      ft.ElevatedButton(
                          "استعلام",
                          bgcolor="#0284c7",
                          color="white",
                          height=28,
                          on_click=lambda ev, drv=d: show_popup(
                              "پاسخ سامانه",
                              engine.real_login_and_action(drv, mode)[1],
                          ),
                      ),
                  ],
              ),
          )
      )
    title_str = (
        "استعلام پروانه‌ها"
        if mode == "license"
        else "استعلام سهمیه سوخت (آبان ۱۴۰۵)"
    )
    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=10,
        controls=[ft.Text(title_str, size=16, weight="bold"), rows],
    )

  def render_tab():
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
    nonlocal active_tab, amen_sub
    active_tab = t_name
    amen_sub = None
    render_tab()

  def build_scaffold():
    page.views.clear()
    top_bar = ft.Container(
        bgcolor="white",
        padding=ft.padding.only(top=36, bottom=10, left=14, right=14),
        border=ft.border.only(bottom=ft.BorderSide(1, "#e2e8f0")),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(
                    f"👤 {current_user['username']} ({to_fa(current_user['days_left'])} روز)",
                    size=12,
                    weight="bold",
                    color="#0284c7",
                ),
                ft.Text(
                    "بارگو بندر", size=18, weight="bold", color="#0f172a"
                ),
                ft.IconButton(
                    icon=ft.icons.CLOUD_SYNC,
                    icon_color="#0284c7",
                    on_click=lambda e: show_popup(
                        "وضعیت درگاه utcms.ir",
                        engine.connect_utcms_session()["msg"],
                    ),
                ),
            ],
        ),
    )
    nav_bar = ft.NavigationBar(
        selected_index=0,
        bgcolor="white",
        destinations=[
            ft.NavigationDestination(icon=ft.icons.PEOPLE, label="کاربران"),
            ft.NavigationDestination(icon=ft.icons.WIDGETS, label="امکانات"),
            ft.NavigationDestination(
                icon=ft.icons.LOCAL_SHIPPING, label="باربرگ"
            ),
            ft.NavigationDestination(icon=ft.icons.ASSIGNMENT, label="پروانه"),
            ft.NavigationDestination(
                icon=ft.icons.LOCAL_GAS_STATION, label="سهمیه"
            ),
        ],
        on_change=lambda ev: switch_tab(
            ["کاربران", "امکانات", "باربرگ", "پروانه", "سهمیه"][
                ev.control.selected_index
            ]
        ),
    )
    page.views.append(
        ft.View(
            route="/app",
            bgcolor="#f1f5f9",
            padding=0,
            controls=[top_bar, body_holder, nav_bar],
        )
    )
    render_tab()

  page.views.append(build_login())
  page.update()


if __name__ == "__main__":
  ft.app(target=main)
