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
                html = """<!DOCTYPE html>
                <html lang="fa" dir="rtl">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>ورود - سامانه هوشمند بارگوبندر</title>
                    <style>
                        body { font-family: Tahoma, Arial, sans-serif; background: linear-gradient(135deg, #0B132B 0%, #1C2541 50%, #28385E 100%); margin: 0; display: flex; align-items: center; justify-content: center; min-height: 100vh; direction: rtl; }
                        .login-container { width: 100%; max-width: 400px; padding: 20px; box-sizing: border-box; text-align: center; }
                        .logo-box { margin-bottom: 20px; }
                        .truck-icon { width: 90px; height: 65px; background: linear-gradient(135deg, #00B4D8, #0077B6); border-radius: 14px; display: inline-flex; align-items: center; justify-content: center; box-shadow: 0 10px 25px rgba(0,180,216,0.4); margin-bottom: 12px; }
                        .truck-icon svg { width: 50px; height: 50px; fill: #ffffff; }
                        .brand-en { font-size: 26px; font-weight: 800; letter-spacing: 1px; color: #00B4D8; margin: 0; text-transform: uppercase; }
                        .brand-fa { font-size: 20px; font-weight: bold; color: #F1F5F9; margin-top: 5px; margin-bottom: 25px; }
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
            else
