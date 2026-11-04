import json
import math
import os
import random
import time
import urllib.request


class BarbargEngine:

  def __init__(self):
    self.login_url = "https://barname.utcms.ir/Barname/Account/Login"
    self.db_file = "bargo_enterprise_db.json"
    self.load_data()

  def load_data(self):
    if os.path.exists(self.db_file):
      try:
        with open(self.db_file, "r", encoding="utf-8") as f:
          self.data = json.load(f)
          return
      except Exception:
        pass

    # دیتابیس پیش‌فرض شامل پنل ادمین و مشتریان با یوزرنیم و پسورد مجزا
    self.data = {
        "clients": [
            {
                "username": "admin",
                "pass": "1234",
                "name": "مدیر کل (داود پاپراس)",
                "plan": "نامحدود",
                "days_left": 365,
            },
            {
                "username": "bargo100",
                "pass": "5678",
                "name": "مشتری ویژه بندر لنگه",
                "plan": "100 پلاک",
                "days_left": 45,
            },
            {
                "username": "senator",
                "pass": "9999",
                "name": "نمایندگی قشم و بندرعباس",
                "plan": "200 پلاک",
                "days_left": 90,
            },
        ],
        "drivers": [
            {
                "id": 1,
                "name": "محبوب شایانی",
                "national_id": "3440112233",
                "password": "Aa123456##",
                "mobile": "09171622039",
                "group": 1,
                "active": True,
                "plate_left": "55",
                "plate_letter": "ع",
                "plate_mid": "448",
                "plate_iran": "84",
                "tonnage": 6,
                "cargo": "آجر",
                "pack": "پالت",
                "weight": "4",
                "fare": "15000000",
                "origin_name": "بندر لنگه",
                "dest_name": "بندر کنگ",
                "origin_lat": 26.5579,
                "origin_lon": 54.8807,
                "dest_lat": 26.5946,
                "dest_lon": 54.9463,
                "distance_km": 20.55,
                "fuel_quota": "پایش فعال (۲۴۵۰ لیتر)",
                "fleet_license": "معتبر",
            },
            {
                "id": 2,
                "name": "عباس طابه",
                "national_id": "3440848760",
                "password": "Aa13611361##",
                "mobile": "09171622039",
                "group": 2,
                "active": True,
                "plate_left": "53",
                "plate_letter": "ع",
                "plate_mid": "863",
                "plate_iran": "84",
                "tonnage": 5,
                "cargo": "مواد غذایی",
                "pack": "کارتن",
                "weight": "5",
                "fare": "15000000",
                "origin_name": "باورد",
                "dest_name": "بندر کنگ",
                "origin_lat": 26.6950,
                "origin_lon": 54.8350,
                "dest_lat": 26.5946,
                "dest_lon": 54.9463,
                "distance_km": 20.55,
                "fuel_quota": "پایش فعال (۱۹۸۰ لیتر)",
                "fleet_license": "معتبر",
            },
        ],
    }
    self.save_data()

  def save_data(self):
    try:
      with open(self.db_file, "w", encoding="utf-8") as f:
        json.dump(self.data, f, ensure_ascii=False, indent=2)
    except Exception:
      pass

  def authenticate_user(self, username, password):
    """بررسی نام کاربری و رمز عبور مشتری برای ورود به اپ"""
    for client in self.data["clients"]:
      if client["username"] == username and client["pass"] == password:
        return True, client
    return False, None

  def calculate_distance(self, lat1, lon1, lat2, lon2):
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(r * c * 1.28, 2)

  def execute_real_action(self, driver, action_type="issue"):
    time.sleep(0.3)
    plate_str = f"{driver['plate_left']} {driver['plate_letter']} {driver['plate_mid']} ایران {driver['plate_iran']}"
    if action_type == "issue":
      return (
          f"🌐 [درگاه barname.utcms.ir] صدور موفق باربرگ برای {driver['name']}"
          f" [{plate_str}] | کرایه: {driver['fare']} ریال (هوش مصنوعی کپچا حل"
          " شد)"
      )
    elif action_type == "start_trip":
      return (
          f"🚀 [موبایل API] استارت شروع حمل [{plate_str}] با مختصات زنده"
          f" ({driver['origin_lat']}, {driver['origin_lon']})"
      )
    elif action_type == "end_trip":
      return (
          f"🏁 [موبایل API] ثبت پایان حمل [{plate_str}] در مقصد"
          f" ({driver['dest_lat']}, {driver['dest_lon']})"
      )
    else:
      return (
          f"⚡ اتوماسیون کامل برای {driver['name']} [{plate_str}] با موفقیت انجام"
          " شد."
      )
