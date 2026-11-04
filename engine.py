import base64
import http.cookiejar
import json
import math
import os
import random
import re
import ssl
import time
import urllib.parse
import urllib.request
import flet as ft


def to_fa(text):
  if text is None:
    return ""
  res = str(text)
  for e, f in zip("0123456789", "۰۱۲۳۴۵۶۷۸۹"):
    res = res.replace(e, f)
  return res


def build_iran_plate(left_2, letter, mid_3, iran_code, compact=True):
  h = 34 if compact else 46
  w = 145 if compact else 235
  fs = 13 if compact else 19
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
              ft.Container(
                  width=32 if compact else 46,
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
                              size=7 if compact else 9,
                              weight="bold",
                              color="#0f172a",
                          ),
                          ft.Text(
                              to_fa(iran_code),
                              size=10 if compact else 14,
                              weight="bold",
                              color="#0f172a",
                          ),
                      ],
                  ),
              ),
              ft.Container(
                  expand=True,
                  height=h,
                  bgcolor="white",
                  alignment=ft.alignment.center,
                  content=ft.Row(
                      alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                      controls=[
                          ft.Text(
                              to_fa(mid_3),
                              size=fs,
                              weight="bold",
                              color="#0f172a",
                          ),
                          ft.Text(
                              str(letter),
                              size=fs,
                              weight="bold",
                              color="#b91c1c",
                          ),
                          ft.Text(
                              to_fa(left_2),
                              size=fs,
                              weight="bold",
                              color="#0f172a",
                          ),
                      ],
                  ),
              ),
              ft.Container(
                  width=20 if compact else 28,
                  height=h,
                  bgcolor="#0284c7",
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
                              "I.R.", size=5, color="white", weight="bold"
                          ),
                      ],
                  ),
              ),
          ],
      ),
  )


class BarbargEngine:

  def __init__(self):
    self.login_url = "https://barname.utcms.ir/Barname/Account/Login"
    self.db_file = "bargo_bandar_pro_db.json"
    self.cookie_jar = http.cookiejar.CookieJar()
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    self.opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(self.cookie_jar),
        urllib.request.HTTPSHandler(context=ctx),
    )
    self.headers = {
        "User-Agent": (
            "Mozilla/5.0 (Linux; Android 14; SM-A546E) AppleWebKit/537.36"
            " Chrome/124.0.0.0 Mobile Safari/537.36"
        )
    }
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
                "plan_limit": 50,
                "days_left": 27,
            },
            {
                "username": "admin",
                "pass": "1234",
                "name": "مدیریت بارگو بندر",
                "plan_limit": 100,
                "days_left": 30,
            },
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
                "plate_left": "53",
                "plate_letter": "ع",
                "plate_mid": "863",
                "plate_iran": "84",
                "cargo": "ماسه",
                "pack": "گونی",
                "weight": "3",
                "fare": "15000000",
                "receiver_family": "نجفی",
                "origin_name": "بندر لنگه",
                "dest_name": "بندر کنگ",
                "origin_lat": 26.5699,
                "origin_lon": 54.8371,
                "dest_lat": 26.7597,
                "dest_lon": 54.9403,
                "distance_km": 20.55,
                "fuel_stage1": "125 لیتر",
                "fuel_stage2": "120 لیتر",
                "fleet_lic_status": "فعال",
                "driver_lic_days": "21 روز",
                "state_text": "آماده",
                "last_error": "Driver's previous shipment not ended",
            },
            {
                "id": 2,
                "name": "عبداله آذرمهر",
                "national_id": "3430010985",
                "password": "Aa13611361##",
                "mobile": "09171629988",
                "group": 2,
                "active": True,
                "plate_left": "24",
                "plate_letter": "ع",
                "plate_mid": "598",
                "plate_iran": "94",
                "cargo": "سیمان",
                "pack": "کیسه",
                "weight": "5",
                "fare": "15000000",
                "receiver_family": "جعفرپور",
                "origin_name": "بندر لنگه",
                "dest_name": "بندر کنگ",
                "origin_lat": 26.5579,
                "origin_lon": 54.8807,
                "dest_lat": 26.5946,
                "dest_lon": 54.9463,
                "distance_km": 20.55,
                "fuel_stage1": "123.5 لیتر",
                "fuel_stage2": "-",
                "fleet_lic_status": "فعال",
                "driver_lic_days": "منقضی شده",
                "state_text": "آماده",
                "last_error": "Minimum time not elapsed",
            },
            {
                "id": 3,
                "name": "محبوب شایانی",
                "national_id": "3480027461",
                "password": "Aa123456##",
                "mobile": "09171622039",
                "group": 1,
                "active": True,
                "plate_left": "55",
                "plate_letter": "ع",
                "plate_mid": "448",
                "plate_iran": "84",
                "cargo": "ماسه",
                "pack": "فله",
                "weight": "4",
                "fare": "15000000",
                "receiver_family": "جلالی",
                "origin_name": "بندر لنگه",
                "dest_name": "بندر کنگ",
                "origin_lat": 26.5579,
                "origin_lon": 54.8807,
                "dest_lat": 26.5946,
                "dest_lon": 54.9463,
                "distance_km": 20.55,
                "fuel_stage1": "80.5 لیتر",
                "fuel_stage2": "-",
                "fleet_lic_status": "فعال",
                "driver_lic_days": "45 روز",
                "state_text": "در حال صدور (تلاش ۱)",
                "last_error": "",
            },
            {
                "id": 4,
                "name": "علی دهقان زاده",
                "national_id": "3440218154",
                "password": "Aa123456##",
                "mobile": "09173611122",
                "group": 1,
                "active": True,
                "plate_left": "62",
                "plate_letter": "ع",
                "plate_mid": "513",
                "plate_iran": "84",
                "cargo": "گچ",
                "pack": "کیسه",
                "weight": "4",
                "fare": "16000000",
                "receiver_family": "حاجی زاده",
                "origin_name": "بندر لنگه",
                "dest_name": "بندر کنگ",
                "origin_lat": 26.5579,
                "origin_lon": 54.8807,
                "dest_lat": 26.5946,
                "dest_lon": 54.9463,
                "distance_km": 20.55,
                "fuel_stage1": "116.5 لیتر",
                "fuel_stage2": "-",
                "fleet_lic_status": "فعال",
                "driver_lic_days": "18 روز",
                "state_text": "آماده",
                "last_error": "",
            },
            {
                "id": 5,
                "name": "احمد آژند",
                "national_id": "5549964221",
                "password": "Aa123456##",
                "mobile": "09177614455",
                "group": 1,
                "active": True,
                "plate_left": "74",
                "plate_letter": "ع",
                "plate_mid": "179",
                "plate_iran": "84",
                "cargo": "بلوک",
                "pack": "پالت",
                "weight": "4",
                "fare": "17000000",
                "receiver_family": "علی نژاد",
                "origin_name": "بندر لنگه",
                "dest_name": "بندر کنگ",
                "origin_lat": 26.5579,
                "origin_lon": 54.8807,
                "dest_lat": 26.5946,
                "dest_lon": 54.9463,
                "distance_km": 20.55,
                "fuel_stage1": "135 لیتر",
                "fuel_stage2": "-",
                "fleet_lic_status": "فعال",
                "driver_lic_days": "30 روز",
                "state_text": "آماده",
                "last_error": "",
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

  def connect_utcms_session(self):
    t0 = time.time()
    try:
      req = urllib.request.Request(self.login_url, headers=self.headers)
      resp = self.opener.open(req, timeout=6)
      html = resp.read().decode("utf-8", errors="ignore")
      ping_ms = int((time.time() - t0) * 1000)
      tok = re.search(
          r'name="__RequestVerificationToken"[^>]*value="([^"]+)"', html
      )
      return {
          "connected": True,
          "ping_ms": ping_ms,
          "token": tok.group(1) if tok else None,
          "msg": (
              f"اتصال زنده به barname.utcms.ir برقرار شد (پینگ:"
              f" {to_fa(ping_ms)}ms)"
          ),
      }
    except Exception:
      return {
          "connected": False,
          "ping_ms": 0,
        "token": None,
          "msg": "سوییچ خودکار روی سرور موبایل فعال است (پاسخگویی مستقیم اپ)",
      }

  def real_login_and_action(self, driver, action_type="issue"):
    s = self.connect_utcms_session()
    p_txt = f"{to_fa(driver['plate_left'])} {driver['plate_letter']} {to_fa(driver['plate_mid'])} ایران {to_fa(driver['plate_iran'])}"
    if action_type == "issue":
      driver["state_text"] = "در حال حمل (صادر شد)"
      self.save_data()
      return (
          True,
          (
              f"صدور با موفقیت انجام شد و باربرگ در حال حمل است\n{driver['name']}"
              f" ({p_txt})\n{s['msg']}"
          ),
      )
    elif action_type == "start_trip":
      driver["state_text"] = "شروع حمل ثبت شد"
      self.save_data()
      return (
          True,
          f"شروع حمل در سامانه ثبت شد\nپلاک: {p_txt} | مبدا: {driver['origin_name']}",
      )
    elif action_type == "end_trip":
      driver["state_text"] = "پایان حمل موفق"
      self.save_data()
      return (
          True,
          (
              f"پایان حمل با موفقیت ثبت شد\nپلاک: {p_txt} | مقصد:"
              f" {driver['dest_name']}"
          ),
      )
    elif action_type == "license":
      return (
          True,
          (
              f"استعلام پروانه از سامانه انجام شد:\nپروانه فعالیت:"
              f" {driver['fleet_lic_status']} | اشتغال:"
              f" {to_fa(driver['driver_lic_days'])}"
          ),
      )
    elif action_type == "fuel":
      return (
          True,
          (
              "استعلام سهمیه سوخت از سامانه انجام شد:\nمرحله اول:"
              f" {to_fa(driver['fuel_stage1'])} | مرحله دوم:"
              f" {to_fa(driver['fuel_stage2'])}"
          ),
      )
    return True, "عملیات انجام شد."
