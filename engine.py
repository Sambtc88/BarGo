import json
import math
import os
import random
import re
import time
import urllib.parse
import urllib.request
import httpx


class BarbargEngine:

  def __init__(self):
    self.login_url = "https://barname.utcms.ir/Barname/Account/Login"
    self.base_url = "https://barname.utcms.ir"
    self.db_file = "bargo_bandar_pro_db.json"
    self.sessions = {}
    self.group_running = {"1": True, "2": True}
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
        "clients": [
            {
                "username": "Davood",
                "pass": "1234",
                "name": "داود پاپراس",
                "limit": 50,
                "days_left": 27,
                "role": "admin",
            },
            {
                "username": "admin",
                "pass": "1234",
                "name": "مدیر ارشد بارگو بندر",
                "limit": 200,
                "days_left": 365,
                "role": "admin",
            },
            {
                "username": "bargo100",
                "pass": "5678",
                "name": "مشتری پنل ۱۰۰ تایی",
                "limit": 100,
                "days_left": 30,
                "role": "client",
            },
        ],
        "group_settings": {
            "1": {
                "rounds": "2000",
                "interval": "0.40",
                "round_time": "40",
                "max_login_5min": False,
                "auto_start": False,
                "otp_stop": True,
                "sort_mode": "خودکار (پیش‌فرض)",
                "server_mode": "سرور موبایل (پیش‌فرض)",
            },
            "2": {
                "rounds": "1000",
                "interval": "1",
                "round_time": "5",
                "max_login_5min": True,
                "auto_start": False,
                "otp_stop": True,
                "sort_mode": "خودکار (پیش‌فرض)",
                "server_mode": "سرور موبایل (پیش‌فرض)",
            },
        },
        "cargo_bank": [
            {
                "name": "ماسه",
                "tonnage": "3",
                "pack": "فله",
                "fare": "15000000",
                "val": "25000000",
            },
            {
                "name": "گچ",
                "tonnage": "4",
                "pack": "کیسه",
                "fare": "20000000",
                "val": "40000000",
            },
            {
                "name": "سیمان",
                "tonnage": "6",
                "pack": "کیسه",
                "fare": "25000000",
                "val": "65000000",
            },
            {
                "name": "مواد معدنی",
                "tonnage": "12",
                "pack": "فله",
                "fare": "45000000",
                "val": "80000000",
            },
            {
                "name": "تره بار",
                "tonnage": "3",
                "pack": "گونی",
                "fare": "30000000",
                "val": "90000000",
            },
            {
                "name": "بلوک",
                "tonnage": "5",
                "pack": "پالت",
                "fare": "18000000",
                "val": "45000000",
            },
            {
                "name": "مواد دریایی",
                "tonnage": "4",
                "pack": "جعبه",
                "fare": "35000000",
                "val": "150000000",
            },
            {
                "name": "آجر",
                "tonnage": "5",
                "pack": "پالت",
                "fare": "16000000",
                "val": "50000000",
            },
        ],
        "parties_bank": [
            {"sender": "عبدالقادر بخشنده", "receiver": "صدیق محمدیان"},
            {"sender": "الیاس احمد پور", "receiver": "فیصل زارعی"},
            {"sender": "عبداله قشمی زاده", "receiver": "اسماعیل بقائی"},
            {"sender": "صالح محمودی", "receiver": "مسلم ساربانی"},
            {"sender": "سلیمان کرم زاده", "receiver": "محسن جعفرپور"},
            {"sender": "صدیق زارعی", "receiver": "عبداله بهمنی"},
            {"sender": "هاشم بحری پور", "receiver": "احمد جلالی"},
            {"sender": "ولید نوری", "receiver": "سینا صادقی فر"},
            {"sender": "علیرضا عبدالهی", "receiver": "ابراهیم دهقان"},
            {"sender": "عبداله هاشمی", "receiver": "بهروز علی نژاد"},
        ],
        "history_logs": [
            {
                "time": "14:23:21",
                "driver": "محمد پورپاک",
                "plate": "61 ع 926 ایران 84",
                "status": "موفق",
                "msg": "صدور با موفقیت انجام شد و باربرگ در حال حمل است",
            },
            {
                "time": "13:17:50",
                "driver": "عباس طابه",
                "plate": "53 ع 863 ایران 84",
                "status": "خطا",
                "msg": "Driver's previous shipment not ended",
            },
            {
                "time": "12:35:07",
                "driver": "عیسی محمدزاده",
                "plate": "64 ع 525 ایران 84",
                "status": "خطا",
                "msg": "پایان حمل ناموفق بود: خطای نامشخص",
            },
        ],
        "drivers": [
            {
                "id": 1,
                "name": "عباس طابه",
                "sender_first": "عباس",
                "sender_last": "طابه",
                "receiver_first": "علی",
                "receiver_last": "نجفی",
                "national_id": "3440848760",
                "login_nid": "3440848760",
                "password": "Aa13611361##",
                "mobile": "09171622039",
                "receiver_mobile": "09121480574",
                "referrer": "",
                "group": 2,
                "active": True,
                "plate_left": "53",
                "plate_letter": "ع",
                "plate_mid": "863",
                "plate_iran": "84",
                "tonnage": 3,
                "cargo": "ماسه",
                "pack": "فله",
                "weight": "3",
                "count": "1",
                "value": "25000000",
                "fare": "15000000",
                "post_fare": "15000000",
                "origin_name": "بندر کنگ",
                "dest_name": "بندر لنگه",
                "origin_city": "بندر لنگه",
                "dest_city": "بندر لنگه",
                "origin_neighborhood": "بندر کنگ",
                "dest_neighborhood": "مهرگان پایین",
                "origin_addr": (
                    "ایران، هرمزگان، شهر بندر لنگه، دهستان حومه بندر لنگه،"
                    " بندر کنگ"
                ),
                "dest_addr": (
                    "ایران، هرمزگان، شهر بندر لنگه، دهستان حومه بندر لنگه،"
                    " بندر لنگه، اسکله مهرگان"
                ),
                "origin_lat": 26.5945625,
                "origin_lon": 54.9463615,
                "dest_lat": 26.5579125,
                "dest_lon": 54.8807159,
                "distance_km": 20.55,
                "map_layer": "OSM سریع",
                "issue_enabled": True,
                "trip_enabled": True,
                "platform": "گوشی",
                "otp_mode": "بدون کد",
                "run_state": "در صف صدور",
                "ok_count": 4,
                "err_count": 1,
                "last_errors": [
                    "13:17:50 - Driver's previous shipment not ended"
                ],
                "fleet_license": "-",
                "driver_license_num": "2129415588763",
                "driver_license_status": "21 روز",
                "license_state": "انجام شد",
                "owner_name": "عباس طابه",
                "birth_info": "استان هرمزگان / شهر بندر لنگه / تاریخ 1358/04/12",
                "issue_date": "1404/06/11",
                "exp_date": "1405/06/11",
                "municipality": "بندر لنگه",
                "fuel_1": "135 لیتر",
                "fuel_2": "-",
                "fuel_state": "موفق",
                "cargo_turns": ["دور اول: ماسه", "دور دوم: گچ", "دور سوم: سیمان"],
                "party_turns": [
                    "علی -> محمد",
                    "عبداله -> حسین",
                    "سلیمان -> محسن",
                ],
            },
            {
                "id": 2,
                "name": "عبداله آذرمهر",
                "sender_first": "عبداله",
                "sender_last": "آذرمهر",
                "receiver_first": "محسن",
                "receiver_last": "رضایی",
                "national_id": "3430010985",
                "login_nid": "3430010985",
                "password": "Aa13611361##",
                "mobile": "09171629988",
                "receiver_mobile": "09173614455",
                "referrer": "",
                "group": 2,
                "active": True,
                "plate_left": "24",
                "plate_letter": "ع",
                "plate_mid": "598",
                "plate_iran": "94",
                "tonnage": 3,
                "cargo": "گچ",
                "pack": "گونی",
                "weight": "3",
                "count": "50",
                "value": "40000000",
                "fare": "15000000",
                "post_fare": "15000000",
                "origin_name": "بندر لنگه",
                "dest_name": "بندر کنگ",
                "origin_city": "بندر لنگه",
                "dest_city": "بندر لنگه",
                "origin_neighborhood": "مرکز شهر",
                "dest_neighborhood": "ساحلی",
                "origin_addr": "ایران، هرمزگان، بندر لنگه، بلوار امام خمینی",
                "dest_addr": "ایران، هرمزگان، بندر کنگ، بلوار ساحلی یادمان",
                "origin_lat": 26.5579,
                "origin_lon": 54.8807,
                "dest_lat": 26.5946,
                "dest_lon": 54.9463,
                "distance_km": 20.55,
                "map_layer": "OSM سریع",
                "issue_enabled": True,
                "trip_enabled": True,
                "platform": "گوشی",
                "otp_mode": "بدون کد",
                "run_state": "در حال صدور (تلاش 1)",
                "ok_count": 6,
                "err_count": 0,
                "last_errors": [],
                "fleet_license": "-",
                "driver_license_num": "14639561232162",
                "driver_license_status": "منقضی شده",
                "license_state": "انجام شد",
                "owner_name": "شیوا گوری نژاد",
                "birth_info": "استان فارس / تاریخ 1361/07/01",
                "issue_date": "1403/05/01",
                "exp_date": "1404/05/01",
                "municipality": "سلطان شهر",
                "fuel_1": "125 لیتر",
                "fuel_2": "-",
                "fuel_state": "موفق",
                "cargo_turns": ["دور اول: گچ", "دور دوم: سیمان"],
                "party_turns": ["هاشم -> احمد", "ولید -> سینا"],
            },
            {
                "id": 3,
                "name": "محبوب شایانی",
                "sender_first": "محبوب",
                "sender_last": "شایانی",
                "receiver_first": "قاسم",
                "receiver_last": "دریایی",
                "national_id": "3440027611",
                "login_nid": "3440027611",
                "password": "Aa123456##",
                "mobile": "09171622039",
                "receiver_mobile": "09178889900",
                "referrer": "",
                "group": 1,
                "active": True,
                "plate_left": "55",
                "plate_letter": "ع",
                "plate_mid": "448",
                "plate_iran": "84",
                "tonnage": 3,
                "cargo": "سیمان",
                "pack": "کیسه",
                "weight": "3",
                "count": "60",
                "value": "45000000",
                "fare": "18000000",
                "post_fare": "18000000",
                "origin_name": "بندر لنگه",
                "dest_name": "بندر کنگ",
                "origin_city": "بندر لنگه",
                "dest_city": "بندر لنگه",
                "origin_neighborhood": "گزیر",
                "dest_neighborhood": "بندر کنگ",
                "origin_addr": "ایران، هرمزگان، بندر لنگه، دهستان مهرگان، گزیر",
                "dest_addr": "ایران، هرمزگان، بندر کنگ، خیابان امام خمینی",
                "origin_lat": 26.7120,
                "origin_lon": 54.8910,
                "dest_lat": 26.5946,
                "dest_lon": 54.9463,
                "distance_km": 18.20,
                "map_layer": "OSM سریع",
                "issue_enabled": True,
                "trip_enabled": True,
                "platform": "گوشی",
                "otp_mode": "بدون کد",
                "run_state": "آماده",
                "ok_count": 8,
                "err_count": 0,
                "last_errors": [],
                "fleet_license": "معتبر",
                "driver_license_num": "9982341122",
                "driver_license_status": "45 روز",
                "license_state": "انجام شد",
                "owner_name": "محبوب شایانی",
                "birth_info": "استان هرمزگان / شهر بندر لنگه / تاریخ 1365/02/15",
                "issue_date": "1404/08/01",
                "exp_date": "1405/08/01",
                "municipality": "بندر لنگه",
                "fuel_1": "80 لیتر",
                "fuel_2": "-",
                "fuel_state": "موفق",
                "cargo_turns": ["دور اول: سیمان", "دور دوم: ماسه"],
                "party_turns": ["عبدالقادر -> صدیق", "الیاس -> فیصل"],
            },
            {
                "id": 4,
                "name": "علی دهقان زاده",
                "sender_first": "علی",
                "sender_last": "دهقان زاده",
                "receiver_first": "ابراهیم",
                "receiver_last": "کریمی",
                "national_id": "3440418153",
                "login_nid": "3440418153",
                "password": "Aa13611361##",
                "mobile": "09173611122",
                "receiver_mobile": "09171112233",
                "referrer": "",
                "group": 1,
                "active": True,
                "plate_left": "62",
                "plate_letter": "ع",
                "plate_mid": "513",
                "plate_iran": "84",
                "tonnage": 30,
                "cargo": "مواد معدنی",
                "pack": "فله",
                "weight": "22",
                "count": "1",
                "value": "85000000",
                "fare": "35000000",
                "post_fare": "35000000",
                "origin_name": "باورد",
                "dest_name": "بندر کنگ",
                "origin_city": "بندر لنگه",
                "dest_city": "بندر لنگه",
                "origin_neighborhood": "باورد",
                "dest_neighborhood": "بندر کنگ",
                "origin_addr": "ایران، هرمزگان، بندر لنگه، باورد",
                "dest_addr": "ایران، هرمزگان، بندر کنگ",
                "origin_lat": 26.6950,
                "origin_lon": 54.8350,
                "dest_lat": 26.5946,
                "dest_lon": 54.9463,
                "distance_km": 20.55,
                "map_layer": "OSM سریع",
                "issue_enabled": True,
                "trip_enabled": True,
                "platform": "گوشی",
                "otp_mode": "بدون کد",
                "run_state": "آماده",
                "ok_count": 5,
                "err_count": 1,
                "last_errors": [
                    "10:56:41 - Minimum time not elapsed",
                    "13:15:00 - Insufficient gap from previous doc (driver)",
                ],
                "fleet_license": "معتبر",
                "driver_license_num": "7761239988",
                "driver_license_status": "60 روز",
                "license_state": "انجام شد",
                "owner_name": "علی دهقان زاده",
                "birth_info": "استان هرمزگان / شهر بندر لنگه / تاریخ 1362/11/20",
                "issue_date": "1404/09/01",
                "exp_date": "1405/09/01",
                "municipality": "بندر لنگه",
                "fuel_1": "2660 لیتر",
                "fuel_2": "-",
                "fuel_state": "موفق",
                "cargo_turns": [
                    "دور اول: سیمان",
                    "دور دوم: گچ",
                    "دور سوم: ماسه",
                ],
                "party_turns": ["صالح -> مسلم", "سلیمان -> محسن"],
            },
            {
                "id": 5,
                "name": "احمد آژند",
                "sender_first": "احمد",
                "sender_last": "آژند",
                "receiver_first": "سعید",
                "receiver_last": "بلوچی",
                "national_id": "5549924211",
                "login_nid": "5549924211",
                "password": "Aa13611361##",
                "mobile": "09177614455",
                "receiver_mobile": "09175556677",
                "referrer": "",
                "group": 1,
                "active": True,
                "plate_left": "74",
                "plate_letter": "ع",
                "plate_mid": "179",
                "plate_iran": "84",
                "tonnage": 3,
                "cargo": "گچ",
                "pack": "کیسه",
                "weight": "3",
                "count": "40",
                "value": "35000000",
                "fare": "16000000",
                "post_fare": "16000000",
                "origin_name": "بندر لنگه",
                "dest_name": "بندر کنگ",
                "origin_city": "بندر لنگه",
                "dest_city": "بندر لنگه",
                "origin_neighborhood": "بندر لنگه",
                "dest_neighborhood": "بندر کنگ",
                "origin_addr": "ایران، هرمزگان، بندر لنگه",
                "dest_addr": "ایران، هرمزگان، بندر کنگ",
                "origin_lat": 26.5579,
                "origin_lon": 54.8807,
                "dest_lat": 26.5946,
                "dest_lon": 54.9463,
                "distance_km": 20.55,
                "map_layer": "OSM سریع",
                "issue_enabled": True,
                "trip_enabled": True,
                "platform": "گوشی",
                "otp_mode": "بدون کد",
                "run_state": "آماده",
                "ok_count": 3,
                "err_count": 0,
                "last_errors": [],
                "fleet_license": "-",
                "driver_license_num": "-",
                "driver_license_status": "-",
                "license_state": "استعلام",
                "owner_name": "احمد آژند",
                "birth_info": "استان هرمزگان / تاریخ 1368/01/10",
                "issue_date": "1404/03/15",
                "exp_date": "1405/03/15",
                "municipality": "بندر کنگ",
                "fuel_1": "135 لیتر",
                "fuel_2": "-",
                "fuel_state": "موفق",
                "cargo_turns": ["دور اول: گچ", "دور دوم: سیمان"],
                "party_turns": ["علی -> محمد", "هاشم -> احمد"],
            },
            {
                "id": 6,
                "name": "محمد پورپاک",
                "sender_first": "محمد",
                "sender_last": "پورپاک",
                "receiver_first": "داود",
                "receiver_last": "شریفی",
                "national_id": "3440171735",
                "login_nid": "3440171735",
                "password": "Aa13611361##",
                "mobile": "09179991122",
                "receiver_mobile": "09174443322",
                "referrer": "",
                "group": 1,
                "active": True,
                "plate_left": "61",
                "plate_letter": "ع",
                "plate_mid": "926",
                "plate_iran": "84",
                "tonnage": 30,
                "cargo": "سیمان",
                "pack": "کیسه",
                "weight": "20",
                "count": "200",
                "value": "95000000",
                "fare": "40000000",
                "post_fare": "40000000",
                "origin_name": "بندرعباس",
                "dest_name": "بندر لنگه",
                "origin_city": "بندرعباس",
                "dest_city": "بندر لنگه",
                "origin_neighborhood": "اسکله شهید رجایی",
                "dest_neighborhood": "بندر لنگه",
                "origin_addr": "ایران، هرمزگان، بندرعباس، پایانه بار",
                "dest_addr": "ایران، هرمزگان، بندر لنگه",
                "origin_lat": 27.1832,
                "origin_lon": 56.2666,
                "dest_lat": 26.5579,
                "dest_lon": 54.8807,
                "distance_km": 192.40,
                "map_layer": "OSM سریع",
                "issue_enabled": True,
                "trip_enabled": True,
                "platform": "گوشی",
                "otp_mode": "کدی",
                "run_state": "در حال لاگین",
                "ok_count": 9,
                "err_count": 1,
                "last_errors": [],
                "fleet_license": "معتبر",
                "driver_license_num": "3440171735",
                "driver_license_status": "85 روز",
                "license_state": "انجام شد",
                "owner_name": "محمد پورپاک",
                "birth_info": "استان هرمزگان / شهر بندر لنگه / تاریخ 1364/05/19",
                "issue_date": "1404/10/01",
                "exp_date": "1405/10/01",
                "municipality": "بندر لنگه",
                "fuel_1": "2420 لیتر",
                "fuel_2": "-",
                "fuel_state": "موفق",
                "cargo_turns": [
                    "دور اول: سیمان",
                    "دور دوم: گچ",
                    "دور سوم: ماسه",
                ],
                "party_turns": ["عبداله -> بهروز", "علیرضا -> ابراهیم"],
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
      if c["username"].lower() == username.lower() and c["pass"] == password:
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

  def latlon_to_tile(self, lat, lon, zoom=14):
    lat_rad = math.radians(lat)
    n = 2.0**zoom
    xtile = int((lon + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return xtile, ytile

  def get_live_map_tile_url(self, lat, lon, zoom=14, layer="OSM سریع"):
    """تولید آدرس تصویر کاشی نقشه زنده بر اساس مختصات و نوع لایه نقشه"""
    x, y = self.latlon_to_tile(lat, lon, zoom)
    if "ماهواره" in layer:
      return f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{y}/{x}"
    elif "Esri خیابانی" in layer:
      return f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{zoom}/{y}/{x}"
    elif "توپوگرافی" in layer or "توپو" in layer:
      return f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{zoom}/{y}/{x}"
    else:
      return f"https://tile.openstreetmap.org/{zoom}/{x}/{y}.png"

  def reverse_geocode_osm(self, lat, lon):
    """دریافت زنده آدرس خیابان و محله از مختصات جغرافیایی روی نقشه (Nominatim OSM)"""
    try:
      url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1&accept-language=fa"
      req = urllib.request.Request(
          url, headers={"User-Agent": "BarGoBandarEnterprise/2.0"}
      )
      with urllib.request.urlopen(req, timeout=4) as resp:
        info = json.loads(resp.read().decode("utf-8"))
        display = info.get("display_name", "")
        addr = info.get("address", {})
        city = (
            addr.get("city")
            or addr.get("town")
            or addr.get("county")
            or "بندر لنگه"
        )
        suburb = (
            addr.get("suburb")
            or addr.get("neighbourhood")
            or addr.get("village")
            or addr.get("road")
            or "مرکز"
        )
        if display:
          return display, city, suburb
    except Exception:
      
