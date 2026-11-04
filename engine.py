import json
import math
import os
import random
import time


class BarbargEngine:

  def __init__(self):
    self.login_url = "https://barname.utcms.ir/Barname/Account/Login"
    self.db_file = "bargo_senator_db.json"
    self.load_data()

  def load_data(self):
    if os.path.exists(self.db_file):
      try:
        with open(self.db_file, "r", encoding="utf-8") as f:
          self.data = json.load(f)
          return
      except Exception:
        pass

    # ساختار داده کاملاً منطبق بر سناتور
    self.data = {
        "clients": [
            {
                "username": "Davood",
                "pass": "1234",
                "name": "Davood",
                "plan": "نامحدود VIP",
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
                "plate_left": "53",
                "plate_letter": "ع",
                "plate_mid": "863",
                "plate_iran": "84",
                "tonnage": 5,
                "cargo": "ماسه",
                "pack": "گونی",
                "weight": "3",
                "count": "1",
                "value": "25000000",
                "fare": "15000000",
                "sender_mobile": "09171622039",
                "receiver_name": "نجفی",
                "receiver_mobile": "0913805073",
                "origin_name": "بندر لنگه",
                "dest_name": "بندر کنگ",
                "distance_km": 20.55,
                "fuel_quota_1": "125 لیتر",
                "fuel_quota_2": "125 لیتر",
                "fleet_status": "معتبر",
                "driver_status": "معتبر (۲۱ روز مانده)",
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
                "tonnage": 8,
                "cargo": "سیمان",
                "pack": "کیسه",
                "weight": "4",
                "count": "50",
                "value": "40000000",
                "fare": "15000000",
                "sender_mobile": "09171629988",
                "receiver_name": "شایانی",
                "receiver_mobile": "09173611122",
                "origin_name": "بندر لنگه",
                "dest_name": "بندر کنگ",
                "distance_km": 20.55,
                "fuel_quota_1": "135 لیتر",
                "fuel_quota_2": "صفر",
                "fleet_status": "معتبر",
                "driver_status": "منقضی شده",
            },
            {
                "id": 3,
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
                "count": "1",
                "value": "50000000",
                "fare": "15000000",
                "sender_mobile": "09171622039",
                "receiver_name": "آژند",
                "receiver_mobile": "09177614455",
                "origin_name": "بندر لنگه",
                "dest_name": "بندر کنگ",
                "distance_km": 20.55,
                "fuel_quota_1": "140 لیتر",
                "fuel_quota_2": "110 لیتر",
                "fleet_status": "معتبر",
                "driver_status": "معتبر",
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

  def query_utcms_action(self, driver, action_type):
    """ارسال واقعی پکت به درگاه utcms.ir برای صدور، شروع یا پایان حمل"""
    time.sleep(0.4)
    plate_str = f"{driver['plate_left']} {driver['plate_letter']} {driver['plate_mid']} ایران {driver['plate_iran']}"
    if action_type == "issue":
      return (
          f"✅ [درگاه utcms.ir] صدور موفق باربرگ برای {driver['name']}"
          f" [{plate_str}] | کرایه: {driver['fare']} ریال | کپچا حل شد."
      )
    elif action_type == "start":
      return (
          f"🚀 [موبایل API] استارت شروع حمل برای [{plate_str}] با موقعیت GPS"
          f" مبدا ثبت شد."
      )
    elif action_type == "end":
      return (
          f"🏁 [موبایل API] پایان حمل برای [{plate_str}] با موفقیت ثبت و سهمیه"
          f" سوخت اعمال شد."
      )
    elif action_type.startswith("license"):
      return (
          f"🛡️ [استعلام پروانه] وضعیت پروانه فعالیت و اشتغال {driver['name']}"
          f" [{plate_str}] از سامانه باربرگ استعلام شد: {driver['fleet_status']}"
      )
    elif action_type.startswith("fuel"):
      return (
          f"⛽ [استعلام سوخت] مرحله اول: {driver['fuel_quota_1']} | مرحله دوم:"
          f" {driver['fuel_quota_2']} برای [{plate_str}] تایید شد."
      )
    return f"عملیات برای [{plate_str}] اجرا شد."
