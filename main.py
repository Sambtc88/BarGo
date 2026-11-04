import time
import traceback
import flet as ft

try:
  from engine import BarbargEngine
except Exception:
  BarbargEngine = None
  ENGINE_ERR = traceback.format_exc()


def build_iran_plate(left_2, letter, mid_3, iran_code, size_mode="compact"):
  """ساخت پلاک استاندارد ایران در سه سایز: کوچک (جدول)، متوسط و بزرگ (ویرایش)"""
  if size_mode == "mini":
    h, w, iran_w, flag_w, num_sz, ir_sz = 30, 128, 28, 18, 12, 9
  elif size_mode == "large":
    h, w, iran_w, flag_w, num_sz, ir_sz = 52, 275, 54, 34, 21, 15
  else:
    h, w, iran_w, flag_w, num_sz, ir_sz = 34, 148, 32, 22, 13, 10

  return ft.Container(
      height=h,
      width=w,
      bgcolor="white",
      border=ft.border.all(1.5, "#0f172a"),
      border_radius=6,
      clip_behavior=ft.ClipBehavior.HARD_EDGE,
      content=ft.Row(
          spacing=0,
          controls=[
              # کادر راست: ایران ۸۴
              ft.Container(
                  width=iran_w,
                  height=h,
                  bgcolor="white",
                  border=ft.border.only(left=ft.BorderSide(1.2, "#0f172a")),
                  alignment=ft.alignment.center,
                  content=ft.Column(
                      spacing=0,
                      alignment=ft.MainAxisAlignment.CENTER,
                      horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                      controls=[
                          ft.Text(
                              "ایران",
                              size=7 if size_mode != "large" else 9,
                              weight="bold",
                              color="#0f172a",
                          ),
                          ft.Text(
                              str(iran_code),
                              size=ir_sz,
                              weight="bold",
                              color="#0f172a",
                          ),
                      ],
                  ),
              ),
              # کادر وسط: ۵۳ ع ۸۶۳
              ft.Container(
                  expand=True,
                  height=h,
                  bgcolor="white",
                  alignment=ft.alignment.center,
                  content=ft.Row(
                      alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                      vertical_alignment=ft.CrossAxisAlignment.CENTER,
                      controls=[
                          ft.Text(
                              str(mid_3),
                              size=num_sz,
                              weight="bold",
                              color="#0f172a",
                          ),
                          ft.Text(
                              str(letter),
                              size=num_sz,
                              weight="bold",
                              color="#b91c1c",
                          ),
                          ft.Text(
                              str(left_2),
                              size=num_sz,
                              weight="bold",
                              color="#0f172a",
                          ),
                      ],
                  ),
              ),
              # نوار پرچم آبی چپ
              ft.Container(
                  width=flag_w,
                  height=h,
                  bgcolor="#0369a1",
                  alignment=ft.alignment.center,
                  content=ft.Column(
                      spacing=1,
                      alignment=ft.MainAxisAlignment.CENTER,
                      horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                      controls=[
                          ft.Container(width=10, height=2, bgcolor="#22c55e"),
                          ft.Container(width=10, height=2, bgcolor="white"),
                          ft.Container(width=10, height=2, bgcolor="#ef4444"),
                          ft.Text(
                              "I.R.",
                              size=5,
                              color="white",
                              weight="bold",
                          ),
                      ],
                  ),
              ),
          ],
      ),
  )


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
  current_user = {
      "username": "Davood",
      "name": "داود پاپراس",
      "limit": 50,
      "days_left": 27,
      "role": "admin",
  }

  # متغیرهای وضعیت صفحات داخلی
  active_tab = "کاربران"
  amenities_subpage = "main"  # main | start_end | cargo_rot | addresses | servers | my_accounts | history
  barbarg_selected_group = None  # None | 1 | 2
  selected_fuel_month = "آبان ۱۴۰۵"
  user_search_q = ""
  user_group_filter = "all"

  body_holder = ft.Container(expand=True, bgcolor="#f1f5f9", padding=10)

  def show_toast(msg, bg="#0f172a"):
    page.snack_bar = ft.SnackBar(
        content=ft.Text(msg, color="white", size=12, weight="bold"),
        bgcolor=bg,
        duration=2500,
    )
    page.snack_bar.open = True
    page.update()

  def show_result_modal(title_txt, msg_txt, is_success=True, time_str=""):
    """پاپ‌آپ نتیجه عملیات یا خطاهای پلاک دقیقاً مشابه ویدیو (متوجه شدم <-)"""
    t_now = time_str or time.strftime("%H:%M:%S")
    header_bg = "#d1fae5" if is_success else "#dbeafe"
    title_col = "#065f46" if is_success else "#1e3a8a"
    icon_item = (
        ft.Icon(ft.icons.CHECK_CIRCLE, color="#10b981", size=26)
        if is_success
        else ft.Icon(ft.icons.INFO, color="#2563eb", size=26)
    )

    dlg = ft.AlertDialog(
        modal=True,
        bgcolor=header_bg,
        shape=ft.RoundedRectangleBorder(radius=16),
        content=ft.Container(
            width=340,
            padding=6,
            content=ft.Column(
                tight=True,
                spacing=10,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                title_txt,
                                size=16,
                                weight="bold",
                                color=title_col,
                            ),
                            icon_item,
                        ],
                    ),
                    ft.Container(
                        bgcolor="white",
                        padding=10,
                        border_radius=10,
                        content=ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text(
                                    f"🕒 {t_now}",
                                    size=11,
                                    color="#64748b",
                                ),
                                ft.Text(
                                    msg_txt,
                                    size=12,
                                    weight="bold",
                                    color="#0f172a",
                                ),
                            ],
                        ),
                    ),
                    ft.ElevatedButton(
                        "متوجه شدم ←",
                        bgcolor="#99f6e4" if is_success else "#bfdbfe",
                        color="#0f172a",
                        width=320,
                        height=40,
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

  # =========================================================================
  # ۱. صفحه لاگین دقیقاً مشابه ابتدای ویدیو (با تیک من ربات نیستم و قوانین)
  # =========================================================================
  def build_login_view():
    tf_u = ft.TextField(
        hint_text="نام کاربری",
        value="Davood",
        bgcolor="#f1f5f9",
        border_color="#cbd5e1",
        border_radius=10,
        text_size=14,
        height=48,
    )
    tf_p = ft.TextField(
        hint_text="کلمه عبور",
        value="1234",
        password=True,
        can_reveal_password=True,
        bgcolor="#f1f5f9",
        border_color="#cbd5e1",
        border_radius=10,
        text_size=14,
        height=48,
    )

    robot_verified = True
    robot_icon = ft.Icon(ft.icons.CHECK_BOX, color="#10b981", size=26)
    robot_sub = ft.Text(
        "تأیید شد – می‌توانید وارد شوید", size=10, color="#059669"
    )

    def toggle_robot(e):
      nonlocal robot_verified
      robot_verified = not robot_verified
      robot_icon.name = (
          ft.icons.CHECK_BOX
          if robot_verified
          else ft.icons.CHECK_BOX_OUTLINE_BLANK
      )
      robot_icon.color = "#10b981" if robot_verified else "#94a3b8"
      robot_sub.value = (
          "تأیید شد – می‌توانید وارد شوید"
          if robot_verified
          else "برای ادامه، این گزینه را تأیید کنید"
      )
      page.update()

    robot_card = ft.Container(
        bgcolor="#ecfdf5",
        border=ft.border.all(1, "#6ee7b7"),
        border_radius=12,
        padding=10,
        on_click=toggle_robot,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        robot_icon,
                        ft.Column(
                            spacing=1,
                            controls=[
                                ft.Text(
                                    "من ربات نیستم",
                                    size=13,
                                    weight="bold",
                                    color="#0f172a",
                                ),
                                robot_sub,
                            ],
                        ),
                    ],
                ),
                ft.Column(
                    spacing=0,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(
                            ft.icons.VERIFIED_USER_OUTLINED,
                            color="#0284c7",
                            size=18,
                        ),
                        ft.Text("امن", size=9, color="#64748b"),
                    ],
                ),
            ],
        ),
    )

    chk_rules = ft.Checkbox(
        label="قوانین را مطالعه و قبول دارم",
        value=True,
        active_color="#0284c7",
    )
    err_lbl = ft.Text("", color="#dc2626", size=12, weight="bold")
    login_btn = ft.ElevatedButton(
        "ورود",
        bgcolor="#0ea5e9",
        color="white",
        width=340,
        height=46,
    )

    def do_login(e):
      if not robot_verified or not chk_rules.value:
        err_lbl.value = "لطفاً تیک امنیتی و قوانین را تأیید نمایید."
        page.update()
        return
      login_btn.text = "در حال بررسی..."
      page.update()
      ok, c_info = engine.authenticate(tf_u.value.strip(), tf_p.value.strip())
      if ok:
        nonlocal current_user
        current_user = c_info
        build_main_shell()
      else:
        login_btn.text = "ورود"
        err_lbl.value = "نام کاربری یا کلمه عبور نادرست است!"
        page.update()

    login_btn.on_click = do_login

    return ft.View(
        route="/login",
        bgcolor="#f8fafc",
        padding=24,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                width=350,
                bgcolor="white",
                padding=24,
                border_radius=20,
                border=ft.border.all(1, "#e2e8f0"),
                shadow=ft.BoxShadow(blur_radius=20, color=ft.colors.BLACK12),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                    controls=[
                        # لوگوی اختصاصی تاج/کامیون بارگو بندر
                        ft.Container(
                            width=72,
                            height=72,
                            bgcolor="#0d9488",
                            border_radius=20,
                            alignment=ft.alignment.center,
                            content=ft.Icon(
                                ft.icons.LOCAL_SHIPPING_ROUNDED,
                                color="white",
                                size=40,
                            ),
                        ),
                        ft.Text(
                            "بارگو بندر",
                            size=22,
                            weight="bold",
                            color="#0d9488",
                        ),
                        ft.Container(
                            alignment=ft.alignment.center_right,
                            content=ft.Text(
                                "ورود",
                                size=15,
                                weight="bold",
                                color="#0f172a",
                            ),
                        ),
                        tf_u,
                        tf_p,
                        robot_card,
                        chk_rules,
                        err_lbl,
                        login_btn,
                    ],
                ),
            )
        ],
    )

  # =========================================================================
  # ۲. دیالوگ ویرایش کامل کاربر + نقشه زنده OSM (ثانیه ۰:۱۴ تا ۰:۵۷ ویدیو)
  # =========================================================================
  def open_user_edit_dialog(drv):
    tf_login_nid = ft.TextField(
        label="کد ملی ورود",
        value=drv.get("login_nid", drv["national_id"]),
        text_size=12,
        expand=True,
    )
    tf_pass = ft.TextField(
        label="رمز عبور",
        value=drv["password"],
        text_size=12,
        expand=True,
    )
    tf_nid = ft.TextField(
        label="کد ملی راننده",
        value=drv["national_id"],
        text_size=12,
        expand=True,
    )
    tf_group = ft.TextField(
        label="گروه", value=str(drv["group"]), text_size=12, width=80
    )
    dd_status = ft.Dropdown(
        label="وضعیت",
        value="فعال" if drv["active"] else "غیرفعال",
        width=110,
        text_size=12,
        options=[
            ft.dropdown.Option("فعال", "فعال"),
            ft.dropdown.Option("غیرفعال", "غیرفعال"),
        ],
    )
    tf_ref = ft.TextField(
        label="معرف",
        hint_text="یادداشت معرف",
        value=drv.get("referrer", ""),
        text_size=12,
        expand=True,
    )
    tf_mob = ft.TextField(
        label="موبایل فرستنده",
        value=drv["mobile"],
        text_size=12,
        expand=True,
    )

    # پلاک
    tf_pl_left = ft.TextField(
        label="دو رقم", value=drv["plate_left"], width=68, text_size=12
    )
    tf_pl_let = ft.TextField(
        label="حرف", value=drv["plate_letter"], width=55, text_size=12
    )
    tf_pl_mid = ft.TextField(
        label="سه رقم", value=drv["plate_mid"], width=78, text_size=12
    )
    tf_pl_ir = ft.TextField(
        label="ایران", value=drv["plate_iran"], width=65, text_size=12
    )

    # فرستنده و گیرنده
    tf_s_first = ft.TextField(
        label="نام فرستنده",
        value=drv.get("sender_first", drv["name"].split()[0]),
        text_size=12,
        expand=True,
    )
    tf_s_last = ft.TextField(
        label="نام خانوادگی فرستنده",
        value=drv.get("sender_last", drv["name"]),
        text_size=12,
        expand=True,
    )
    tf_r_first = ft.TextField(
        label="نام گیرنده",
        value=drv.get("receiver_first", "علی"),
        text_size=12,
        expand=True,
    )
    tf_r_last = ft.TextField(
        label="نام خانوادگی گیرنده",
        value=drv.get("receiver_last", "نجفی"),
        text_size=12,
        expand=True,
    )
    tf_r_mob = ft.TextField(
        label="موبایل گیرنده",
        value=drv.get("receiver_mobile", "09121480574"),
        text_size=12,
        expand=True,
    )

    # آدرس، مختصات و نقشه زنده
    map_mode_select = "origin"  # origin | dest
    current_zoom = 14
    selected_layer = drv.get("map_layer", "OSM سریع")

    tf_search_place = ft.TextField(
        hint_text="نام استان یا آدرس... (مثال: بندر کنگ، گزیر، باورد)",
        text_size=12,
        height=40,
        expand=True,
    )
    tf_o_addr = ft.TextField(
        label="آدرس مبدأ",
        value=drv.get("origin_addr", ""),
        text_size=11,
    )
    tf_d_addr = ft.TextField(
        label="آدرس مقصد",
        value=drv.get("dest_addr", ""),
        text_size=11,
    )
    tf_o_lat = ft.TextField(
        label="lat مبدأ",
        value=str(drv["origin_lat"]),
        text_size=11,
        expand=True,
    )
    tf_o_lon = ft.TextField(
        label="lng مبدأ",
        value=str(drv["origin_lon"]),
        text_size=11,
        expand=True,
    )
    tf_d_lat = ft.TextField(
        label="lat مقصد",
        value=str(drv["dest_lat"]),
        text_size=11,
        expand=True,
    )
    tf_d_lon = ft.TextField(
        label="lng مقصد",
        value=str(drv["dest_lon"]),
        text_size=11,
        expand=True,
    )
    tf_o_city = ft.TextField(
        label="شهر مبدأ",
        value=drv.get("origin_city", "بندر لنگه"),
        text_size=11,
        expand=True,
    )
    tf_o_nb = ft.TextField(
        label="خیابان / محله مبدأ",
        value=drv.get("origin_neighborhood", "بندر کنگ"),
        text_size=11,
        expand=True,
    )
    tf_d_city = ft.TextField(
        label="شهرستان مقصد",
        value=drv.get("dest_city", "بندر لنگه"),
        text_size=11,
        expand=True,
    )
    tf_d_nb = ft.TextField(
        label="خیابان / محله مقصد",
        value=drv.get("dest_neighborhood", "مهرگان پایین"),
        text_size=11,
        expand=True,
    )

    map_status_lbl = ft.Text(
        "کلیک بعدی روی نقشه یا جابجایی اسلایدر به عنوان مبدأ ثبت می‌شود.",
        size=11,
        color="#0369a1",
        weight="bold",
    )
    layer_badge = ft.Container(
        bgcolor="#0284c7",
        padding=ft.padding.symmetric(horizontal=8, vertical=3),
        border_radius=8,
        content=ft.Text(
            selected_layer, color="white", size=10, weight="bold"
        ),
    )
    dist_chip = ft.Container(
        bgcolor="#0284c7",
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
        border_radius=12,
        content=ft.Text(
            f"{drv['distance_km']} km", color="white", size=11, weight="bold"
        ),
    )

    # تصویر زنده کاشی نقشه از سرور OSM / Esri
    live_map_img = ft.Image(
        src=engine.get_live_map_tile_url(
            drv["origin_lat"], drv["origin_lon"], current_zoom, selected_layer
        ),
        width=360,
        height=185,
        fit=ft.ImageFit.COVER,
        border_radius=10,
    )

    def refresh_map_tile():
      try:
        lat = (
            float(tf_o_lat.value)
            if map_mode_select == "origin"
            else float(tf_d_lat.value)
        )
        lon = (
            float(tf_o_lon.value)
            if map_mode_select == "origin"
            else float(tf_d_lon.value)
        )
        live_map_img.src = engine.get_live_map_tile_url(
            lat, lon, current_zoom, selected_layer
        )
        km = engine.calculate_distance(
            float(tf_o_lat.value),
            float(tf_o_lon.value),
            float(tf_d_lat.value),
            float(tf_d_lon.value),
        )
        drv["distance_km"] = km
        dist_chip.content.value = f"{km} km"
        page.update()
      except Exception:
        pass

    def shift_coordinates(dlat, dlon):
      """اسکرول زنده روی نقشه با دکمه‌های جهتی و دریافت خودکار نام خیابان"""
      try:
        if map_mode_select == "origin":
          nlat = round(float(tf_o_lat.value) + dlat, 6)
          nlon = round(float(tf_o_lon.value) + dlon, 6)
          tf_o_lat.value = str(nlat)
          tf_o_lon.value = str(nlon)
          map_status_lbl.value = "مبدأ ثبت شد؛ در حال دریافت آدرس..."
          page.update()
          addr_str, c_str, sub_str = engine.reverse_geocode_osm(nlat, nlon)
          tf_o_addr.value = addr_str
          tf_o_city.value = c_str
          tf_o_nb.value = sub_str
          map_status_lbl.value = f"مبدأ روی نقشه بروز شد ({sub_str})"
        else:
          nlat = round(float(tf_d_lat.value) + dlat, 6)
          nlon = round(float(tf_d_lon.value) + dlon, 6)
          tf_d_lat.value = str(nlat)
          tf_d_lon.value = str(nlon)
          map_status_lbl.value = "مقصد ثبت شد؛ در حال دریافت آدرس..."
          page.update()
          addr_str, c_str, sub_str = engine.reverse_geocode_osm(nlat, nlon)
          tf_d_addr.value = addr_str
          tf_d_city.value = c_str
          tf_d_nb.value = sub_str
          map_status_lbl.value = f"مقصد روی نقشه بروز شد ({sub_str})"
        refresh_map_tile()
      except Exception:
        pass

    def do_search_map(e):
      q = tf_search_place.value.strip()
      if not q:
        return
      lat, lon, disp, c_name, sub_name = engine.search_address_osm(q)
      if map_mode_select == "origin":
        tf_o_lat.value, tf_o_lon.value = str(lat), str(lon)
        tf_o_addr.value, tf_o_city.value, tf_o_nb.value = disp, c_name, sub_name
      else:
        tf_d_lat.value, tf_d_lon.value = str(lat), str(lon)
        tf_d_addr.value, tf_d_city.value, tf_d_nb.value = disp, c_name, sub_name
      map_status_lbl.value = f"مکان «{q}» روی نقشه پیدا و ثبت شد."
      refresh_map_tile()

    # انتخاب نوع نقشه (۹ لایه دقیقاً مشابه ثانیه ۰:۳۴ ویدیو)
    dd_map_layer = ft.Dropdown(
        label="انتخاب نقشه",
        value=selected_layer,
        text_size=12,
        options=[
            ft.dropdown.Option("مپ پیش فرض بارگو", "مپ پیش فرض بارگو"),
            ft.dropdown.Option("BarGo سریع", "BarGo سریع"),
            ft.dropdown.Option("BarGo روشن", "BarGo روشن"),
            ft.dropdown.Option("OSM سریع", "OSM سریع"),
            ft.dropdown.Option("OpenStreetMap", "OpenStreetMap"),
            ft.dropdown.Option("Esri خیابانی", "Esri خیابانی"),
            ft.dropdown.Option("Esri توپو", "Esri توپو"),
            ft.dropdown.Option("ماهواره‌ای Esri", "ماهواره‌ای Esri"),
            ft.dropdown.Option("توپوگرافی", "توپوگرافی"),
        ],
    )

    def on_layer_change(e):
      nonlocal selected_layer
      selected_layer = dd_map_layer.value
      layer_badge.content.value = selected_layer
      refresh_map_tile()

    dd_map_layer.on_change = on_layer_change

    btn_mode_orig = ft.ElevatedButton(
        "ثبت مبدأ روی نقشه",
        bgcolor="#0284c7",
        color="white",
        height=30,
        on_click=lambda e: (
            setattr(btn_mode_orig, "bgcolor", "#0284c7"),
            setattr(btn_mode_dest, "bgcolor", "#94a3b8"),
            refresh_map_tile(),
        ),
    )
    btn_mode_dest = ft.ElevatedButton(
        "ثبت مقصد روی نقشه",
        bgcolor="#94a3b8",
        color="white",
        height=30,
    )

    def set_mode_orig(e):
      nonlocal map_mode_select
      map_mode_select = "origin"
      btn_mode_orig.bgcolor = "#0284c7"
      btn_mode_dest.bgcolor = "#94a3b8"
      map_status_lbl.value = "حالت انتخاب مبدأ فعال است."
      refresh_map_tile()

    def set_mode_dest(e):
      nonlocal map_mode_select
      map_mode_select = "dest"
      btn_mode_dest.bgcolor = "#0284c7"
      btn_mode_orig.bgcolor = "#94a3b8"
      map_status_lbl.value = "حالت انتخاب مقصد فعال است."
      refresh_map_tile()

    btn_mode_orig.on_click = set_mode_orig
    btn_mode_dest.on_click = set_mode_dest

    # اطلاعات بار و ۱۰ نوع بسته‌بندی دقیقاً مشابه ثانیه ۰:۴۸ ویدیو
    dd_cargo = ft.Dropdown(
        label="کالا",
        value=drv["cargo"],
        expand=True,
        text_size=12,
        options=[
            ft.dropdown.Option(c["name"], c["name"])
            for c in engine.data["cargo_bank"]
        ],
    )
    dd_pack = ft.Dropdown(
        label="نوع بسته‌بندی",
        value=drv["pack"],
        expand=True,
        text_size=12,
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
                "شاخه",
                "سایر",
            ]
        ],
    )
    tf_weight = ft.TextField(
        label="وزن", value=drv["weight"], width=85, text_size=12
    )
    tf_count = ft.TextField(
        label="تعداد", value=drv.get("count", "1"), width=85, text_size=12
    )
    tf_val = ft.TextField(
        label="ارزش", value=drv.get("value", "25000000"), expand=True, text_size=12
    )
    tf_fare = ft.TextField(
        label="کرایه", value=drv["fare"], expand=True, text_size=12
    )
    tf_post_fare = ft.TextField(
        label="کرایه پس‌کرایه",
        value=drv.get("post_fare", drv["fare"]),
        expand=True,
        text_size=12,
    )

    def save_user_edits(e):
      drv["login_nid"] = tf_login_nid.value.strip()
      drv["password"] = tf_pass.value.strip()
      drv["national_id"] = tf_nid.value.strip()
      try:
        drv["group"] = int(tf_group.value.strip() or 1)
      except ValueError:
        drv["group"] = 1
      drv["active"] = dd_status.value == "فعال"
      drv["referrer"] = tf_ref.value.strip()
      drv["mobile"] = tf_mob.value.strip()
      drv["plate_left"] = tf_pl_left.value.strip()
      drv["plate_letter"] = tf_pl_let.value.strip()
      drv["plate_mid"] = tf_pl_mid.value.strip()
      drv["plate_iran"] = tf_pl_ir.value.strip()
      drv["sender_first"] = tf_s_first.value.strip()
      drv["sender_last"] = tf_s_last.value.strip()
      drv["name"] = f"{drv['sender_first']} {drv['sender_last']}".strip()
      drv["receiver_first"] = tf_r_first.value.strip()
      drv["receiver_last"] = tf_r_last.value.strip()
      drv["receiver_mobile"] = tf_r_mob.value.strip()
      drv["origin_addr"] = tf_o_addr.value.strip()
      drv["dest_addr"] = tf_d_addr.value.strip()
      try:
        drv["origin_lat"] = float(tf_o_lat.value)
        drv["origin_lon"] = float(tf_o_lon.value)
        drv["dest_lat"] = float(tf_d_lat.value)
        drv["dest_lon"] = float(tf_d_lon.value)
      except ValueError:
        pass
      drv["origin_city"] = tf_o_city.value.strip()
      drv["origin_neighborhood"] = tf_o_nb.value.strip()
      drv["dest_city"] = tf_d_city.value.strip()
      drv["dest_neighborhood"] = tf_d_nb.value.strip()
      drv["origin_name"] = drv["origin_neighborhood"]
      drv["dest_name"] = drv["dest_neighborhood"]
      drv["map_layer"] = selected_layer
      drv["cargo"] = dd_cargo.value
      drv["pack"] = dd_pack.value
      drv["weight"] = tf_weight.value.strip()
      drv["count"] = tf_count.value.strip()
      drv["value"] = tf_val.value.strip()
      drv["fare"] = tf_fare.value.strip()
      drv["post_fare"] = tf_post_fare.value.strip()

      engine.save_data()
      dlg_edit.open = False
      render_active_view()
      show_toast("کاربر ویرایش شد.")

    dlg_edit = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text("ویرایش کاربر", size=16, weight="bold", color="#0f172a"),
                ft.IconButton(
                    icon=ft.icons.CLOSE,
                    on_click=lambda e: setattr(dlg_edit, "open", False)
                    or page.update(),
                ),
            ],
        ),
        content=ft.Container(
            width=400,
            height=520,
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                spacing=8,
                controls=[
                    ft.ExpansionTile(
                        title=ft.Text(
                            "مشخصات کاربر",
                            size=13,
                            weight="bold",
                            color="#0369a1",
                        ),
                        initially_expanded=True,
                        controls=[
                            ft.Container(
                                padding=8,
                                content=ft.Column(
                                    spacing=8,
                                    controls=[
                                        ft.Row([tf_login_nid, tf_pass, tf_nid]),
                                        ft.Row([tf_group, dd_status, tf_ref]),
                                        ft.Row([tf_mob]),
                                    ],
                                ),
                            )
                        ],
                    ),
                    ft.ExpansionTile(
                        title=ft.Text(
                            "پلاک", size=13, weight="bold", color="#0369a1"
                        ),
                        initially_expanded=True,
                        controls=[
                            ft.Container(
                                padding=8,
                                content=ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=8,
                                    controls=[
                                        build_iran_plate(
                                            drv["plate_left"],
                                            drv["plate_letter"],
                                            drv["plate_mid"],
                                            drv["plate_iran"],
                                            size_mode="large",
                                        ),
                                        ft.Row([
                                            tf_pl_ir,
                                            tf_pl_mid,
                                            tf_pl_let,
                                            tf_pl_left,
                                        ]),
                                    ],
                                ),
                            )
                        ],
                    ),
                    ft.ExpansionTile(
                        title=ft.Text(
                            "فرستنده و گیرنده",
                            size=13,
                            weight="bold",
                            color="#0369a1",
                        ),
                        controls=[
                            ft.Container(
                                padding=8,
                                content=ft.Column(
                                    spacing=8,
                                    controls=[
                                        ft.Row([tf_s_first, tf_s_last]),
                                        ft.Row([tf_r_first, tf_r_last]),
                                        ft.Row([tf_r_mob]),
                                    ],
                                ),
                            )
                        ],
                    ),
                    ft.ExpansionTile(
                        title=ft.Text(
                            "آدرس و مختصات (نقشه زنده)",
                            size=13,
                            weight="bold",
                            color="#0369a1",
                        ),
                        initially_expanded=True,
                        controls=[
                            ft.Container(
                                padding=8,
                                content=ft.Column(
                                    spacing=8,
                                    controls=[
                                        ft.Row(
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                            controls=[
                                                layer_badge,
                                                ft.Container(
                                                    expand=True,
                                                    content=map_status_lbl,
                                                ),
                                            ],
                                        ),
                                        dd_map_layer,
                                        ft.Row([
                                            tf_search_place,
                                            ft.ElevatedButton(
                                                "جستجو",
                                                bgcolor="#0284c7",
                                                color="white",
                                                height=38,
                                                on_click=do_search_map,
                                            ),
                                        ]),
                                        ft.Row(
                                            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                                            controls=[
                                                btn_mode_orig,
                                                btn_mode_dest,
                                            ],
                                        ),
                                        # کادر نقشه زنده واقعی + کنترلر پیمایش و زوم
                                        ft.Stack(
                                            controls=[
                                                live_map_img,
                                                ft.Container(
                                                    top=8,
                                                    left=8,
                                                    content=dist_chip,
                                                ),
                                                ft.Container(
                                                    top=75,
                                                    left=165,
                                                    content=ft.Icon(
                                                        ft.icons.LOCATION_ON,
                                                        color="#e11d48",
                                                        size=34,
                                                    ),
                                                ),
                                                ft.Container(
                                                    bottom=8,
                                                    right=8,
                                                    bgcolor="#ffffffcc",
                                                    border_radius=8,
                                                    padding=4,
                                                    content=ft.Row(
                                                        spacing=2,
                                                        controls=[
                                                            ft.IconButton(
                                                                icon=ft.icons.ARROW_UPWARD,
                                                                icon_size=16,
                                                                tooltip="حرکت به شمال",
                                                                on_click=lambda e: shift_coordinates(
                                                                    0.003, 0
                                                                ),
                                                            ),
                                                            ft.IconButton(
                                                                icon=ft.icons.ARROW_DOWNWARD,
                                                                icon_size=16,
                                                                tooltip="حرکت به جنوب",
                                                                on_click=lambda e: shift_coordinates(
                                                                    -0.003, 0
                                                                ),
                                                            ),
                                                            ft.IconButton(
                                                                icon=ft.icons.ARROW_FORWARD,
                                                                icon_size=16,
                                                                tooltip="حرکت به شرق",
                                                                on_click=lambda e: shift_coordinates(
                                                                    0, 0.003
                                                                ),
                                                            ),
                                                            ft.IconButton(
                                                                icon=ft.icons.ARROW_BACK,
                                                                icon_size=16,
                                                                tooltip="حرکت به غرب",
                                                                on_click=lambda e: shift_coordinates(
                                                                    0, -0.003
                                                                ),
                                                            ),
                                                        ],
                                                    ),
                                                ),
                                            ]
                                        ),
                                        tf_o_addr,
                                        tf_d_addr,
                                        ft.Row([tf_o_lat, tf_o_lon]),
                                        ft.Row([tf_d_lat, tf_d_lon]),
                                        ft.Row([tf_o_city, tf_o_nb]),
                                        ft.Row([tf_d_city, tf_d_nb]),
                                    ],
                                ),
                            )
                        ],
                    ),
                    ft.ExpansionTile(
                        title=ft.Text(
                            "اطلاعات بار",
                            size=13,
                            weight="bold",
                            color="#0369a1",
                        ),
                        initially_expanded=True,
                        controls=[
                            ft.Container(
                                padding=8,
                                content=ft.Column(
                                    spacing=8,
                                    controls=[
                                        ft.Row([dd_cargo, tf_weight, dd_pack]),
                                        ft.Row([tf_count, tf_val, tf_fare]),
                                        ft.Row([tf_post_fare]),
                                    ],
                                ),
                            )
                        ],
                    ),
                ],
            ),
        ),
        actions=[
            ft.ElevatedButton(
                "ذخیره تغییرات",
                bgcolor="#0284c7",
                color="white",
                on_click=save_user_edits,
            ),
            ft.OutlinedButton(
                "انصراف",
                on_click=lambda e: setattr(dlg_edit, "open", False)
                or page.update(),
            ),
        ],
    )
    page.dialog = dlg_edit
    dlg_edit.open = True
    page.update()

  # =========================================================================
  # ۳. دیالوگ‌های افزودن کاربر (استعلام زنده از سامانه) و جابجایی گروه
  # =========================================================================
  def open_add_user_live_dialog(e):
    tf_nid = ft.TextField(
        label="کد ملی راننده (۱۰ رقمی)",
        hint_text="مثال: 3440188885",
        text_size=13,
    )
    tf_pass = ft.TextField(
        label="رمز عبور سامانه utcms.ir",
        value="Aa13611361##",
        text_size=13,
    )
    dd_grp = ft.Dropdown(
        label="انتخاب گروه",
        value="1",
        options=[
            ft.dropdown.Option("1", "گروه ۱"),
            ft.dropdown.Option("2", "گروه ۲"),
        ],
    )
    status_txt = ft.Text(
        "با وارد کردن کد ملی و رمز، پلاک و نام راننده مستقیماً از سامانه باربرگ استعلام می‌شود.",
        size=11,
        color="#64748b",
    )

    def do_add(e):
      if len(tf_nid.value.strip()) < 8:
        status_txt.value = "لطفاً کد ملی معتبر وارد کنید!"
        status_txt.color = "#dc2626"
        page.update()
        return
      status_txt.value = "در حال اتصال به barname.utcms.ir و واکشی ناوگان..."
      status_txt.color = "#0284c7"
      page.update()
      ok, res = engine.fetch_driver_by_nid_live(
          tf_nid.value.strip(), tf_pass.value.strip(), int(dd_grp.value)
      )
      if ok:
        dlg.open = False
        render_active_view()
        show_toast(
            f"راننده «{res['name']}» با پلاک از سامانه دریافت و اضافه شد.",
            "#10b981",
        )
      else:
        status_txt.value = res
        status_txt.color = "#dc2626"
        page.update()

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(
            "افزودن کاربر (اتصال به سامانه باربرگ)", size=15, weight="bold"
        ),
        content=ft.Container(
            width=360,
            content=ft.Column(
                tight=True,
                spacing=10,
                controls=[tf_nid, tf_pass, dd_grp, status_txt],
            ),
        ),
        actions=[
            ft.ElevatedButton(
                "استعلام و افزودن",
                bgcolor="#0284c7",
                color="white",
                on_click=do_add,
            ),
            ft.OutlinedButton(
                "انصراف",
                on_click=lambda e: setattr(dlg, "open", False) or page.update(),
            ),
        ],
    )
    page.dialog = dlg
    dlg.open = True
    page.update()

  def open_bulk_add_dialog(e):
    tf_bulk = ft.TextField(
        label="ورود گروهی (هر خط: کدملی,رمزعبور)",
        multiline=True,
        min_lines=4,
        max_lines=6,
        hint_text="3440188885,Aa13611361##\n3430043425,Aa13611361##",
        text_size=12,
    )
    dd_g = ft.Dropdown(
        label="گروه مقصد",
        value="1",
        options=[
            ft.dropdown.Option("1", "گروه ۱"),
            ft.dropdown.Option("2", "گروه ۲"),
        ],
    )

    def do_bulk(e):
      lines = [
          ln.strip()
          for ln in (tf_bulk.value or "").splitlines()
          if ln.strip()
      ]
      added = 0
      for ln in lines:
        parts = ln.replace(" ", "").split(",")
        nid = parts[0]
        pw = parts[1] if len(parts) > 1 else "Aa13611361##"
        ok, _ = engine.fetch_driver_by_nid_live(nid, pw, int(dd_g.value))
        if ok:
          added += 1
      dlg.open = False
      render_active_view()
      show_toast(f"{added} کاربر به صورت گروهی استعلام و اضافه شدند.", "#10b981")

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("افزودن گروهی کاربران", size=15, weight="bold"),
        content=ft.Container(
            width=360,
            content=ft.Column(tight=True, spacing=10, controls=[tf_bulk, dd_g]),
        ),
        actions=[
            ft.ElevatedButton(
                "ثبت گروهی",
                bgcolor="#0284c7",
                color="white",
                on_click=do_bulk,
            ),
            ft.OutlinedButton(
                "انصراف",
                on_click=lambda e: setattr(dlg, "open", False) or page.update(),
            ),
        ],
    )
    page.dialog = dlg
    dlg.open = True
    page.update()

  def open_move_group_dialog(e):
    """دیالوگ جابجایی گروه دقیقاً مشابه دقیقه ۰۲:۵۱ ویدیو"""
    dd_src = ft.Dropdown(
        label="گروه مبدأ",
        value="1",
        options=[
            ft.dropdown.Option("1", "گروه ۱"),
            ft.dropdown.Option("2", "گروه ۲"),
        ],
    )
    tf_dst = ft.TextField(
        label="شماره گروه مقصد", value="2", keyboard_type=ft.KeyboardType.NUMBER
    )
    checks_col = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO, height=180)
    selected_map = {}

    def populate_drivers_for_src():
      checks_col.controls.clear()
      selected_map.clear()
      src_g = int(dd_src.value or 1)
      for d in engine.data["drivers"]:
        if d["group"] == src_g:
          cb = ft.Checkbox(
              label=f"{d['name']} – {d['national_id']}", value=True
          )
          selected_map[d["id"]] = cb
          checks_col.controls.append(cb)
      page.update()

    dd_src.on_change = lambda e: populate_drivers_for_src()
    populate_drivers_for_src()

    def do_transfer(e):
      try:
        target_g = int(tf_dst.value.strip() or 2)
      except ValueError:
        target_g = 2
      moved = 0
      for d in engine.data["drivers"]:
        if d["id"] in selected_map and selected_map[d["id"]].value:
          d["group"] = target_g
          moved += 1
      engine.save_data()
      dlg.open = False
      render_active_view()
      show_toast(f"{moved} راننده به گروه {target_g} منتقل شدند.", "#0284c7")

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("جابجایی گروه", size=16, weight="bold"),
        content=ft.Container(
            width=360,
            content=ft.Column(
                tight=True,
                spacing=10,
                controls=[
                    dd_src,
                    tf_dst,
                    ft.Text(
                        "رانندگان (تیک بزنید):",
                        size=12,
                        color="#64748b",
                        weight="bold",
                    ),
                    checks_col,
                ],
            ),
        ),
        actions=[
            ft.ElevatedButton(
                "انتقال انتخاب‌شده‌ها",
                bgcolor="#0284c7",
                color="white",
                on_click=do_transfer,
            ),
            ft.OutlinedButton(
                "انصراف",
                on_click=lambda e: setattr(dlg, "open", False) or page.update(),
            ),
        ],
    )
    page.dialog = dlg
    dlg.open = True
    page.update()

  # =========================================================================
  # ۴. ساخت تب «کاربران» (ساختار جدولی فشرده دقیقاً مطابق ثانیه ۰:۱۱ ویدیو)
  # =========================================================================
  def build_users_tab():
    total_cnt = len(engine.data["drivers"])
    limit_cnt = current_user.get("limit", 50)
    rem_cnt = max(0, limit_cnt - total_cnt)

    rows_list = ft.Column(spacing=6)

    # سرستون جدول: ردیف | راننده | پلاک | گروه | عملیات
    table_header = ft.Container(
        bgcolor="#e0f2fe",
        padding=ft.padding.symmetric(horizontal=8, vertical=8),
        border_radius=8,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(
                    "ردیف",
                    size=11,
                    weight="bold",
                    color="#0f172a",
                    width=28,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "راننده",
                    size=11,
                    weight="bold",
                    color="#0f172a",
                    width=88,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "پلاک",
                    size=11,
                    weight="bold",
                    color="#0f172a",
                    width=130,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "گروه",
                    size=11,
                    weight="bold",
                    color="#0f172a",
                    width=28,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "عملیات",
                    size=11,
                    weight="bold",
                    color="#0f172a",
                    width=62,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
        ),
    )
    rows_list.controls.append(table_header)

    for idx, drv in enumerate(engine.data["drivers"], start=1):
      if (
          user_group_filter != "all"
          and str(drv["group"]) != user_group_filter
      ):
        continue
      if user_search_q:
        sq = user_search_q.strip()
        p_full = f"{drv['plate_left']}{drv['plate_mid']}{drv['plate_iran']}"
        if (
            sq not in drv["name"]
            and sq not in drv["national_id"]
            and sq not in p_full
        ):
          continue

      is_on = drv["active"]

      def toggle_drv(e, d=drv):
        d["active"] = not d["active"]
        engine.save_data()
        render_active_view()

      def delete_drv(e, d=drv):
        engine.data["drivers"].remove(d)
        engine.save_data()
        render_active_view()
        show_toast(f"کاربر {d['name']} حذف شد.", "#dc2626")

      # دکمه کپسولی سبز ON / قرمز OFF دقیقاً مشابه ویدیو
      pill_switch = ft.Container(
          width=56,
          height=24,
          bgcolor="#16a34a" if is_on else "#dc2626",
          border_radius=12,
          padding=ft.padding.symmetric(horizontal=4),
          on_click=toggle_drv,
          content=ft.Row(
              alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
              controls=[
                  ft.Text(
                      "ON" if is_on else "OFF",
                      color="white",
                      size=9,
                      weight="bold",
                  ),
                  ft.Container(
                      width=16,
                      height=16,
                      bgcolor="white",
                      border_radius=8,
                  ),
              ],
          ),
      )

      row_card = ft.Container(
          bgcolor="white" if is_on else "#fff1f2",
          padding=ft.padding.symmetric(horizontal=6, vertical=8),
          border_radius=10,
          border=ft.border.all(1, "#e2e8f0" if is_on else "#fecdd3"),
          content=ft.Row(
              alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
              vertical_alignment=ft.CrossAxisAlignment.CENTER,
              controls=[
                  # ۱. ردیف
                  ft.Container(
                      width=26,
                      height=26,
                      bgcolor="#f1f5f9",
                      border_radius=8,
                      alignment=ft.alignment.center,
                      content=ft.Text(
                          str(idx), size=11, weight="bold", color="#334155"
                      ),
                  ),
                  # ۲. نام راننده و کدملی در دو خط компакт
                  ft.Container(
                      width=90,
                      content=ft.Column(
                          spacing=1,
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                          controls=[
                              ft.Text(
                                  drv["name"],
                                  size=11,
                                  weight="bold",
                                  color="#0f172a",
                                  text_align=ft.TextAlign.CENTER,
                                  max_lines=1,
                                  overflow=ft.TextOverflow.ELLIPSIS,
                              ),
                              ft.Text(
                                  drv["national_id"],
                                  size=9,
                                  color="#64748b",
                                  text_align=ft.TextAlign.CENTER,
                              ),
                          ],
                      ),
                  ),
                  # ۳. پلاک استاندارد مینی
                  build_iran_plate(
                      drv["plate_left"],
                      drv["plate_letter"],
                      drv["plate_mid"],
                      drv["plate_iran"],
                      size_mode="mini",
                  ),
                  # ۴. شماره گروه
                  ft.Container(
                      width=26,
                      height=26,
                      bgcolor="#f1f5f9",
                      border_radius=8,
                      alignment=ft.alignment.center,
                      content=ft.Text(
                          str(drv["group"]),
                          size=11,
                          weight="bold",
                          color="#0f172a",
                      ),
                  ),
                  # ۵. ستون عملیات (ON/OFF، ویرایش، حذف)
                  ft.Column(
                      spacing=3,
                      horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                      controls=[
                          pill_switch,
                          ft.Container(
                              width=56,
                              height=22,
                              bgcolor="#0284c7",
                              border_radius=6,
                              alignment=ft.alignment.center,
                              on_click=lambda e, d=drv: open_user_edit_dialog(
                                  d
                              ),
                              content=ft.Text(
                                  "ویرایش",
                                  color="white",
                                  size=9,
                                  weight="bold",
                              ),
                          ),
                          ft.Container(
                              width=56,
                              height=22,
                              bgcolor="#fff1f2",
                              border=ft.border.all(1, "#fda4af"),
                              border_radius=6,
                              alignment=ft.alignment.center,
                              on_click=delete_drv,
                              content=ft.Text(
                                  "حذف",
                                  color="#be123c",
                                  size=9,
                                  weight="bold",
                              ),
                          ),
                      ],
                  ),
              ],
          ),
      )
      rows_list.controls.append(row_card)

    def on_search_in(e):
      nonlocal user_search_q
      user_search_q = e.control.value
      render_active_view()

    def on_grp_in(e):
      nonlocal user_group_filter
      user_group_filter = e.control.value
      render_active_view()

    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=8,
        controls=[
            ft.Container(
                bgcolor="white",
                padding=12,
                border_radius=14,
                border=ft.border.all(1, "#e2e8f0"),
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.Text(
                            "مدیریت کاربران",
                            size=17,
                            weight="bold",
                            color="#0f172a",
                        ),
                        ft.Text(
                            "افزودن دستی، افزودن کاربر، افزودن گروهی، ویرایش، حذف و جابجایی گروه",
                            size=10,
                            color="#64748b",
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.OutlinedButton(
                                    "افزودن دستی",
                                    height=36,
                                    expand=True,
                                    on_click=lambda e: open_user_edit_dialog(
                                        engine.data["drivers"][0]
                                    ),
                                ),
                                ft.ElevatedButton(
                                    "افزودن کاربر",
                                    bgcolor="#0284c7",
                                    color="white",
                                    height=36,
                                    expand=True,
                                    on_click=open_add_user_live_dialog,
                                ),
                                ft.OutlinedButton(
                                    "افزودن گروهی",
                                    height=36,
                                    expand=True,
                                    on_click=open_bulk_add_dialog,
                                ),
                            ],
                        ),
                        ft.Text(
                            f"نمایش: {total_cnt} از {total_cnt} | سقف: {limit_cnt} | باقی‌مانده: {rem_cnt}",
                            size=11,
                            weight="bold",
                            color="#334155",
                        ),
                        ft.OutlinedButton(
                            "جابجایی گروه",
                            width=400,
                            height=36,
                            on_click=open_move_group_dialog,
                        ),
                        ft.Row(
                            controls=[
                                ft.Dropdown(
                                    value=user_group_filter,
                                    width=120,
                                    height=42,
                                    text_size=11,
                                    options=[
                                        ft.dropdown.Option("all", "همه گروه‌ها"),
                                        ft.dropdown.Option("1", "گروه ۱"),
                                        ft.dropdown.Option("2", "گروه ۲"),
                                    ],
                                    on_change=on_grp_in,
                                ),
                                ft.TextField(
                                    hint_text="جستجوی نام، کد ملی یا پلاک ...",
                                    value=user_search_q,
                                    height=42,
                                    text_size=11,
                                    expand=True,
                                    on_change=on_search_in,
                                ),
                            ]
                        ),
                    ],
                ),
            ),
            rows_list,
        ],
    )

  # =========================================================================
  # ۵. تب «باربرگ» (گروه ۱ و ۲ + تنظیمات ۵ تبی + پاپ‌آپ هر پلاک - دقیقه ۰۱:۳۷ تا ۰۲:۱۴)
  # =========================================================================
  def open_group_settings_dialog(grp_id):
    """دیالوگ تنظیمات گروه با ۵ تب (زمان‌بندی و دور، تنظیمات کاربر، زمان‌بندی روزانه، شروع هوشمند، شروع ۲)"""
    g_cfg = engine.data["group_settings"].get(
        str(grp_id), engine.data["group_settings"]["1"]
    )
    active_sub = "timing"
    sub_holder = ft.Container(height=330)

    tf_rounds = ft.TextField(
        label="تعداد دور", value=g_cfg["rounds"], text_size=13
    )
    tf_interval = ft.TextField(
        label="فاصله هر باربرگ (دقیقه)", value=g_cfg["interval"], text_size=13
    )
    tf_rtime = ft.TextField(
        label="زمان دور (دقیقه)", value=g_cfg["round_time"], text_size=13
    )
    chk_limit5 = ft.Checkbox(
        label="تعداد لاگین مجاز در هر ده دقیقه (جلوگیری از بن محدودیت ورود)",
        value=g_cfg["max_login_5min"],
    )

    chk_auto_daily = ft.Checkbox(
        label="استارت/استپ خودکار در ساعات مشخص روز",
        value=g_cfg["auto_start"],
    )
    chk_otp_stop = ft.Checkbox(
        label="استپ OTP (در صورت فعال بودن، با دریافت OTP ربات متوقف می‌شود)",
        value=g_cfg["otp_stop"],
    )
    dd_sort = ft.Dropdown(
        label="مرتب‌سازی پلاک‌ها",
        value=g_cfg["sort_mode"],
        options=[
            ft.dropdown.Option("خودکار (پیش‌فرض)", "خودکار (پیش‌فرض)"),
            ft.dropdown.Option("بر اساس حروف الفبا", "بر اساس حروف الفبا"),
            ft.dropdown.Option("بر اساس تناژ", "بر اساس تناژ"),
        ],
    )

    user_sub_mode = "trip"  # trip | issue | platform

    def render_sub():
      if active_sub == "timing":
        sub_holder.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
            controls=[
                tf_rounds,
                tf_interval,
                tf_rtime,
                chk_limit5,
                ft.Text(
                    "هر کاربر در هر ده دقیقه حداکثر همین تعداد لاگین می‌زند؛ بیشتر از آن با آزاد شدن نوبت صبر می‌کند (هم سرور اصلی هم سرور موبایل).",
                    size=10,
                    color="#dc2626",
                ),
            ],
        )
      elif active_sub == "users":
        drv_items = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO, height=230)
        for idx, d in enumerate(
            [x for x in engine.data["drivers"] if str(x["group"]) == str(grp_id)],
            start=1,
        ):
          if user_sub_mode == "trip":
            cb = ft.Checkbox(
                label=f"{idx}. {d['name']} ({d['national_id']})",
                value=d.get("trip_enabled", True),
                on_change=lambda e, item=d: setattr(
                    item, "__setitem__", ("trip_enabled", e.control.value)
                ),
            )
            drv_items.controls.append(cb)
          elif user_sub_mode == "issue":
            cb = ft.Checkbox(
                label=f"{idx}. {d['name']} ({d['national_id']})",
                value=d.get("issue_enabled", True),
            )
            drv_items.controls.append(cb)
          else:
            row_plat = ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(f"{idx}. {d['name']}", size=11, weight="bold"),
                    ft.Dropdown(
                        value=d.get("platform", "گوشی"),
                        width=95,
                        height=35,
                        text_size=11,
                        options=[
                            ft.dropdown.Option("گوشی", "گوشی"),
                            ft.dropdown.Option("وب", "وب"),
                        ],
                    ),
                    ft.Dropdown(
                        value=d.get("otp_mode", "بدون کد"),
                        width=105,
                        height=35,
                        text_size=11,
                        options=[
                            ft.dropdown.Option("بدون کد", "بدون کد"),
                            ft.dropdown.Option("کدی", "کدی"),
