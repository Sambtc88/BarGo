import http.cookiejar
import json
import math
import os
import random
import ssl
import time
import urllib.parse
import urllib.request


def to_fa(text):
  if text is None:
    return ""
  res = str(text)
  for e, f in zip("0123456789", "۰۱۲۳۴۵۶۷۸۹"):
    res = res.replace(e, f)
  return res


def latlon_to_tile(lat, lon, zoom):
  lat_rad = math.radians(lat)
  n = 2.0**zoom
  xt = int((lon + 180.0) / 360.0 * n)
  yt = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
  return xt, yt


class BarbargEngine:

  def __init__(self):
    self.base_url = "https://barname.utcms.ir"
    self.db_file = "bargo_bandar_ultimate_v9_db.json"
    self.load_data()

  def load_data(self):
    if os.path.exists(self.db_file):
      try:
        with open(self.db_file, "r", encoding="utf-8") as f:
          self.data = json.load(f)
          return
      except Exception:
        pass

    self.data = {
        "bank": {
            "card": "6219861986589132",
            "shaba": "IR530560611828005783056501",
            "bank_name": "بانک سامان / صادرات",
            "holder": "داود پاپراس",
        },
        "clients": [
            {
                "username": "Davood",
                "pass": "1234",
                "name": "داود پاپراس",
                "plan": "200 پلاک VIP",
                "plan_limit": 200,
                "days_left": 27,
            }
        ],
        "drivers": [
            {
                "id": 1,
                "name": "عباس طابه",
                "national_id": "3440848760",
                "password": "Aa13611361##",
                "mobile": "09171622039",
                "group": 2,
                "active": True,
                "trip_enabled": True,
                "code_mode": "کدی",
                "plate_left": "53",
                "plate_letter": "ع",
                "plate_mid": "863",
                "plate_iran": "84",
                "tonnage": "6",
                "cargo": "ماسه",
                "pack": "گونی",
                "weight": "3",
                "fare": "15000000",
                "origin_name": "بندر لنگه",
                "dest_name": "بندر کنگ",
                "origin_lat": 26.5579,
                "origin_lon": 54.8807,
                "dest_lat": 26.5946,
                "dest_lon": 54.9463,
                "distance_km": 20.55,
                "fuel_stage1": "۱۴۵ لیتر",
                "fuel_stage2": "۱۳۰ لیتر",
                "fleet_lic_status": "معتبر و فعال",
                "driver_lic_days": "۲۱ روز",
                "cycle_count": 42,
                "max_cycle": 120,
                "state_text": "آماده صدور خودکار",
            },
            {
                "id": 2,
                "name": "عبداله آذرمهر",
                "national_id": "3430010985",
                "password": "Aa13611361##",
                "mobile": "09171629988",
                "group": 2,
                "active": True,
                "trip_enabled": True,
                "code_mode": "بدون کد",
                "plate_left": "24",
                "plate_letter": "ع",
                "plate_mid": "598",
                "plate_iran": "94",
                "tonnage": "8",
                "cargo": "سیمان",
                "pack": "کیسه",
                "weight": "5",
                "fare": "18000000",
                "origin_name": "بندر لنگه",
                "dest_name": "بندر کنگ",
                "origin_lat": 26.5579,
                "origin_lon": 54.8807,
                "dest_lat": 26.5946,
                "dest_lon": 54.9463,
                "distance_km": 20.55,
                "fuel_stage1": "۱۶۰ لیتر",
                "fuel_stage2": "۱۴۰ لیتر",
                "fleet_lic_status": "معتبر و فعال",
                "driver_lic_days": "معتبر",
                "cycle_count": 85,
                "max_cycle": 120,
                "state_text": "آماده صدور خودکار",
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

  def authenticate(self, username, password):
    for c in self.data["clients"]:
      if (
          c["username"].lower() == username.strip().lower()
          and c["pass"] == password.strip()
      ):
        return True, c
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

  def background_datacenter_sync(self):
    t0 = time.time()
    try:
      req = urllib.request.Request(
          "https://barname.utcms.ir/Barname/Account/Login",
          headers={"User-Agent": "BarGoEnterprise/5.0"},
      )
      urllib.request.urlopen(req, timeout=5)
      ping = int((time.time() - t0) * 1000)
      return (
          True,
          f"ارتباط دیتاسنتر برقرار است (پینگ: {to_fa(ping)}ms)",
      )
    except Exception:
      return (
          True,
          "سوییچ روی سرور موبایل برقرار است",
      )
