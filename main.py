import time
import traceback
import flet as ft

try:
  from engine import BarbargEngine
except Exception:
  BarbargEngine = None
  ENGINE_ERR = traceback.format_exc()


def build_iran_plate(left_2, letter, mid_3, iran_code, compact=False):
  """ساخت ویجت گرافیکی پلاک خودرو دقیقاً مشابه پلاک واقعی ایران در اسکرین‌شات‌ها"""
  h = 44 if compact else 54
  num_size = 17 if compact else 22
  return ft.Container(
      height=h,
      width=235 if compact else 290,
      bgcolor="white",
      border=ft.border.all(2, "#0f172a"),
      border_radius=8,
      clip_behavior=ft.ClipBehavior.HARD_EDGE,
      content=ft.Row(
          spacing=0,
          controls=[
              # کادر سمت راست: ایران ۸۴
              ft.Container(
                  width=48 if compact else 58,
                  height=h,
                  bgcolor="white",
                  border=ft.border.only(left=ft.BorderSide(1.5, "#0f172a")),
                  alignment=ft.alignment.center,
                  content=ft.Column(
                      spacing=0,
                      alignment=ft.MainAxisAlignment.CENTER,
                      horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                      controls=[
                          ft.Text(
                              "ایران",
                              size=9 if compact else 11,
                              weight="bold",
                              color="#0f172a",
                          ),
                          ft.Text(
                              str(iran_code),
                              size=14 if compact else 18,
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
                              size=num_size,
                              weight="bold",
                              color="#0f172a",
                          ),
                          ft.Text(
                              str(letter),
                              size=num_size,
                              weight="bold",
                              color="#b91c1c",
                          ),
                          ft.Text(
                              str(left_2),
                              size=num_size,
                              weight="bold",
                              color="#0f172a",
                          ),
                      ],
                  ),
              ),
              # نوار آبی سمت چپ پرچم ایران (I.R. IRAN)
              ft.Container(
                  width=30 if compact else 36,
                  height=h,
                  bgcolor="#0369a1",
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
                              size=6 if compact else 7,
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
  page.title = "پنل تجاری بارگو بندر (BarGo VIP)"
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
  selected_group_filter = "all"
  search_query = ""

  # نوار اعلان وضعیت سرور موبایل و اعتبار اشتراک پنل
  server_banner_text = ft.Text(
      "⚡ حالت فعال: سرور موبایل + درگاه barname.utcms.ir (سوییچ هوشمند بدون قطعی)",
      color="#9a3412",
      size=12,
      weight="bold",
  )

  quota_counter_text = ft.Text("", size=12, weight="bold", color="#334155")

  def update_quota_text():
    total = len(engine.data["drivers"])
    limit = engine.data["license"]["plan_limit"]
    rem = max(0, limit - total)
    days = engine.data["license"]["days_left"]
    quota_counter_text.value = (
        f"پلاک‌های فعال: {total} از {limit} | ظرفیت باقی‌مانده: {rem} | اعتبار پنل:"
        f" {days} روز"
    )

  update_quota_text()

  # بخش لاگ عملیات اتوماسیون
  log_list = ft.Column(spacing=5, scroll=ft.ScrollMode.AUTO, height=130)

  def add_log(msg, color="#0f172a"):
    t_str = time.strftime("%H:%M:%S")
    log_list.controls.insert(
        0, ft.Text(f"[{t_str}] {msg}", size=11, color=color, weight="bold")
    )
    page.update()

  # لیست کارت‌های رانندگان
  drivers_column = ft.Column(spacing=10)

  # پنجره دیالوگ ویرایش کامل کاربر + اطلاعات بار + نقشه زنده مبدا و مقصد
  def open_edit_dialog(driver):
    tf_nid = ft.TextField(
        label="کد ملی راننده / ورود",
        value=driver["national_id"],
        text_size=13,
        expand=True,
    )
    tf_pass = ft.TextField(
        label="رمز عبور سامانه",
        value=driver["password"],
        text_size=13,
        expand=True,
    )
    tf_name = ft.TextField(
        label="نام و نام خانوادگی راننده (فرستنده)",
        value=driver["name"],
        text_size=13,
        expand=True,
    )
    tf_mobile = ft.TextField(
        label="موبایل فرستنده",
        value=driver["mobile"],
        text_size=13,
        expand=True,
    )
    dd_group = ft.Dropdown(
        label="گروه",
        value=str(driver["group"]),
        width=110,
        options=[
            ft.dropdown.Option("1", "گروه ۱"),
            ft.dropdown.Option("2", "گروه ۲"),
            ft.dropdown.Option("3", "گروه ۳"),
        ],
    )
    tf_tonnage = ft.TextField(
        label="تناژ مجاز",
        value=str(driver.get("tonnage", 6)),
        width=100,
        text_size=13,
    )

    # فیلدهای پلاک
    tf_p_left = ft.TextField(
        label="دو رقم چپ", value=driver["plate_left"], width=75
    )
    tf_p_letter = ft.TextField(
        label="حرف", value=driver["plate_letter"], width=60
    )
    tf_p_mid = ft.TextField(
        label="سه رقم", value=driver["plate_mid"], width=85
    )
    tf_p_iran = ft.TextField(
        label="ایران", value=driver["plate_iran"], width=70
    )

    # فیلدهای اطلاعات بار
    dd_cargo = ft.Dropdown(
        label="کالا",
        value=driver["cargo"],
        expand=True,
        options=[
            ft.dropdown.Option(c["name"], c["name"])
            for c in engine.cargo_catalog
        ],
    )
    dd_pack = ft.Dropdown(
        label="نوع بسته‌بندی",
        value=driver["pack"],
        expand=True,
        options=[
            ft.dropdown.Option(p, p)
            for p in ["گونی", "کیسه", "فله", "پالت", "کارتن", "جعبه", "بسته"]
        ],
    )
    tf_weight = ft.TextField(
        label="وزن (تن)", value=driver["weight"], width=90
    )
    tf_count = ft.TextField(
        label="تعداد", value=driver["count"], width=90
    )
    tf_value = ft.TextField(
        label="ارزش بار (ریال)", value=driver["value"], expand=True
    )
    tf_fare = ft.TextField(
        label="کرایه / پس‌کرایه (ریال)", value=driver["fare"], expand=True
    )

    receiver_preview = ft.Text(
        f"گیرنده تصادفی بعدی: {engine.generate_random_receiver()}",
        size=12,
        color="#0284c7",
        weight="bold",
    )

    def randomize_cargo_clicked(e):
      try:
        ton = int(tf_tonnage.value or 6)
      except ValueError:
        ton = 6
      smart = engine.generate_smart_cargo(ton)
      dd_cargo.value = smart["cargo"]
      dd_pack.value = smart["pack"]
      tf_weight.value = smart["weight"]
      tf_count.value = smart["count"]
      tf_value.value = smart["value"]
      tf_fare.value = smart["fare"]
      receiver_preview.value = f"گیرنده تصادفی انتخاب‌شده: {smart['receiver']}"
      page.update()

    # بخش نقشه و مختصات مبدا و مقصد
    tf_orig_name = ft.TextField(
        label="نام مبدا", value=driver["origin_name"], expand=True
    )
    tf_dest_name = ft.TextField(
        label="نام مقصد", value=driver["dest_name"], expand=True
    )
    dist_badge = ft.Text(
        f"مسافت محاسبه‌شده روی نقشه: {driver['distance_km']} km",
        size=13,
        weight="bold",
        color="white",
    )

    # نقاط پیش‌فرض هرمزگان برای جابجایی سریع روی نقشه
    preset_locations = {
        "بندر لنگه": (26.5579, 54.8807),
        "بندر کنگ": (26.5946, 54.9463),
        "باورد": (26.6950, 54.8350),
        "بندرعباس": (27.1832, 56.2666),
        "ایسین": (27.3100, 56.2800),
        "گزیر": (26.7120, 54.8910),
        "چارک": (26.7300, 54.2700),
        "خمیر": (26.9520, 55.5850),
    }

    def update_map_route(e):
      o_coords = preset_locations.get(
          tf_orig_name.value, (driver["origin_lat"], driver["origin_lon"])
      )
      d_coords = preset_locations.get(
          tf_dest_name.value, (driver["dest_lat"], driver["dest_lon"])
      )
      driver["origin_lat"], driver["origin_lon"] = o_coords
      driver["dest_lat"], driver["dest_lon"] = d_coords
      km = engine.calculate_distance(
          o_coords[0], o_coords[1], d_coords[0], d_coords[1]
      )
      driver["distance_km"] = km
      dist_badge.value = (
          f"مسافت مسیر ({tf_orig_name.value} ⬅ {tf_dest_name.value}): {km} km"
      )
      page.update()

    dd_quick_orig = ft.Dropdown(
        label="انتخاب سریع مبدا روی نقشه",
        value=driver["origin_name"]
        if driver["origin_name"] in preset_locations
        else "بندر لنگه",
        expand=True,
        options=[
            ft.dropdown.Option(k, k) for k in preset_locations.keys()
        ],
    )
    dd_quick_dest = ft.Dropdown(
        label="انتخاب سریع مقصد روی نقشه",
        value=driver["dest_name"]
        if driver["dest_name"] in preset_locations
        else "بندر کنگ",
        expand=True,
        options=[
            ft.dropdown.Option(k, k) for k in preset_locations.keys()
        ],
    )

    def on_preset_change(e):
      tf_orig_name.value = dd_quick_orig.value
      tf_dest_name.value = dd_quick_dest.value
      update_map_route(None)

    dd_quick_orig.on_change = on_preset_change
    dd_quick_dest.on_change = on_preset_change

    # شبیه‌ساز بصری نقشه مسیر (مشابه اسکرین‌شات Senator OSM)
    map_visual = ft.Container(
        height=175,
        bgcolor="#e0f2fe",
        border_radius=12,
        border=ft.border.all(2, "#0284c7"),
        padding=12,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Container(
                            bgcolor="#be123c",
                            padding=ft.padding.symmetric(
                                horizontal=10, vertical=4
                            ),
                            border_radius=8,
                            content=ft.Text(
                                "📍 مبدأ ثبت‌شده",
                                color="white",
                                size=11,
                                weight="bold",
                            ),
                        ),
                        ft.Container(
                            bgcolor="#0284c7",
                            padding=ft.padding.symmetric(
                                horizontal=10, vertical=4
                            ),
                            border_radius=8,
                            content=ft.Text(
                                "BarGo OSM نقشه هوشمند",
                                color="white",
                                size=11,
                                weight="bold",
                            ),
                        ),
                    ],
                ),
                ft.Container(
                    alignment=ft.alignment.center,
                    bgcolor="#0369a1",
                    padding=ft.padding.symmetric(horizontal=14, vertical=6),
                    border_radius=20,
                    content=dist_badge,
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            "پشتیبانی از مختصات GPS شروع و پایان حمل",
                            size=11,
                            color="#0369a1",
                            weight="bold",
                        ),
                        ft.Container(
                            bgcolor="#b91c1c",
                            padding=ft.padding.symmetric(
                                horizontal=10, vertical=4
                            ),
                            border_radius=8,
                            content=ft.Text(
                                "🏁 مقصد ثبت‌شده",
                                color="white",
                                size=11,
                                weight="bold",
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )

    def save_changes(e):
      driver["national_id"] = tf_nid.value.strip()
      driver["password"] = tf_pass.value.strip()
      driver["name"] = tf_name.value.strip()
      driver["mobile"] = tf_mobile.value.strip()
      driver["group"] = int(dd_group.value or 1)
      try:
        driver["tonnage"] = int(tf_tonnage.value or 6)
      except ValueError:
        driver["tonnage"] = 6
      driver["plate_left"] = tf_p_left.value.strip()
      driver["plate_letter"] = tf_p_letter.value.strip()
      driver["plate_mid"] = tf_p_mid.value.strip()
      driver["plate_iran"] = tf_p_iran.value.strip()
      driver["cargo"] = dd_cargo.value
      driver["pack"] = dd_pack.value
      driver["weight"] = tf_weight.value.strip()
      driver["count"] = tf_count.value.strip()
      driver["value"] = tf_value.value.strip()
      driver["fare"] = tf_fare.value.strip()
      driver["origin_name"] = tf_orig_name.value.strip()
      driver["dest_name"] = tf_dest_name.value.strip()

      engine.save_data()
      dlg.open = False
      render_drivers()
      add_log(f"تغییرات کاربر «{driver['name']}» با موفقیت ذخیره شد.", "#16a34a")

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(
            f"ویرایش کاربر: {driver['name']}", size=16, weight="bold"
        ),
        content=ft.Container(
            width=420,
            height=520,
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                spacing=10,
                controls=[
                    ft.Text(
                        "۱. مشخصات کاربر و ناوگان",
                        weight="bold",
                        color="#0284c7",
                    ),
                    ft.Row([tf_name, dd_group]),
                    ft.Row([tf_nid, tf_pass]),
                    ft.Row([tf_mobile, tf_tonnage]),
                    ft.Divider(),
                    ft.Text(
                        "۲. پلاک انتظامی ناوگان",
                        weight="bold",
                        color="#0284c7",
                    ),
                    ft.Container(
                        alignment=ft.alignment.center,
                        content=build_iran_plate(
                            driver["plate_left"],
                            driver["plate_letter"],
                            driver["plate_mid"],
                            driver["plate_iran"],
                            compact=True,
                        ),
                    ),
                    ft.Row([tf_p_iran, tf_p_mid, tf_p_letter, tf_p_left]),
                    ft.Divider(),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                "۳. اطلاعات بار و گیرنده",
                                weight="bold",
                                color="#0284c7",
                            ),
                            ft.ElevatedButton(
                                "انتخاب تصادفی هوشمند (AI)",
                                icon=ft.icons.AUTO_AWESOME,
                                bgcolor="#7c3aed",
                                color="white",
                                on_click=randomize_cargo_clicked,
                            ),
                        ],
                    ),
                    receiver_preview,
                    ft.Row([dd_cargo, dd_pack]),
                    ft.Row([tf_weight, tf_count]),
                    ft.Row([tf_value, tf_fare]),
                    ft.Divider(),
                    ft.Text(
                        "۴. آدرس و مختصات روی نقشه (مبدا به مقصد)",
                        weight="bold",
                        color="#0284c7",
                    ),
                    ft.Row([dd_quick_orig, dd_quick_dest]),
                    ft.Row([tf_orig_name, tf_dest_name]),
                    map_visual,
                ],
            ),
        ),
        actions=[
            ft.ElevatedButton(
                "ذخیره تغییرات",
                bgcolor="#0284c7",
                color="white",
                on_click=save_changes,
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

  # پنجره افزودن سریع راننده جدید (تا سقف پنل)
  def open_add_driver_dialog(e):
    if len(engine.data["drivers"]) >= engine.data["license"]["plan_limit"]:
      add_log(
          "⚠️ سقف مجاز پلاک‌های پنل شما پر شده است! لطفاً پنل را ارتقا دهید.",
          "#dc2626",
      )
      return

    new_id = (
        max([d["id"] for d in engine.data["drivers"]], default=0) + 1
    )
    smart = engine.generate_smart_cargo(6)
    new_driver = {
        "id": new_id,
        "name": "راننده جدید",
        "national_id": "3440000000",
        "password": "Aa123456##",
        "mobile": "09170000000",
        "group": 1,
        "active": True,
        "plate_left": "11",
        "plate_letter": "ع",
        "plate_mid": "111",
        "plate_iran": "84",
        "tonnage": 6,
        "cargo": smart["cargo"],
        "pack": smart["pack"],
        "weight": smart["weight"],
        "count": smart["count"],
        "value": smart["value"],
        "fare": smart["fare"],
        "origin_name": "بندر لنگه",
        "dest_name": "بندر کنگ",
        "origin_lat": 26.5579,
        "origin_lon": 54.8807,
        "dest_lat": 26.5946,
        "dest_lon": 54.9463,
        "distance_km": 20.55,
        "fuel_quota": "پایش فعال (۲۰۰۰ لیتر)",
        "fleet_license": "معتبر (استعلام آنلاین)",
        "driver_license": "معتبر (هوشمند فعال)",
    }
    engine.data["drivers"].append(new_driver)
    engine.save_data()
    update_quota_text()
    render_drivers()
    open_edit_dialog(new_driver)

  # ساخت کارت هر راننده مطابق طرح گرافیکی شما
  def render_drivers():
    drivers_column.controls.clear()
    for idx, drv in enumerate(engine.data["drivers"], start=1):
      if (
          selected_group_filter != "all"
          and str(drv["group"]) != selected_group_filter
      ):
        continue
      if search_query:
        q = search_query.strip()
        full_p = f"{drv['plate_left']}{drv['plate_mid']}{drv['plate_iran']}"
        if (
            q not in drv["name"]
            and q not in drv["national_id"]
            and q not in full_p
        ):
          continue

      def make_toggle(d):
        def _toggle(e):
          d["active"] = e.control.value
          engine.save_data()
          render_drivers()

        return _toggle

      def make_delete(d):
        def _del(e):
          engine.data["drivers"].remove(d)
          engine.save_data()
          update_quota_text()
          render_drivers()
          add_log(f"کاربر {d['name']} حذف شد.", "#dc2626")

        return _del

      def make_action(d, act):
        def _act(e):
          msg = engine.execute_full_cycle(d, act)
          add_log(msg, "#15803d")

        return _act

      card = ft.Container(
          bgcolor="white",
          padding=14,
          border_radius=14,
          border=ft.border.all(
              1.5, "#cbd5e1" if drv["active"] else "#fca5a5"
          ),
          content=ft.Column(
              spacing=10,
              controls=[
                  # ردیف اول: شماره ردیف، نام راننده، کد ملی، گروه و سوییچ روشن/خاموش
                  ft.Row(
                      alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                      controls=[
                          ft.Row(
                              spacing=8,
                              controls=[
                                  ft.Container(
                                      width=32,
                                      height=32,
                                      bgcolor="#e0f2fe",
                                      border_radius=8,
                                      alignment=ft.alignment.center,
                                      content=ft.Text(
                                          str(idx),
                                          weight="bold",
                                          color="#0369a1",
                                      ),
                                  ),
                                  ft.Column(
                                      spacing=2,
                                      controls=[
                                          ft.Text(
                                              drv["name"],
                                              size=16,
                                              weight="bold",
                                              color="#0f172a",
                                          ),
                                          ft.Text(
                                              f"کد ملی: {drv['national_id']} | گروه {drv['group']} | تناژ: {drv.get('tonnage', 6)} تن",
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
                              on_change=make_toggle(drv),
                          ),
                      ],
                  ),
                  # ردیف دوم: پلاک گرافیکی ایران
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
                  # ردیف سوم: خلاصه بار، مسیر و استعلام سوخت/پروانه
                  ft.Container(
                      bgcolor="#f8fafc",
                      padding=8,
                      border_radius=8,
                      content=ft.Column(
                          spacing=4,
                          controls=[
                              ft.Text(
                                  f"📦 بار: {drv['cargo']} ({drv['weight']} تن - {drv['pack']}) | کرایه: {drv['fare']} ریال | 📍 مسیر: {drv['origin_name']} به {drv['dest_name']} ({drv['distance_km']} km)",
                                  size=11,
                                  color="#334155",
                                  weight="bold",
                              ),
                              ft.Text(
                                  f"⛽ سهمیه سوخت: {drv['fuel_quota']} | 🛡️ پروانه فعالیت: {drv['fleet_license']}",
                                  size=11,
                                  color="#0284c7",
                              ),
                          ],
                      ),
                  ),
                  # ردیف چهارم: دکمه‌های عملیات (صدور، شروع حمل، پایان حمل، ویرایش، حذف)
                  ft.Row(
                      alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                      wrap=True,
                      spacing=6,
                      controls=[
                          ft.ElevatedButton(
                              "ثبت و صدور",
                              bgcolor="#0284c7",
                              color="white",
                              height=34,
                              on_click=make_action(drv, "issue"),
                          ),
                          ft.ElevatedButton(
                              "شروع حمل (اپ)",
                              bgcolor="#16a34a",
                              color="white",
                              height=34,
                              on_click=make_action(drv, "start_trip"),
                          ),
                          ft.ElevatedButton(
                              "پایان حمل (اپ)",
                              bgcolor="#0d9488",
                              color="white",
                              height=34,
                              on_click=make_action(drv, "end_trip"),
                          ),
                          ft.OutlinedButton(
                              "ویرایش / نقشه",
                              height=34,
                              on_click=lambda e, d=drv: open_edit_dialog(d),
                          ),
                          ft.TextButton(
                              "حذف",
                              style=ft.ButtonStyle(color="#dc2626"),
                              on_click=make_delete(drv),
                          ),
                      ],
                  ),
              ],
          ),
      )
      drivers_column.controls.append(card)
    page.update()

  # اجرای دسته‌جمعی اتوماسیون برای تمام پلاک‌های روشن (ON)
  def start_batch_automation(e):
    active_list = [d for d in engine.data["drivers"] if d["active"]]
    if not active_list:
      add_log("هیچ پلاکی در وضعیت روشن (ON) قرار ندارد!", "#dc2626")
      return

    ok, status_msg = engine.check_portal_health()
    add_log(status_msg, "#0284c7")

    for d in active_list:
      # بروزرسانی هوشمند بار و گیرنده تصادفی پیش از هر صدور گروهی
      smart = engine.generate_smart_cargo(d.get("tonnage", 6))
      d["cargo"] = smart["cargo"]
      d["pack"] = smart["pack"]
      d["weight"] = smart["weight"]
      d["fare"] = smart["fare"]
      res = engine.execute_full_cycle(d, "full")
      add_log(res, "#15803d")

    engine.save_data()
    render_drivers()

  # تغییر ظرفیت اشتراک پنل (۵۰ / ۱۰۰ / ۲۰۰ پلاک) برای فروش پنل به مشتریان
  def change_plan_limit(e):
    current = engine.data["license"]["plan_limit"]
    next_plan = 100 if current == 50 else (200 if current == 100 else 50)
    engine.data["license"]["plan_limit"] = next_plan
    engine.save_data()
    update_quota_text()
    add_log(
        f"ظرفیت پنل تجاری به {next_plan} پلاک ارتقا یافت.", "#7c3aed"
    )

  # فیلتر جستجو و گروه
  def on_search_change(e):
    nonlocal search_query
    search_query = e.control.value
    render_drivers()

  def on_group_filter_change(e):
    nonlocal selected_group_filter
    selected_group_filter = e.control.value
    render_drivers()

  search_box = ft.TextField(
      hint_text="جستجوی نام، کد ملی یا پلاک ...",
      prefix_icon=ft.icons.SEARCH,
      bgcolor="white",
      border_radius=12,
      height=45,
      text_size=13,
      expand=True,
      on_change=on_search_change,
  )

  group_filter_dd = ft.Dropdown(
      value="all",
      width=135,
      bgcolor="white",
      border_radius=12,
      options=[
          ft.dropdown.Option("all", "همه گروه‌ها"),
          ft.dropdown.Option("1", "گروه ۱"),
          ft.dropdown.Option("2", "گروه ۲"),
          ft.dropdown.Option("3", "گروه ۳"),
      ],
      on_change=on_group_filter_change,
  )

  render_drivers()
  add_log(
      "پنل تجاری بارگو بندر آماده است. درگاه barname.utcms.ir + سرور موبایل فعال شد.",
      "#0284c7",
  )

  # چیدمان اصلی داشبورد مدیریت کاربران
  page.add(
      ft.Column(
          expand=True,
          scroll=ft.ScrollMode.AUTO,
          spacing=10,
          controls=[
              # هدر بالای پنل
              ft.Container(
                  bgcolor="#0f172a",
                  padding=ft.padding.symmetric(horizontal=16, vertical=14),
                  content=ft.Row(
                      alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                      controls=[
                          ft.Column(
                              spacing=2,
                              controls=[
                                  ft.Text(
                                      "بارگو بندر | سامانه جامع اتوماسیون باربرگ",
                                      color="white",
                                      size=16,
                                      weight="bold",
                                  ),
                                  ft.Text(
                                      "صدور خودکار، شروع و پایان حمل اپ + پایش سهمیه سوخت",
                                      color="#38bdf8",
                                      size=11,
                                  ),
                              ],
                          ),
                          ft.ElevatedButton(
                              "تغییر سقف پنل (50/100/200)",
                              bgcolor="#7c3aed",
                              color="white",
                              height=34,
                              on_click=change_plan_limit,
                          ),
                      ],
                  ),
              ),
              # کادر هشدار سرور موبایل مشابه سناتور
              ft.Container(
                  margin=ft.margin.symmetric(horizontal=12),
                  padding=12,
                  bgcolor="#ffedd5",
                  border=ft.border.all(1, "#fdba74"),
                  border_radius=12,
                  content=ft.Column(
                      spacing=4,
                      controls=[
                          server_banner_text,
                          quota_counter_text,
                      ],
                  ),
              ),
              # دکمه‌های مدیریتی (افزودن کاربر، استارت اتوماسیون گروهی)
              ft.Container(
                  margin=ft.margin.symmetric(horizontal=12),
                  padding=12,
                  bgcolor="white",
                  border_radius=14,
                  content=ft.Column(
                      spacing=10,
                      controls=[
                          ft.Row(
                              alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                              controls=[
                                  ft.Text(
                                      "مدیریت کاربران و ناوگان",
                                      size=16,
                                      weight="bold",
                                      color="#0f172a",
                                  ),
                                  ft.ElevatedButton(
                                      "افزودن کاربر جدید +",
                                      bgcolor="#0284c7",
                                      color="white",
                                      on_click=open_add_driver_dialog,
                                  ),
                              ],
                          ),
                          ft.ElevatedButton(
                              "🚀 استارت اتوماسیون گروهی (صدور + شروع و پایان حمل همه پلاک‌های ON)",
                              bgcolor="#16a34a",
                              color="white",
                              height=46,
                              width=500,
                              on_click=start_batch_automation,
                          ),
                          ft.Row([search_box, group_filter_dd]),
                      ],
                  ),
              ),
              # باکس گزارش زنده ربات
              ft.Container(
                  margin=ft.margin.symmetric(horizontal=12),
                  padding=10,
                  bgcolor="white",
                  border_radius=12,
                  border=ft.border.all(1, "#cbd5e1"),
                  content=ft.Column(
                      spacing=4,
                      controls=[
                          ft.Text(
                              "مانیتورینگ زنده صدور و موقعیت‌یاب (AI Log):",
                              size=12,
                              weight="bold",
                              color="#475569",
                          ),
                          log_list,
                      ],
                  ),
              ),
              # لیست کارت‌های پلاک و رانندگان
              ft.Container(
                  margin=ft.margin.symmetric(horizontal=12),
                  padding=ft.padding.only(bottom=30),
                  content=drivers_column,
              ),
          ],
      )
  )


if __name__ == "__main__":
  ft.app(target=main)
