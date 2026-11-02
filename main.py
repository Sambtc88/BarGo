import http.server
import socketserver
import sqlite3
import urllib.parse

PORT = 2727

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
                    is_active INTEGER DEFAULT 1,
                    history TEXT DEFAULT '✓,✓,✓,✓,✓,✓,✗,✓'
                )''')
    c.execute("INSERT OR IGNORE INTO panels (username, password, max_plates, is_admin, is_active) VALUES ('admin', 'admin123', 200, 1, 1)")
    conn.commit()
    return conn

db_conn = init_db()

HTML_PAGE = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>پنل ثبت باربرگ بندر</title>
    <style>
        body { font-family: Tahoma, sans-serif; background: #F2F5F8; margin: 0; padding: 0; direction: rtl; }
        .header { background: #0277BD; color: white; padding: 15px; text-align: center; font-size: 18px; font-weight: bold; }
        .container { padding: 15px; max-width: 500px; margin: auto; }
        .card { background: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 15px; }
        input, select { width: 100%; padding: 10px; margin: 8px 0; border: 1px solid #ccc; border-radius: 8px; box-sizing: border-box; }
        button { background: #0277BD; color: white; border: none; padding: 12px; width: 100%; border-radius: 8px; font-weight: bold; cursor: pointer; }
        button:hover { background: #01579B; }
    </style>
</head>
<body>
    <div class="header">پنل ثبت باربرگ بندر</div>
    <div class="container">
        <div class="card">
            <h3>مدیریت و صدور باربرگ</h3>
            <p>سیستم مدیریت پنل‌ها و پلاک‌ها فعال است.</p>
            <hr>
            <h4>افزودن پلاک جدید</h4>
            <input type="text" id="name" placeholder="نام و نام خانوادگی راننده">
            <input type="text" id="nid" placeholder="کد ملی">
            <div style="display: flex; gap: 5px;">
                <input type="text" id="p2" placeholder="سه‌رقم">
                <input type="text" id="let" value="ع" placeholder="حرف">
                <input type="text" id="p1" placeholder="دورقم">
                <input type="text" id="iran" value="۸۴" placeholder="ایران">
            </div>
            <button onclick="alert('پلاک با موفقیت در صف گروه ثبت شد!')">ثبت و افزودن به گروه</button>
        </div>
        <div class="card">
            <h3>وضعیت گروه‌ها و سرور موبایل</h3>
            <button style="background: #2E7D32; margin-bottom: 8px;" onclick="alert('ربات صدور باربرگ گروه ۱ روی سرور سامانه آغاز شد.')">شروع عملیات گروه ۱ (سرور سامانه)</button>
            <button style="background: #E65100;" onclick="alert('ربات روی تانل آنتن موبایل سوییچ شد!')">سوییچ به سرور آنتن موبایل (سیم‌کارت)</button>
        </div>
    </div>
</body>
</html>
"""

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode("utf-8"))

def run():
    server_address = ('', PORT)
    httpd = http.server.HTTPServer(server_address, MyHandler)
    print(f"سرور روی پورت {PORT} روشن شد...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
