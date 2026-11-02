import http.server
import sqlite3
import urllib.parse
import http.cookies

PORT = 2727

# راه‌اندازی پایگاه داده با نام کاربری و رمز عبور دلخواه شما
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
                    plate_part1 TEXT,
                    plate_letter TEXT,
                    plate_part2 TEXT,
                    plate_iran TEXT,
                    group_num INTEGER DEFAULT 1,
                    is_active INTEGER DEFAULT 1
                )''')
    # ثبت نام کاربری DAVOOD و رمز عبور Dp9498Dp
    c.execute("INSERT OR IGNORE INTO panels (username, password, max_plates, is_admin, is_active) VALUES ('DAVOOD', 'Dp9498Dp', 200, 1, 1)")
    conn.commit()
    return conn

db_conn = init_db()

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
                    <title>ورود - باربرگ بندر</title>
                    <style>
                        body { font-family: Tahoma, sans-serif; background: #0277BD; margin: 0; display: flex; align-items: center; justify-content: center; height: 100vh; direction: rtl; }
                        .login-card { background: white; padding: 25px; border-radius: 12px; width: 320px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); margin: auto; }
                        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ccc; border-radius: 8px; box-sizing: border-box; }
                        button { background: #0277BD; color: white; border: none; padding: 12px; width: 100%; border-radius: 8px; font-weight: bold; cursor: pointer; }
                        button:hover { background: #01579B; }
                        h2 { text-align: center; color: #0277BD; margin-bottom: 20px; }
                    </style>
                </head>
                <body>
                    <div class="login-card">
                        <h2>ورود به باربرگ بندر</h2>
                        <form method="POST" action="/login">
                            <input type="text" name="username" placeholder="نام کاربری" required>
                            <input type="password" name="password" placeholder="رمز عبور" required>
                            <button type="submit">ورود به پنل</button>
                        </form>
                    </div>
                </body>
                </html>"""
            else:
                c = db_conn.cursor()
                c.execute("SELECT id, max_plates, is_admin FROM panels WHERE username = ?", (username,))
                panel_data = c.fetchone()
                panel_id, max_plates, is_admin = panel_data

                c.execute("SELECT COUNT(*) FROM drivers WHERE panel_id = ?", (panel_id,))
                current_plates_count = c.fetchone()[0]

                c.execute("SELECT name, national_id, plate_part1, plate_letter, plate_part2, plate_iran, group_num FROM drivers WHERE panel_id = ?", (panel_id,))
                drivers = c.fetchall()

                drivers_html = ""
                for d in drivers:
                    drivers_html += f"<tr><td>{d[0]}</td><td>{d[1]}</td><td>{d[2]} {d[3]} {d[4]} - ایران {d[5]}</td><td>گروه {d[6]}</td></tr>"

                html = f"""<!DOCTYPE html>
                <html lang="fa" dir="rtl">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>پنل مدیریت - باربرگ بندر</title>
                    <style>
                        body {{ font-family: Tahoma, sans-serif; background: #F2F5F8; margin: 0; padding: 0; direction: rtl; }}
                        .header {{ background: #0277BD; color: white; padding: 15px; display: flex; justify-content: space-between; align-items: center; font-weight: bold; }}
                        .container {{ padding: 15px; max-width: 600px; margin: auto; }}
                        .card {{ background: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 15px; }}
                        input, select {{ width: 100%; padding: 10px; margin: 8px 0; border: 1px solid #ccc; border-radius: 8px; box-sizing: border-box; }}
                        button {{ background: #0277BD; color: white; border: none; padding: 12px; width: 100%; border-radius: 8px; font-weight: bold; cursor: pointer; }}
                        button:hover {{ background: #01579B; }}
                        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
                        th {{ background: #f0f0f0; }}
                        .logout-btn {{ background: #D32F2F; width: auto; padding: 6px 12px; font-size: 12px; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <span>خوش آمدید، {username} (سقف پلاک: {current_plates_count}/{max_plates})</span>
                        <a href="/logout"><button class="logout-btn">خروج</button></a>
                    </div>
                    <div class="container">
                        <div class="card">
                            <h3>ثبت پلاک و راننده جدید</h3>
                            <form method="POST" action="/add_driver">
                                <input type="text" name="name" placeholder="نام و نام خانوادگی راننده" required>
                                <input type="text" name="nid" placeholder="کد ملی" required>
                                <div style="display: flex; gap: 5px;">
                                    <input type="text" name="p2" placeholder="سه‌رقم (مثل ۴۴۸)" required>
                                    <input type="text" name="let" value="ع" placeholder="حرف" required>
                                    <input type="text" name="p1" placeholder="دورقم (مثل ۵۵)" required>
                                    <input type="text" name="iran" value="۸۴" placeholder="ایران" required>
                                </div>
                                <select name="group_num">
                                    <option value="1">گروه ۱</option>
                                    <option value="2">گروه ۲</option>
                                    <option value="3">گروه ۳</option>
                                </select>
                                <button type="submit">ثبت پلاک در سامانه</button>
                            </form>
                        </div>

                        <div class="card">
                            <h3>سوییچ سرور و وضعیت ربات</h3>
                            <button style="background: #2E7D32; margin-bottom: 8px;" onclick="alert('عملیات روی سرور اصلی سامانه درون‌شهری آغاز شد.')">شروع عملیات (سرور سامانه درون‌شهری)</button>
                            <button style="background: #E65100;" onclick="alert('ارتباط روی سرور آنتن موبایل (سیم‌کارت) سوییچ شد!')">سوییچ به سرور آنتن موبایل (موبایل هات‌اسپات)</button>
                        </div>

                        <div class="card">
                            <h3>لیست پلاک‌های ثبت شده شما</h3>
                            <table>
                                <tr><th>نام راننده</th><th>کد ملی</th><th>پلاک</th><th>گروه</th></tr>
                                {drivers_html if drivers_html else '<tr><td colspan="4">هنوز پلاک ثبت نشده است.</td></tr>'}
                            </table>
                        </div>
                    </div>
                </body>
                </html>"""
            
            self.wfile.write(html.encode("utf-8"))

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

        elif self.path == "/add_driver":
            cookie = http.cookies.SimpleCookie(self.headers.get('Cookie'))
            username = cookie.get('session').value if 'session' in cookie else None

            if username:
                c = db_conn.cursor()
                c.execute("SELECT id, max_plates FROM panels WHERE username = ?", (username,))
                panel = c.fetchone()
                panel_id, max_plates = panel

                c.execute("SELECT COUNT(*) FROM drivers WHERE panel_id = ?", (panel_id,))
                count = c.fetchone()[0]

                if count < max_plates:
                    name = params.get('name', [''])[0]
                    nid = params.get('nid', [''])[0]
                    p2 = params.get('p2', [''])[0]
                    let = params.get('let', [''])[0]
                    p1 = params.get('p1', [''])[0]
                    iran = params.get('iran', [''])[0]
                    group_num = params.get('group_num', ['1'])[0]

                    c.execute("INSERT INTO drivers (panel_id, name, national_id, plate_part1, plate_letter, plate_part2, plate_iran, group_num) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                              (panel_id, name, nid, p1, let, p2, iran, group_num))
                    db_conn.commit()

            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()

def run():
    server_address = ('', PORT)
    httpd = http.server.HTTPServer(server_address, BarbargHandler)
    print(f"سرور روی پورت {PORT} روشن شد...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
