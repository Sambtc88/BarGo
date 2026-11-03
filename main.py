import http.server
import sqlite3
import urllib.parse
import http.cookies
import random
from datetime import datetime, timedelta
from engine import BarbargEngine

PORT = 2727
engine = BarbargEngine()

def init_db():
    conn = sqlite3.connect("barbarg_bandar.db", check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS panels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT,
                    max_plates INTEGER DEFAULT 50,
                    is_admin INTEGER DEFAULT 0,
                    is_active INTEGER DEFAULT 1,
                    expire_date TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS servers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_name TEXT,
                    group_assigned TEXT,
                    status TEXT DEFAULT 'active'
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS drivers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    panel_id INTEGER,
                    name TEXT,
                    national_id TEXT,
                    plate_part1 TEXT,
                    plate_letter TEXT,
                    plate_part2 TEXT,
                    plate_iran TEXT,
                    vehicle_class TEXT,
                    max_load_ton REAL,
                    group_num INTEGER DEFAULT 1,
                    issue_status INTEGER DEFAULT 1,
                    transport_status INTEGER DEFAULT 1,
                    is_active INTEGER DEFAULT 1
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS receipts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    panel_id INTEGER,
                    username TEXT,
                    tracking_code TEXT,
                    amount TEXT,
                    status TEXT DEFAULT 'pending'
                )''')
    
    expire_admin = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
    c.execute("INSERT OR IGNORE INTO panels (username, password, max_plates, is_admin, is_active, expire_date) VALUES ('DAVOOD', 'Dp9498Dp', 1000, 1, 1, ?)", (expire_admin,))
    
    c.execute("INSERT OR IGNORE INTO servers (ip_name, group_assigned, status) VALUES ('IP 001', 'آماده انتخاب', 'active')")
    c.execute("INSERT OR IGNORE INTO servers (ip_name, group_assigned, status) VALUES ('IP 003', 'گروه ۲', 'busy')")
    c.execute("INSERT OR IGNORE INTO servers (ip_name, group_assigned, status) VALUES ('IP 391', 'گروه ۱', 'active')")
    
    conn.commit()
    return conn

db_conn = init_db()

def generate_random_receiver():
    first_names = ["علی", "محمد", "رضا", "مهدی", "حسین", "حسن", "احمد", "محسن", "عباس", "سعید"]
    last_names = ["پوراصفهانی", "کریمی", "موسوی", "حیدری", "قاسمی", "مرادی", "صادقی", "زارعی", "رضایی", "کریمیان"]
    phone_prefix = ["0917", "0936", "0990", "0913", "0902"]
    return f"{random.choice(first_names)} {random.choice(last_names)}", f"{random.choice(phone_prefix)}{random.randint(100, 999)}{random.randint(1000, 9999)}"

class BarbargHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        if path == "/logout":
            self.send_response(303)
            self.send_header('Location', '/')
            self.send_header('Set-Cookie', 'session=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT')
            self.end_headers()
            return

        if path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            
            cookie = http.cookies.SimpleCookie(self.headers.get('Cookie'))
            username = cookie.get('session').value if 'session' in cookie else None

            if not username:
                # صفحه لاگین اختصاصی با دیزاین شبیه سناتور، رنگ‌بندی جذاب، تصویر کامیونت و متن کامل
                html = """<!DOCTYPE html>
                <html lang="fa" dir="rtl">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>ورود - سامانه هوشمند بارگوبندر</title>
                    <style>
                        body { font-family: Tahoma, Arial, sans-serif; background: linear-gradient(135deg, #0B132B 0%, #1C2541 50%, #28385E 100%); margin: 0; display: flex; align-items: center; justify-content: center; min-height: 100vh; direction: rtl; }
                        .login-container { width: 100%; max-width: 400px; padding: 20px; box-sizing: border-box; text-align: center; }
                        
                        /* باکس لوگو و کامیونت */
                        .logo-box { margin-bottom: 20px; }
                        .truck-icon { width: 90px; height: 65px; background: linear-gradient(135deg, #00B4D8, #0077B6); border-radius: 14px; display: inline-flex; align-items: center; justify-content: center; box-shadow: 0 10px 25px rgba(0,180,216,0.4); margin-bottom: 12px; }
                        .truck-icon svg { width: 50px; height: 50px; fill: #ffffff; }
                        .brand-en { font-size: 26px; font-weight: 800; letter-spacing: 1px; color: #00B4D8; margin: 0; text-transform: uppercase; }
                        .brand-fa { font-size: 20px; font-weight: bold; color: #F1F5F9; margin-top: 5px; margin-bottom: 25px; }

                        /* فرم ورود مشابه سناتور ولی شیک‌تر */
                        .form-card { background: rgba(255, 255, 255, 0.98); padding: 30px 25px; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.3); text-align: right; }
                        .form-group { margin-bottom: 15px; }
                        .form-group label { display: block; font-size: 13px; color: #334155; margin-bottom: 6px; font-weight: bold; }
                        input[type="text"], input[type="password"] { width: 100%; padding: 14px; background: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 12px; box-sizing: border-box; color: #1E293B; font-size: 15px; outline: none; transition: 0.3s; }
                        input:focus { border-color: #00B4D8; background: #fff; box-shadow: 0 0 8px rgba(0,180,216,0.2); }
                        
                        .captcha-box { background: #F8FAFC; border: 1px solid #CBD5E1; padding: 12px; border-radius: 12px; display: flex; align-items: center; justify-content: space-between; margin: 15px 0; font-size: 13px; color: #475569; }
                        .rules-box { display: flex; align-items: center; gap: 8px; margin: 15px 0; font-size: 13px; color: #334155; }
                        .rules-box a { color: #E53E3E; text-decoration: none; font-weight: bold; }

                        .btn-submit { background: linear-gradient(135deg, #00B4D8, #0077B6); color: white; border: none; padding: 15px; width: 100%; border-radius: 12px; font-weight: bold; cursor: pointer; font-size: 16px; box-shadow: 0 8px 20px rgba(0,180,216,0.4); transition: 0.3s; }
                        .btn-submit:hover { opacity: 0.95; transform: translateY(-2px); }

                        .footer-text { margin-top: 25px; font-size: 12px; color: #94A3B8; text-align: center; line-height: 1.6; }
                    </style>
                </head>
                <body>
                    <div class="login-container">
                        <div class="logo-box">
                            <!-- آیکون اختصاصی کامیونت باربرگ -->
                            <div class="truck-icon">
                                <svg viewBox="0 0 24 24"><path d="M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4zM6 18.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm13.5-9l1.96 2.5H17V9.5h2.5zm-1.5 9c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z"/></svg>
                            </div>
                            <div class="brand-en">Bargo Bandar</div>
                            <div class="brand-fa">بارگوبندر</div>
                        </div>

                        <div class="form-card">
                            <form method="POST" action="/login">
                                <div class="form-group">
                                    <label>نام کاربری</label>
                                    <input type="text" name="username" placeholder="نام کاربری" required>
                                </div>
                                <div class="form-group">
                                    <label>کلمه عبور</label>
                                    <input type="password" name="password" placeholder="کلمه عبور" required>
                                </div>

                                <div class="captcha-box">
                                    <label style="display:flex; align-items:center; gap:8px; cursor:pointer;">
                                        <input type="checkbox" style="width:20px; height:20px; accent-color:#00B4D8;" required>
                                        <span>من ربات نیستم</span>
                                    </label>
                                    <span style="color:#0284C7; font-size:12px; font-weight:bold;">امن 🛡️</span>
                                </div>

                                <div class="rules-box">
                                    <input type="checkbox" style="width:18px; height:18px; accent-color:#00B4D8;" required>
                                    <span><a href="#">قوانین</a> را مطالعه و قبول دارم</span>
                                </div>

                                <button type="submit" class="btn-submit">ورود</button>
                            </form>
                        </div>

                        <div class="footer-text">
                            سامانه مدیریت پیشرفته باربرگ و ناوگان درون‌شهری
                        </div>
                    </div>
                </body>
                </html>"""
            else:
                c = db_conn.cursor()
                c.execute("SELECT id, max_plates, is_admin, expire_date FROM panels WHERE username = ?", (username,))
                panel_data = c.fetchone()
                
                if not panel_data:
                    self.wfile.write("خطای دسترسی".encode("utf-8"))
                    return

                panel_id, max_plates, is_admin, expire_date_str = panel_data

                try:
                    days_left = max(0, (datetime.strptime(expire_date_str, '%Y-%m-%d') - datetime.now()).days)
                except:
                    days_left = 30

                current_server_mode = engine.auto_switch_server()
                server_display_name = "سرور اصلی سامانه درون‌شهری (پایدار)" if current_server_mode == "urban_main" else "سرور موبایل / هات‌اسپات (سوییچ خودکار هوشمند)"
                server_badge_color = "#2E7D32" if current_server_mode == "urban_main" else "#E65100"

                if is_admin == 1:
                    c.execute("SELECT id, username, max_plates, expire_date FROM panels WHERE is_admin = 0")
                    all_customers = c.fetchall()
                    customers_html = ""
                    for cust in all_customers:
                        try:
                            c_days = max(0, (datetime.strptime(cust[3], '%Y-%m-%d') - datetime.now()).days)
                        except:
                            c_days = 0
                        customers_html += f"<tr><td>{cust[1]}</td><td>{cust[2]} پلاک</td><td>{c_days} روز</td><td><a href='/renew_panel?id={cust[0]}' style='color:green; margin-left:10px; font-weight:bold;'>تمدید</a> <a href='/delete_panel?id={cust[0]}' style='color:red; font-weight:bold;'>حذف</a></td></tr>"

                    c.execute("SELECT id, username, tracking_code, amount FROM receipts WHERE status = 'pending'")
                    pending_receipts = c.fetchall()
                    receipts_html = ""
                    for rec in pending_receipts:
                        receipts_html += f"<tr><td>{rec[1]}</td><td>کد: {rec[2]} - {rec[3]} ریال</td><td><a href='/approve_receipt?id={rec[0]}' style='color:green; font-weight:bold;'>تایید</a></td></tr>"

                    c.execute("SELECT id, ip_name, group_assigned, status FROM servers")
                    all_servers = c.fetchall()
                    servers_html = ""
                    for s in all_servers:
                        s_col = "#2E7D32" if s[3] == "active" else "#C62828"
                        servers_html += f"<div style='background:#f9f9f9; border:1px solid #ddd; padding:10px; border-radius:8px; margin:5px 0; display:flex; justify-content:space-between; align-items:center;'><span><b>{s[1]}</b> ({s[2]})</span><span style='color:{s_col}; font-weight:bold;'>{'فعال' if s[3]=='active' else 'اشغال'}</span></div>"

                    html = f"""<!DOCTYPE html>
                    <html lang="fa" dir="rtl">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>مدیریت کل - باربرگ بندر</title>
                        <style>
                            body {{ font-family: Tahoma, sans-serif; background: #EDF2F7; margin: 0; padding: 0; direction: rtl; }}
                            .header {{ background: #0277BD; color: white; padding: 15px 25px; display: flex; justify-content: space-between; align-items: center; font-weight: bold; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                            .container {{ padding: 20px; max-width: 700px; margin: auto; }}
                            .card {{ background: white; padding: 22px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 20px; }}
                            input {{ width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 10px; box-sizing: border-box; }}
                            button {{ background: #2E7D32; color: white; border: none; padding: 12px; width: 100%; border-radius: 10px; font-weight: bold; cursor: pointer; }}
                            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }}
                            th, td {{ border: 1px solid #edf2f7; padding: 10px; text-align: center; }}
                            th {{ background: #F7FAFC; color: #4A5568; }}
                            .logout-btn {{ background: #E53E3E; padding: 8px 16px; font-size: 13px; color: white; text-decoration: none; border-radius: 8px; }}
                            .status-box {{ background: {server_badge_color}; color: white; padding: 14px; border-radius: 12px; text-align: center; font-size: 14px; margin-bottom: 20px; font-weight: bold; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
                        </style>
                    </head>
                    <body>
                        <div class="header">
                            <span>مدیر کل سامانه: {username}</span>
                            <a href="/logout" class="logout-btn">خروج</a>
                        </div>
                        <div class="container">
                            <div class="status-box">
                                وضعیت هوشمند سرور: {server_display_name}
                            </div>
                            <div class="card">
                                <h3>مدیریت و تزریق سرورها (۳ سرور فعال)</h3>
                                {servers_html}
                            </div>
                            <div class="card">
                                <h3>فیش‌های واریزی در انتظار تایید</h3>
                                <table>
                                    <tr><th>کاربر</th><th>جزئیات</th><th>عملیات</th></tr>
                                    {receipts_html if receipts_html else '<tr><td colspan="3">فیش در انتظاری وجود ندارد.</td></tr>'}
                                </table>
                            </div>
                            <div class="card">
                                <h3>ساخت پنل هوشمند جدید (اشتراک ۳۰ روزه)</h3>
                                <form method="POST" action="/add_panel">
                                    <input type="text" name="new_user" placeholder="نام کاربری مشتری" required>
                                    <input type="text" name="new_pass" placeholder="رمز عبور مشتری" required>
                                    <input type="number" name="max_plates" placeholder="سقف تعداد پلاک" value="50" required>
                                    <button type="submit">ایجاد پنل تجاری</button>
                                </form>
                            </div>
                            <div class="card">
                                <h3>مدیریت مشتریان و اعتبار</h3>
                                <table>
                                    <tr><th>کاربر</th><th>سقف پلاک</th><th>اعتبار</th><th>عملیات</th></tr>
                                    {customers_html if customers_html else '<tr><td colspan="4">مشتری‌ای ثبت نشده است.</td></tr>'}
                                </table>
                            </div>
                        </div>
                    </body>
                    </html>"""
                else:
                    c.execute("SELECT COUNT(*) FROM drivers WHERE panel_id = ?", (panel_id,))
                    current_plates_count = c.fetchone()[0]

                    c.execute("SELECT id, name, national_id, plate_part1, plate_letter, plate_part2, plate_iran, vehicle_class, max_load_ton, issue_status, transport_status FROM drivers WHERE panel_id = ?", (panel_id,))
                    drivers = c.fetchall()

                    drivers_html = ""
                    for d in drivers:
                        iss_txt = "صدور روشن" if d[9] == 1 else "صدور خاموش"
                        iss_col = "#2E7D32" if d[9] == 1 else "#C62828"
                        trn_txt = "حمل روشن" if d[10] == 1 else "حمل خاموش"
                        trn_col = "#2E7D32" if d[10] == 1 else "#C62828"

                        drivers_html += f"""<tr>
                            <td><b>{d[1]}</b><br><small>{d[2]}</small></td>
                            <td><span style="background:#E3F2FD; padding:4px 8px; border-radius:6px; font-weight:bold;">{d[3]} {d[4]} {d[5]} - {d[6]}</span></td>
                            <td>{d[7]} ({d[8]} ت)</td>
                            <td>
                                <a href='/toggle_issue?id={d[0]}' style='color:white; background:{iss_col}; padding:6px 10px; border-radius:6px; text-decoration:none; font-size:11px; display:inline-block; margin-bottom:4px; font-weight:bold;'>{iss_txt}</a><br>
                                <a href='/toggle_transport?id={d[0]}' style='color:white; background:{trn_col}; padding:6px 10px; border-radius:6px; text-decoration:none; font-size:11px; display:inline-block; font-weight:bold;'>{trn_txt}</a>
                            </td>
                        </tr>"""

                    c.execute("SELECT ip_name, group_assigned, status FROM servers")
                    user_servers = c.fetchall()
                    srv_grid = ""
                    for us in user_servers:
                        srv_grid += f"<div style='background:#1E293B; color:#FFF; padding:10px; border-radius:8px; text-align:center; font-size:12px;'><b>{us[0]}</b><br>{us[1]}</div>"

                    html = f"""<!DOCTYPE html>
                    <html lang="fa" dir="rtl">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>پنل هوشمند اختصاصی - باربرگ بندر</title>
                        <style>
                            body {{ font-family: Tahoma, sans-serif; background: #EDF2F7; margin: 0; padding: 0; direction: rtl; }}
                            .header {{ background: #0277BD; color: white; padding: 15px 25px; display: flex; justify-content: space-between; align-items: center; font-weight: bold; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                            .container {{ padding: 20px; max-width: 700px; margin: auto; }}
                            .card {{ background: white; padding: 22px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 20px; }}
                            input, select {{ width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 10px; box-sizing: border-box; background: #FAFAFA; }}
                            button {{ background: #0277BD; color: white; border: none; padding: 12px; width: 100%; border-radius: 10px; font-weight: bold; cursor: pointer; transition: 0.3s; }}
                            button:hover {{ background: #01579B; }}
                            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }}
                            th, td {{ border: 1px solid #edf2f7; padding: 10px; text-align: center; vertical-align: middle; }}
                            th {{ background: #F7FAFC; color: #4A5568; }}
                            .logout-btn {{ background: #E53E3E; padding: 8px 16px; font-size: 13px; color: white; text-decoration: none; border-radius: 8px; }}
                            .status-box {{ background: {server_badge_color}; color: white; padding: 14px; border-radius: 12px; text-align: center; font-size: 14px; margin-bottom: 20px; font-weight: bold; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
                            .card-box {{ background: #0F172A; color: #FFF; padding: 18px; border-radius: 12px; text-align: center; margin-bottom: 15px; }}
                        </style>
                    </head>
                    <body>
                        <div class="header">
                            <span>کاربر: {username} | اعتبار: {days_left} روز</span>
                            <a href="/logout" class="logout-btn">خروج</a>
                        </div>
                        <div class="container">
                            <div class="status-box">
                                وضعیت سرور هوشمند: {server_display_name}
                            </div>

                            <div class="card">
                                <h3>وضعیت سرورهای فعال اختصاصی</h3>
                                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 10px;">
                                    {srv_grid}
                                </div>
                            </div>

                            <div class="card">
                                <h3>انتخاب نقشه زنده (مپ سریع OSM / سناتور / آفلاین)</h3>
                                <select name="map_type">
                                    <option value="osm">نقشه سریع OSM (پیش‌فرض)</option>
                                    <option value="senator_fast">نقشه سریع سناتور</option>
                                    <option value="offline_hybrid">نقشه هوشمند ترکیبی / آفلاین</option>
                                </select>
                            </div>

                            <div class="card">
                                <h3>ثبت راننده و تعیین کلاس تناژ ({current_plates_count}/{max_plates})</h3>
                                <form method="POST" action="/add_driver">
                                    <input type="text" name="name" placeholder="نام و نام خانوادگی راننده" required>
                                    <input type="text" name="nid" placeholder="کد ملی" required>
                                    <div style="display: flex; gap: 8px;">
                                        <input type="text" name="p2" placeholder="سه‌رقم پلاک" required>
                                        <input type="text" name="let" value="ع" placeholder="حرف" required>
                                        <input type="text" name="p1" placeholder="دورقم پلاک" required>
                                        <input type="text" name="iran" value="۸۴" placeholder="ایران" required>
                                    </div>
                                    <select name="vehicle_class">
                                        <option value="3.5ton">کلاس ۳.۵ تن (ظرفیت هوشمند: حداکثر ۲ تن)</option>
                                        <option value="6ton">کلاس ۶ تن (ظرفیت هوشمند: حداکثر ۳.۵ تن)</option>
                                        <option value="19ton">کلاس ۱۹ تن (ظرفیت هوشمند: حداکثر ۱۰ تن)</option>
                                        <option value="26ton">کلاس ۲۶ تن (ظرفیت هوشمند: ۱۵ الی ۱۶ تن)</option>
                                        <option value="40ton">کلاس ۴۰ و ۴۲ تن (ظرفیت هوشمند: ۲۰ تن)</option>
                                    </select>
                                    <button type="submit">ثبت راننده جدید</button>
                                </form>
                            </div>

                            <div class="card">
                                <h3>صدور هوشمند باربرگ (سقف زیر ۲۰۰ میلیون ریال)</h3>
                                <form method="POST" action="/issue_barbarg">
                                    <select name="cargo_type">
                                        <option value="سیمان">سیمان / گچ (محاسبه ریالی هوشمند)</option>
                                        <option value="تره بار">تره بار و مواد غذایی</option>
                                        <option value="تیرچه چوب">تیرچه، بلوک و چوب</option>
                                    </select>
                                    <input type="number" name="custom_price" placeholder="مبلغ کرایه ریالی (اختیاری)">
                                    <button type="submit" style="background: #2E7D32;">صدور باربرگ با گیرنده تصادفی</button>
                                </form>
                            </div>

                            <div class="card">
                                <h3>مدیریت وضعیت صدور و حمل رانندگان</h3>
                                <table>
                                    <tr><th>راننده</th><th>پلاک</th><th>تناژ</th><th>عملیات</th></tr>
                                    {drivers_html if drivers_html else '<tr><td colspan="4">راننده‌ای ثبت نشده است.</td></tr>'}
                                </table>
                            </div>

                            <div class="card">
                                <h3>تمدید اشتراک و اطلاعات واریز</h3>
                                <div class="card-box">
                                    <div style="color: #94A3B8; font-size: 13px;">شماره کارت:</div>
                                    <div style="font-size: 18px; color: #38BDF8; direction: ltr; margin: 4px 0; font-weight: bold;">6219 8619 8658 9132</div>
                                    <div style="color: #94A3B8; font-size: 13px;">شماره شبا:</div>
                                    <div style="font-size: 12px; color: #4ADE80; direction: ltr; word-break: break-all;">IR530560611828005783056501</div>
                                </div>
                                <form method="POST" action="/submit_receipt">
                                    <input type="text" name="tracking_code" placeholder="شماره پیگیری یا ۴ رقم آخر کارت" required>
                                    <input type="number" name="amount" placeholder="مبلغ واریزی (ریال)" required>
                                    <button type="submit" style="background: #0277BD;">ارسال فیش واریزی</button>
                                </form>
                            </div>
                        </div>
                    </body>
                    </html>"""
            
            self.wfile.write(html.encode("utf-8"))

        elif path.startswith("/delete_panel"):
            qp = urllib.parse.parse_qs(parsed_path.query)
            p_id = qp.get("id", [None])[0]
            if p_id:
                c = db_conn.cursor()
                c.execute("DELETE FROM panels WHERE id = ? AND is_admin = 0", (p_id,))
                c.execute("DELETE FROM drivers WHERE panel_id = ?", (p_id,))
                db_conn.commit()
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()

        elif path.startswith("/renew_panel"):
            qp = urllib.parse.parse_qs(parsed_path.query)
            p_id = qp.get("id", [None])[0]
            if p_id:
                c = db_conn.cursor()
                c.execute("SELECT expire_date FROM panels WHERE id = ?", (p_id,))
                row = c.fetchone()
                if row:
                    try:
                        base_date = max(datetime.strptime(row[0], '%Y-%m-%d'), datetime.now())
                    except:
                        base_date = datetime.now()
                    new_exp = (base_date + timedelta(days=30)).strftime('%Y-%m-%d')
                    c.execute("UPDATE panels SET expire_date = ? WHERE id = ?", (new_exp, p_id))
                    db_conn.commit()
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()

        elif path.startswith("/approve_receipt"):
            qp = urllib.parse.parse_qs(parsed_path.query)
            rec_id = qp.get("id", [None])[0]
            if rec_id:
                c = db_conn.cursor()
                c.execute("SELECT panel_id FROM receipts WHERE id = ?", (rec_id,))
                r_data = c.fetchone()
                if r_data:
                    p_id = r_data[0]
                    c.execute("SELECT expire_date FROM panels WHERE id = ?", (p_id,))
                    p_data = c.fetchone()
                    if p_data:
                        try:
                            base_date = max(datetime.strptime(p_data[0], '%Y-%m-%d'), datetime.now())
                        except:
                            base_date = datetime.now()
                        new_exp = (base_date + timedelta(days=30)).strftime('%Y-%m-%d')
                        c.execute("UPDATE panels SET expire_date = ? WHERE id = ?", (new_exp, p_id))
                    c.execute("UPDATE receipts SET status = 'approved' WHERE id = ?", (rec_id,))
                    db_conn.commit()
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()

        elif path.startswith("/toggle_issue"):
            qp = urllib.parse.parse_qs(parsed_path.query)
            d_id = qp.get("id", [None])[0]
            if d_id:
                c = db_conn.cursor()
                c.execute("SELECT issue_status FROM drivers WHERE id = ?", (d_id,))
                row = c.fetchone()
                if row:
                    new_st = 0 if row[0] == 1 else 1
                    c.execute("UPDATE drivers SET issue_status = ? WHERE id = ?", (new_st, d_id))
                    db_conn.commit()
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()

        elif path.startswith("/toggle_transport"):
            qp = urllib.parse.parse_qs(parsed_path.query)
            d_id = qp.get("id", [None])[0]
            if d_id:
                c = db_conn.cursor()
                c.execute("SELECT transport_status FROM drivers WHERE id = ?", (d_id,))
                row = c.fetchone()
                if row:
                    new_st = 0 if row[0] == 1 else 1
                    c.execute("UPDATE drivers SET transport_status = ? WHERE id = ?", (new_st, d_id))
                    db_conn.commit()
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = urllib.parse.parse_qs(post_data)

        if self.path == "/login":
            username = params.get('username', [''])[0]
            password = params.get('password', [''])[0]

            c = db_conn.cursor()
            c.execute("SELECT * FROM panels WHERE username = ? AND password = ? AND is_active = 1", (username, password))
            user = c.fetchone()

            if user:
                self.send_response(303)
                self.send_header('Location', '/')
                self.send_header('Set-Cookie', f'session={username}; Path=/')
                self.end_headers()
            else:
                self.send_response(303)
                self.send_header('Location', '/')
                self.end_headers()

        elif self.path == "/add_panel":
            new_user = params.get('new_user', [''])[0]
            new_pass = params.get('new_pass', [''])[0]
            max_plates = params.get('max_plates', ['50'])[0]
            expire_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            if new_user and new_pass:
                try:
                    c = db_conn.cursor()
                    c.execute("INSERT INTO panels (username, password, max_plates, is_admin, is_active, expire_date) VALUES (?, ?, ?, 0, 1, ?)", 
                              (new_user, new_pass, int(max_plates), expire_date))
                    db_conn.commit()
                except Exception as e:
                    print("Error:", e)
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()

        elif self.path == "/submit_receipt":
            cookie = http.cookies.SimpleCookie(self.headers.get('Cookie'))
            username = cookie.get('session').value if 'session' in cookie else None
            if username:
                c = db_conn.cursor()
                c.execute("SELECT id FROM panels WHERE username = ?", (username,))
                p = c.fetchone()
                if p:
                    c.execute("INSERT INTO receipts (panel_id, username, tracking_code, amount, status) VALUES (?, ?, ?, ?, 'pending')",
                              (p[0], username, params.get('tracking_code', [''])[0], params.get('amount', [''])[0]))
                    db_conn.commit()
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()

        elif self.path == "/add_driver":
            cookie = http.cookies.SimpleCookie(self.headers.get('Cookie'))
            username = cookie.get('session').value if 'session' in cookie else None
            if username:
                c = db_conn.cursor()
                c.execute("SELECT id, max_plates FROM panels WHERE username = ?", (username,))
                panel = c.fetchone()
                if panel:
                    panel_id, max_plates = panel
                    c.execute("SELECT COUNT(*) FROM drivers WHERE panel_id = ?", (panel_id,))
                    if c.fetchone()[0] < max_plates:
                        name = params.get('name', [''])[0]
                        nid = params.get('nid', [''])[0]
                        p2 = params.get('p2', [''])[0]
                        let = params.get('let', [''])[0]
                        p1 = params.get('p1', [''])[0]
                        iran = params.get('iran', [''])[0]
                        v_class = params.get('vehicle_class', ['3.5ton'])[0]
                        
                        load_map = {"3.5ton": 2.0, "6ton": 3.5, "19ton": 10.0, "26ton": 15.5, "40ton": 20.0}
                        c.execute("INSERT INTO drivers (panel_id, name, national_id, plate_part1, plate_letter, plate_part2, plate_iran, vehicle_class, max_load_ton, issue_status, transport_status, group_num) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1, 1)",
                                  (panel_id, name, nid, p1, let, p2, iran, v_class, load_map.get(v_class, 2.0)))
                        db_conn.commit()
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()

        elif self.path == "/issue_barbarg":
            cargo = params.get('cargo_type', ['سیمان'])[0]
            custom_price = params.get('custom_price', [''])[0]
            price_rial = int(custom_price) if custom_price.isdigit() else random.randint(45000000, 185000000)
            rec_name, rec_phone = generate_random_receiver()
            print(f"[AI Barbarg] بار: {cargo} | کرایه: {price_rial:,} ریال | گیرنده: {rec_name} ({rec_phone})")
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()

def run():
    server_address = ('', PORT)
    httpd = http.server.HTTPServer(server_address, BarbargHandler)
    print(f"سرور تجاری و پیشرفته روی پورت {PORT} روشن شد...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
