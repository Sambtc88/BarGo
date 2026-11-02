import flet as ft
import sqlite3
import asyncio
from engine import BarbargEngine

def init_db():
    conn = sqlite3.connect("barbarg_bandar.db", check_same_thread=False)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS panels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT,
                    max_plates INTEGER DEFAULT 50,
                    is_admin INTEGER DEFAULT 0,
                    is_active INTEGER DEFAULT 1
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS drivers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    panel_id INTEGER,
                    name TEXT,
                    national_id TEXT,
                    phone TEXT DEFAULT '',
                    utcms_pass TEXT DEFAULT '',
                    plate_part1 TEXT,
                    plate_letter TEXT,
                    plate_part2 TEXT,
                    plate_iran TEXT,
                    group_num INTEGER DEFAULT 1,
                    is_active INTEGER DEFAULT 1,
                    history TEXT DEFAULT '✓,✓,✓,✓,✓,✓,✗,✓'
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS group_servers (
                    panel_id INTEGER,
                    group_num INTEGER,
                    use_mobile INTEGER DEFAULT 0,
                    proxy_address TEXT DEFAULT '',
                    PRIMARY KEY (panel_id, group_num)
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS cargo_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    panel_id INTEGER,
                    group_num INTEGER DEFAULT 1,
                    cargo_name TEXT,
                    cargo_code TEXT DEFAULT '',
                    weight INTEGER DEFAULT 10000,
                    sender_name TEXT,
                    receiver_name TEXT
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS smart_routes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    panel_id INTEGER,
                    group_num INTEGER DEFAULT 1,
                    origin_address TEXT,
                    origin_postal TEXT DEFAULT '',
                    dest_address TEXT,
                    dest_postal TEXT DEFAULT ''
                )''')
    
    c.execute("INSERT OR IGNORE INTO panels (username, password, max_plates, is_admin, is_active) VALUES ('admin', 'admin123', 200, 1, 1)")
    conn.commit()
    return conn

db_conn = init_db()
bot_engine = BarbargEngine(db_conn)

def main(page: ft.Page):
    page.title = "پنل ثبت باربرگ بندر"
    page.rtl = True
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F2F5F8"
    page.padding = 0

    session = {
        "panel_id": None,
        "username": "",
        "max_plates": 50,
        "is_admin": 0,
        "selected_group": 1,
        "group_running": False,
        "search_query": ""
    }

    def show_msg(text, bg="#1976D2"):
        page.snack_bar = ft.SnackBar(ft.Text(text, color="white", weight=ft.FontWeight.BOLD), bgcolor=bg)
        page.snack_bar.open = True
        page.update()

    def build_plate_ui(p1, letter, p2, iran):
        return ft.Container(
            border=ft.border.all(1.5, "#212121"),
            border_radius=6,
            bgcolor="white",
            width=150,
            height=36,
            content=ft.Row(
                spacing=0,
                controls=[
                    ft.Container(
                        width=32,
                        border=ft.border.only(left=ft.border.BorderSide(1, "#616161")),
                        alignment=ft.alignment.center,
                        content=ft.Column(
                            spacing=0,
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Text("ایران", size=8, weight=ft.FontWeight.BOLD, color="black"),
                                ft.Text(iran, size=11, weight=ft.FontWeight.BOLD, color="black"),
                            ]
                        )
                    ),
                    ft.Expanded(
                        child=ft.Container(
                            alignment=ft.alignment.center,
                            content=ft.Text(f"{p2} {letter} {p1}", size=13, weight=ft.FontWeight.BOLD, color="#D32F2F" if letter == "ع" else "black")
                        )
                    ),
                    ft.Container(
                        width=18,
                        bgcolor="#0D47A1",
                        alignment=ft.alignment.center,
                        content=ft.Text("I.R", size=7, color="white", weight=ft.FontWeight.BOLD)
                    )
                ]
            )
        )

    user_tf = ft.TextField(label="نام کاربری", border_radius=10, prefix_icon=ft.icons.PERSON)
    pass_tf = ft.TextField(label="رمز عبور", password=True, can_reveal_password=True, border_radius=10, prefix_icon=ft.icons.LOCK)
    err_txt = ft.Text("", color="#D32F2F", size=12, weight=ft.FontWeight.BOLD)

    def handle_login(e):
        c = db_conn.cursor()
        c.execute("SELECT id, username, max_plates, is_admin, is_active FROM panels WHERE username=? AND password=?", 
                  (user_tf.value.strip(), pass_tf.value.strip()))
        row = c.fetchone()
        if not row:
            err_txt.value = "نام کاربری یا رمز عبور نادرست است!"
            page.update()
            return
        if row[4] == 0:
            err_txt.value = "این پنل توسط مدیریت غیرفعال شده است!"
            page.update()
            return

        session["panel_id"] = row[0]
        session["username"] = row[1]
        session["max_plates"] = row[2]
        session["is_admin"] = row[3]
        err_txt.value = ""
        launch_dashboard()

    login_screen = ft.Container(
        expand=True,
        alignment=ft.alignment.center,
        padding=20,
        content=ft.Card(
            elevation=5,
            content=ft.Container(
                width=370,
                padding=30,
                bgcolor="white",
                border_radius=15,
                content=ft.Column(
                    tight=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            padding=15, border_radius=50, bgcolor="#E3F2FD",
                            content=ft.Icon(ft.icons.DIRECTIONS_BOAT_FILLED_ROUNDED, size=48, color="#0277BD")
                        ),
                        ft.Text("پنل ثبت باربرگ بندر", size=22, weight=ft.FontWeight.BOLD, color="#01579B"),
                        ft.Text("سامانه هوشمند مدیریت ناوگان و صدور باربرگ", size=12, color="#757575"),
                        ft.Divider(height=20),
                        user_tf,
                        pass_tf,
                        err_txt,
                        ft.Container(height=5),
                        ft.ElevatedButton(
                            "ورود به پنل کاربری",
                            width=310, height=46,
                            bgcolor="#0277BD", color="white",
                            on_click=handle_login
                        )
                    ]
                )
            )
        )
    )

    main_body = ft.Container(expand=True, padding=12)

    def render_users_tab(filter_group="all"):
        c = db_conn.cursor()
        c.execute("SELECT COUNT(*) FROM drivers WHERE panel_id=?", (session["panel_id"],))
        total_used = c.fetchone()[0]
        max_limit = session["max_plates"]
        rem_plates = max(0, max_limit - total_used)

        query = "SELECT id, name, national_id, plate_part1, plate_letter, plate_part2, plate_iran, group_num, is_active, phone FROM drivers WHERE panel_id=?"
        params = [session["panel_id"]]
        if filter_group != "all":
            query += " AND group_num=?"
            params.append(int(filter_group))
        if session["search_query"]:
            q = f"%{session['search_query']}%"
            query += " AND (name LIKE ? OR national_id LIKE ? OR plate_part2 LIKE ?)"
            params.extend([q, q, q])

        c.execute(query, tuple(params))
        drivers_list = c.fetchall()

        def open_driver_modal(edit_data=None):
            if not edit_data and total_used >= max_limit:
                show_msg(f"ظرفیت پک شما ({max_limit} پلاک) تکمیل شده است!", "#D32F2F")
                return

            f_name = ft.TextField(label="نام و نام خانوادگی راننده", value=edit_data[1] if edit_data else "")
            f_nid = ft.TextField(label="کد ملی راننده", value=edit_data[2] if edit_data else "")
            f_phone = ft.TextField(label="شماره موبایل", value=edit_data[9] if edit_data else "")
            f_p2 = ft.TextField(label="سه رقم (۴۴۸)", value=edit_data[5] if edit_data else "", width=95)
            f_let = ft.TextField(label="حرف (ع)", value=edit_data[4] if edit_data else "ع", width=65)
            f_p1 = ft.TextField(label="دو رقم (۵۵)", value=edit_data[3] if edit_data else "", width=85)
            f_ir = ft.TextField(label="ایران (۸۴)", value=edit_data[6] if edit_data else "۸۴", width=75)
            f_grp = ft.TextField(label="شماره گروه (۱ تا ۱۰)", value=str(edit_data[7]) if edit_data else "1")

            def save_driver(e):
                if not f_name.value or not f_nid.value or not f_p2.value:
                    show_msg("لطفاً نام، کد ملی و پلاک را کامل وارد کنید", "#E65100")
                    return
                cur = db_conn.cursor()
                if edit_data:
                    cur.execute('''UPDATE drivers SET name=?, national_id=?, phone=?, plate_part1=?, plate_letter=?, plate_part2=?, plate_iran=?, group_num=?
                                   WHERE id=? AND panel_id=?''',
                                (f_name.value, f_nid.value, f_phone.value, f_p1.value, f_let.value, f_p2.value, f_ir.value, int(f_grp.value), edit_data[0], session["panel_id"]))
                else:
                    cur.execute('''INSERT INTO drivers (panel_id, name, national_id, phone, plate_part1, plate_letter, plate_part2, plate_iran, group_num)
                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                (session["panel_id"], f_name.value, f_nid.value, f_phone.value, f_p1.value, f_let.value, f_p2.value, f_ir.value, int(f_grp.value)))
                db_conn.commit()
                dlg.open = False
                render_users_tab(filter_group)

            dlg = ft.AlertDialog(
                title=ft.Text("ویرایش راننده" if edit_data else "افزودن راننده به پنل"),
                content=ft.Column(
                    tight=True,
                    controls=[f_name, f_nid, f_phone, ft.Row([f_p2, f_let, f_p1, f_ir], spacing=5), f_grp]
                ),
                actions=[
                    ft.TextButton("انصراف", on_click=lambda e: setattr(dlg, 'open', False) or page.update()),
                    ft.ElevatedButton("ذخیره اطلاعات", bgcolor="#0277BD", color="white", on_click=save_driver)
                ]
            )
            page.dialog = dlg
            dlg.open = True
            page.update()

        def open_bulk_modal(e):
            bulk_tf = ft.TextField(
                label="اطلاعات را خط به خط وارد کنید",
                hint_text="نام راننده,کدملی,دورقم,حرف,سه‌رقم,ایران,گروه\nمثال:\nعباس طابه,3440848760,53,ع,863,84,1",
                multiline=True, min_lines=6, max_lines=10
            )
            def save_bulk(ev):
                lines = [l.strip() for l in bulk_tf.value.split("\n") if l.strip()]
                if total_used + len(lines) > max_limit:
                    show_msg(f"خطا! سقف باقی‌مانده پک شما {rem_plates} پلاک است.", "#D32F2F")
                    return
                cur = db_conn.cursor()
                added = 0
                for line in lines:
                    parts = [p.strip() for p in line.replace("،", ",").split(",")]
                    if len(parts) >= 6:
                        grp = int(parts[6]) if len(parts) >= 7 and parts[6].isdigit() else 1
                        cur.execute('''INSERT INTO drivers (panel_id, name, national_id, plate_part1, plate_letter, plate_part2, plate_iran, group_num)
                                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                                    (session["panel_id"], parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], grp))
                        added += 1
                db_conn.commit()
                b_dlg.open = False
                show_msg(f"تعداد {added} پلاک به صورت گروهی ثبت شد", "#2E7D32")
                render_users_tab(filter_group)

            b_dlg = ft.AlertDialog(
                title=ft.Text("افزودن گروهی پلاک‌ها"),
                content=bulk_tf,
                actions=[
                    ft.TextButton("انصراف", on_click=lambda ev: setattr(b_dlg, 'open', False) or page.update()),
                    ft.ElevatedButton("ثبت گروهی", bgcolor="#2E7D32", color="white", on_click=save_bulk)
                ]
            )
            page.dialog = b_dlg
            b_dlg.open = True
            page.update()

        def open_move_group_modal(e):
            src_dd = ft.Dropdown(label="گروه مبدأ", options=[ft.dropdown.Option(str(i), f"گروه {i}") for i in range(1, 11)])
            dst_tf = ft.TextField(label="گروه مقصد", value="2")
            chk_container = ft.Column(scroll=ft.ScrollMode.AUTO, height=180)
            selected_ids = set()

            def on_src_change(ev):
                selected_ids.clear()
                chk_container.controls.clear()
                cur = db_conn.cursor()
                cur.execute("SELECT id, name, plate_part1, plate_letter, plate_part2 FROM drivers WHERE panel_id=? AND group_num=?",
                            (session["panel_id"], int(src_dd.value)))
                for r in cur.fetchall():
                    def make_chk(d_id):
                        def on_chk(c_ev):
                            if c_ev.control.value:
                                selected_ids.add(d_id)
                            else:
                                selected_ids.discard(d_id)
                        return on_chk
                    chk_container.controls.append(ft.Checkbox(label=f"{r[1]} ({r[4]}{r[3]}{r[2]})", on_change=make_chk(r[0])))
                page.update()

            src_dd.on_change = on_src_change

            def do_transfer(ev):
                if not selected_ids or not dst_tf.value.isdigit():
                    return
                cur = db_conn.cursor()
                for d_id in selected_ids:
                    cur.execute("UPDATE drivers SET group_num=? WHERE id=? AND panel_id=?", (int(dst_tf.value), d_id, session["panel_id"]))
                db_conn.commit()
                m_dlg.open = False
                render_users_tab(filter_group)

            m_dlg = ft.AlertDialog(
                title=ft.Text("جابجایی گروه"),
                content=ft.Column(
                    tight=True,
                    controls=[src_dd, dst_tf, ft.Text("رانندگان (تیک بزنید):", size=12), ft.Container(border=ft.border.all(1, "#E0E0E0"), border_radius=8, padding=8, content=chk_container)]
                ),
                actions=[
                    ft.OutlinedButton("انصراف", on_click=lambda ev: setattr(m_dlg, 'open', False) or page.update()),
                    ft.ElevatedButton("انتقال انتخاب‌شده‌ها", bgcolor="#1565C0", color="white", on_click=do_transfer)
                ]
            )
            page.dialog = m_dlg
            m_dlg.open = True
            page.update()

        driver_rows = []
        for idx, d in enumerate(drivers_list, 1):
            def make_toggle(d_id):
                def _toggle(ev):
                    db_conn.cursor().execute("UPDATE drivers SET is_active=? WHERE id=?", (1 if ev.control.value else 0, d_id))
                    db_conn.commit()
                return _toggle

            def make_del(d_id):
                def _del(ev):
                    db_conn.cursor().execute("DELETE FROM drivers WHERE id=? AND panel_id=?", (d_id, session["panel_id"]))
                    db_conn.commit()
                    render_users_tab(filter_group)
                return _del

            def make_edit(d_row):
                return lambda ev: open_driver_modal(d_row)

            driver_rows.append(
                ft.Container(
                    bgcolor="white", padding=10, border_radius=12, margin=ft.margin.only(bottom=8),
                    border=ft.border.all(1, "#E0E0E0"),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.CircleAvatar(content=ft.Text(str(idx), size=12), radius=14, bgcolor="#E3F2FD", color="#0D47A1"),
                            ft.Column([ft.Text(d[1], weight=ft.FontWeight.BOLD, size=13), ft.Text(d[2], size=11, color="#757575")], spacing=2, width=105),
                            build_plate_ui(d[3], d[4], d[5], d[6]),
                            ft.CircleAvatar(content=ft.Text(str(d[7]), size=12, weight=ft.FontWeight.BOLD), radius=14, bgcolor="#EEEEEE", color="black"),
                            ft.Column(
                                spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Switch(value=bool(d[8]), active_color="#43A047", height=28, on_change=make_toggle(d[0])),
                                    ft.ElevatedButton("ویرایش", height=26, width=68, bgcolor="#1976D2", color="white", on_click=make_edit(d)),
                                    ft.OutlinedButton("حذف", height=26, width=68, on_click=make_del(d[0]))
                                ]
                            )
                        ]
                    )
                )
            )

        main_body.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(
                    bgcolor="white", padding=15, border_radius=15, border=ft.border.all(1, "#E0E0E0"),
                    content=ft.Column([
                        ft.Text("مدیریت کاربران (پنل ثبت باربرگ بندر)", size=18, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.OutlinedButton("افزودن دستی", expand=True, on_click=lambda e: open_driver_modal(None)),
                            ft.ElevatedButton("افزودن کاربر", expand=True, bgcolor="#1565C0", color="white", on_click=lambda e: open_driver_modal(None)),
                            ft.OutlinedButton("افزودن گروهی", expand=True, on_click=open_bulk_modal),
                        ]),
                        ft.Container(
                            padding=8, bgcolor="#E3F2FD", border_radius=8, alignment=ft.alignment.center,
                            content=ft.Text(f"نمایش: {len(drivers_list)} از {total_used} | سقف پک: {max_limit} | باقی‌مانده: {rem_plates}", size=13, weight=ft.FontWeight.BOLD, color="#0D47A1")
                        ),
                        ft.OutlinedButton("جابجایی گروه", width=float("inf"), on_click=open_move_group_modal),
                        ft.Row([
                            ft.Dropdown(
                                width=130, value=filter_group,
                                options=[ft.dropdown.Option("all", "همه گروه‌ها")] + [ft.dropdown.Option(str(i), f"گروه {i}") for i in range(1, 11)],
                                on_change=lambda ev: render_users_tab(ev.control.value)
                            ),
                            ft.TextField(
                                hint_text="جستجوی نام، کد ملی یا پلاک ...",
                                value=session["search_query"], expand=True, height=45, content_padding=10,
                                on_submit=lambda ev: (session.update({"search_query": ev.control.value}), render_users_tab(filter_group))
                            )
                        ])
                    ])
                ),
                ft.Column(controls=driver_rows)
            ]
        )
        page.update()

    def render_barbarg_tab():
        grp = session["selected_group"]
        c = db_conn.cursor()
        
        c.execute("SELECT use_mobile, proxy_address FROM group_servers WHERE panel_id=? AND group_num=?", (session["panel_id"], grp))
        srv_row = c.fetchone()
        use_mob = bool(srv_row[0]) if srv_row else False
        mob_addr = srv_row[1] if srv_row else ""

        c.execute("SELECT id, name, national_id, plate_part1, plate_letter, plate_part2, plate_iran, history FROM drivers WHERE panel_id=? AND group_num=? AND is_active=1",
                  (session["panel_id"], grp))
        active_drivers = c.fetchall()

        is_grp_running = bot_engine.is_running(session["panel_id"], grp)
        session["group_running"] = is_grp_running

        def toggle_mobile_srv(e):
            new_val = 0 if use_mob else 1
            cur = db_conn.cursor()
            cur.execute('''INSERT INTO group_servers (panel_id, group_num, use_mobile, proxy_address)
                           VALUES (?, ?, ?, ?)
                           ON CONFLICT(panel_id, group_num) DO UPDATE SET use_mobile=?''',
                        (session["panel_id"], grp, new_val, mob_addr, new_val))
            db_conn.commit()
            render_barbarg_tab()

        def start_operation(mode_name):
            if bot_engine.is_running(session["panel_id"], grp):
                show_msg(f"گروه {grp} هم‌اکنون در حال اجراست!", "#E65100")
                return
            srv_type = f"سرور آنتن موبایل ({mob_addr or 'متصل'})" if use_mob else "سرور مستقیم سامانه"
            show_msg(f"عملیات «{mode_name}» برای گروه {grp} روی [{srv_type}] آغاز شد.", "#2E7D32")
            page.run_task(bot_engine.run_group_cycle, session["panel_id"], grp, mode_name, render_barbarg_tab)
            render_barbarg_tab()

        def stop_operation(e):
            bot_engine.stop_group(session["panel_id"], grp)
            session["group_running"] = False
            show_msg(f"فرمان توقف به گروه {grp} ارسال شد.", "#C62828")
            render_barbarg_tab()

        cards = []
        for idx, d in enumerate(active_drivers, 1):
            h_list = d[7].split(",") if d[7] else []
            t_icons = []
            for item in h_list:
                ok = (item == "✓")
                t_icons.append(
                    ft.Container(
                        width=24, height=24, border_radius=12,
                        bgcolor="#E8F5E9" if ok else "#FFEBEE", alignment=ft.alignment.center,
                        content=ft.Text(item, color="#2E7D32" if ok else "#C62828", size=12, weight=ft.FontWeight.BOLD)
                    )
                )

            cards.append(
                ft.Container(
                    bgcolor="white", padding=12, border_radius=12, margin=ft.margin.only(bottom=10),
                    border=ft.border.all(1, "#E0E0E0"),
                    content=ft.Column([
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row([ft.CircleAvatar(content=ft.Text(str(idx), size=12), radius=12, bgcolor="#E3F2FD", color="#0D47A1"), ft.Text(d[1], weight=ft.FontWeight.BOLD, size=14)]),
                                ft.Text(d[2], size=12, color="#757575")
                            ]
                        ),
                        ft.Divider(height=8),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[build_plate_ui(d[3], d[4], d[5], d[6]), ft.Row(spacing=4, controls=t_icons)]
                        )
                    ])
                )
            )

        main_body.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(
                    bgcolor="white", padding=15, border_radius=15, border=ft.border.all(1, "#E0E0E0"),
                    content=ft.Column([
                        ft.Text("باربرگ (پنل ثبت باربرگ بندر)", size=18, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.Dropdown(
                                expand=True, value=str(grp),
                                options=[ft.dropdown.Option(str(i), f"گروه {i}") for i in range(1, 11)],
                                on_change=lambda ev: (session.update({"selected_group": int(ev.control.value)}), render_barbarg_tab())
                            ),
                            ft.OutlinedButton("بروزرسانی لیست", expand=True, on_click=lambda ev: render_barbarg_tab())
                        ]),
                        ft.Container(
                            width=float("inf"), padding=12, border_radius=10,
                            bgcolor="#E8F5E9" if session["group_running"] else "#ECEFF1", alignment=ft.alignment.center,
                            content=ft.Text(
                                f"در حال صدور خودکار باربرگ (گروه {grp})..." if session["group_running"] else "متوقف",
                                weight=ft.FontWeight.BOLD, color="#2E7D32" if session["group_running"] else "#37474F"
                            )
                        ),
                        ft.OutlinedButton(
                            text=f"متصل به سرور آنتن موبایل ({mob_addr or 'آی‌پی سیم‌کارت فعال'})" if use_mob else "این گروه از سرور موبایل استفاده نمی‌کند",
                            icon=ft.icons.CELL_TOWER if use_mob else ft.icons.DNS,
                            width=float("inf"), on_click=toggle_mobile_srv
                        ),
                        ft.Row(
                            scroll=ft.ScrollMode.AUTO, spacing=6,
                            controls=[
                                ft.ElevatedButton("تاریخچه", icon=ft.icons.HISTORY, bgcolor="#EF6C00", color="white"),
                                ft.ElevatedButton("شروع", icon=ft.icons.PLAY_ARROW, bgcolor="#43A047", color="white", on_click=lambda e: start_operation("شروع عادی")),
                                ft.ElevatedButton("شروع هوشمند", icon=ft.icons.STAR, bgcolor="#F9A825", color="white", on_click=lambda e: start_operation("شروع هوشمند")),
                                ft.ElevatedButton("شروع ۲", icon=ft.icons.LOOKS_TWO, bgcolor="#8E24AA", color="white", on_click=lambda e: start_operation("شروع ۲")),
                                ft.ElevatedButton("توقف", icon=ft.icons.STOP, bgcolor="#1E88E5", color="white", on_click=stop_operation),
                            ]
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.TextField(hint_text="جستجوی نام، کد ملی یا پلاک", expand=True, height=40, content_padding=8),
                                ft.Container(padding=8, bgcolor="#F5F5F5", border_radius=8, content=ft.Text(f"تعداد راننده‌ها: {len(active_drivers)}", size=12, weight=ft.FontWeight.BOLD))
                            ]
                        )
                    ])
                ),
                ft.Column(controls=cards)
            ]
        )
        page.update()

    def open_mobile_server_settings():
        grp_dd = ft.Dropdown(label="انتخاب گروه", value="1", options=[ft.dropdown.Option(str(i), f"گروه {i}") for i in range(1, 11)])
        proxy_tf = ft.TextField(label="آدرس پراکسی / تانل آنتن موبایل", hint_text="http://192.168.1.55:8080")
        use_sw = ft.Switch(label="استفاده اجباری این گروه از اینترنت آنتن موبایل", value=True)

        def load_grp_srv(ev=None):
            cur = db_conn.cursor()
            cur.execute("SELECT use_mobile, proxy_address FROM group_servers WHERE panel_id=? AND group_num=?", (session["panel_id"], int(grp_dd.value)))
            r = cur.fetchone()
            use_sw.value = bool(r[0]) if r else False
            proxy_tf.value = r[1] if r else ""
            page.update()

        grp_dd.on_change = load_grp_srv
        load_grp_srv()

        def save_srv(ev):
            cur = db_conn.cursor()
            cur.execute('''INSERT INTO group_servers (panel_id, group_num, use_mobile, proxy_address)
                           VALUES (?, ?, ?, ?)
                           ON CONFLICT(panel_id, group_num) DO UPDATE SET use_mobile=?, proxy_address=?''',
                        (session["panel_id"], int(grp_dd.value), 1 if use_sw.value else 0, proxy_tf.value.strip(), 1 if use_sw.value else 0, proxy_tf.value.strip()))
            db_conn.commit()
            s_dlg.open = False
            show_msg(f"تنظیمات سرور موبایل گروه {grp_dd.value} ذخیره شد", "#2E7D32")

        s_dlg = ft.AlertDialog(
            title=ft.Text("مدیریت سرورها و آنتن موبایل"),
            content=ft.Column(tight=True, controls=[grp_dd, proxy_tf, use_sw]),
            actions=[
                ft.TextButton("بستن", on_click=lambda e: setattr(s_dlg, 'open', False) or page.update()),
                ft.ElevatedButton("ذخیره سرور گروه", bgcolor="#0277BD", color="white", on_click=save_srv)
            ]
        )
        page.dialog = s_dlg
        s_dlg.open = True
        page.update()

    def open_cargo_rotation_modal():
        grp_dd = ft.Dropdown(label="انتخاب گروه", value="1", width=130, options=[ft.dropdown.Option(str(i), f"گروه {i}") for i in range(1, 11)])
        c_name = ft.TextField(label="نام کالا", expand=True)
        c_weight = ft.TextField(label="وزن (کیلوگرم)", value="15000", width=120)
        c_sender = ft.TextField(label="نام فرستنده", expand=True)
        c_receiver = ft.TextField(label="نام گیرنده", expand=True)
        cargo_list_col = ft.Column(scroll=ft.ScrollMode.AUTO, height=160)

        def refresh_cargos(ev=None):
            cargo_list_col.controls.clear()
            cur = db_conn.cursor()
            cur.execute("SELECT id, cargo_name, weight, sender_name, receiver_name FROM cargo_types WHERE panel_id=? AND group_num=?", (session["panel_id"], int(grp_dd.value)))
            for r in cur.fetchall():
                def make_del_c(cid):
                    def _d(e):
                        db_conn.cursor().execute("DELETE FROM cargo_types WHERE id=?", (cid,))
                        db_conn.commit()
                        refresh_cargos()
                    return _d
                cargo_list_col.controls.append(
                    ft.Container(
                        bgcolor="#F5F7FA", padding=8, border_radius=8,
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(f"{r[1]} ({r[2]} ک.گ) | {r[3]} ⬅ {r[4]}", size=12, weight=ft.FontWeight.BOLD),
                                ft.IconButton(ft.icons.DELETE_OUTLINE, icon_color="#C62828", icon_size=18, on_click=make_del_c(r[0]))
                            ]
                        )
                    )
                )
            page.update()

        grp_dd.on_change = refresh_cargos

        def add_cargo(ev):
            if not c_name.value:
                return
            db_conn.cursor().execute("""INSERT INTO cargo_types (panel_id, group_num, cargo_name, weight, sender_name, receiver_name)
                                        VALUES (?, ?, ?, ?, ?, ?)""",
                                     (session["panel_id"], int(grp_dd.value), c_name.value, int(c_weight.value or 10000), c_sender.value, c_receiver.value))
            db_conn.commit()
            c_name.value = ""
            refresh_cargos()

        refresh_cargos()
        dlg = ft.AlertDialog(
            title=ft.Text("تعیین نوع بار (چرخش خودکار)"),
            content=ft.Column(
                tight=True,
                controls=[ft.Row([grp_dd, c_name, c_weight]), ft.Row([c_sender, c_receiver]), ft.ElevatedButton("افزودن به چرخش بار", bgcolor="#2E7D32", color="white", width=float("inf"), on_click=add_cargo), ft.Divider(), cargo_list_col]
            ),
            actions=[ft.TextButton("بستن", on_click=lambda e: setattr(dlg, 'open', False) or page.update())]
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def open_smart_routes_modal():
        grp_dd = ft.Dropdown(label="انتخاب گروه", value="1", width=130, options=[ft.dropdown.Option(str(i), f"گروه {i}") for i in range(1, 11)])
        orig_tf = ft.TextField(label="آدرس مبدأ", expand=True)
        dest_tf = ft.TextField(label="آدرس مقصد", expand=True)
        routes_col = ft.Column(scroll=ft.ScrollMode.AUTO, height=160)

        def refresh_routes(ev=None):
            routes_col.controls.clear()
            cur = db_conn.cursor()
            cur.execute("SELECT id, origin_address, dest_address FROM smart_routes WHERE panel_id=? AND group_num=?", (session["panel_id"], int(grp_dd.value)))
            for idx, r in enumerate(cur.fetchall(), 1):
                def make_del_r(rid):
                    def _d(e):
                        db_conn.cursor().execute("DELETE FROM smart_routes WHERE id=?", (rid,))
                        db_conn.commit()
                        refresh_routes()
                    return _d
                routes_col.controls.append(
                    ft.Container(
                        bgcolor="#F3E5F5", padding=8, border_radius=8,
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(f"مسیر {idx}: {r[1]} ⬅ {r[2]}", size=12, weight=ft.FontWeight.BOLD),
                                ft.IconButton(ft.icons.DELETE_OUTLINE, icon_color="#C62828", icon_size=18, on_click=make_del_r(r[0]))
                            ]
                        )
                    )
                )
            page.update()

        grp_dd.on_change = refresh_routes

        def add_route(ev):
            if not orig_tf.value or not dest_tf.value:
                return
            db_conn.cursor().execute("INSERT INTO smart_routes (panel_id, group_num, origin_address, dest_address) VALUES (?, ?, ?, ?)",
                                     (session["panel_id"], int(grp_dd.value), orig_tf.value, dest_tf.value))
            db_conn.commit()
            orig_tf.value = ""
            dest_tf.value = ""
            refresh_routes()

        refresh_routes()
        dlg = ft.AlertDialog(
            title=ft.Text("آدرس‌های زنجیره‌ای و شروع هوشمند"),
            content=ft.Column(
                tight=True,
                controls=[grp_dd, orig_tf, dest_tf, ft.ElevatedButton("افزودن مسیر به زنجیره", bgcolor="#6A1B9A", color="white", width=float("inf"), on_click=add_route), ft.Divider(), routes_col]
            ),
            actions=[ft.TextButton("بستن", on_click=lambda e: setattr(dlg, 'open', False) or page.update())]
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def render_features_tab():
        items = [
            ("شروع و پایان حمل", "مدیریت عملیات پلاک‌ها", ft.icons.LOCAL_SHIPPING, "#E3F2FD", lambda e: render_barbarg_tab()),
            ("تعیین نوع بار", "چرخش کالا و فرستنده/گیرنده", ft.icons.INVENTORY_2, "#E8F5E9", lambda e: open_cargo_rotation_modal()),
            ("آدرس‌ها", "مدیریت نقشه و آدرس رانندگان", ft.icons.LOCATION_ON, "#E0F7FA", lambda e: open_smart_routes_modal()),
            ("مدیریت سرورها", "تنظیم سرور سامانه یا آنتن موبایل", ft.icons.CELL_
