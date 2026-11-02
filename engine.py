import time
import urllib.request
import json

class BarbargEngine:
    def __init__(self):
        # حالت پیش‌فرض سرور: سامانه درون‌شهری
        self.active_server = "urban_main"

    def switch_server(self, server_type):
        """سوییچ بین سرور سامانه درون‌شهری و آنتن موبایل"""
        if server_type == "urban":
            self.active_server = "urban_main"
            print("[Engine] سوییچ روی سرور اصلی سامانه درون‌شهری انجام شد.")
        elif server_type == "mobile":
            self.active_server = "mobile_antenna"
            print("[Engine] سوییچ روی سرور آنتن موبایل (هات‌اسپات سیم‌کارت) انجام شد.")
        return self.active_server

    def register_plate_task(self, plate_data, group_num):
        """منطق پردازش و ارسال پلاک به صف و سامانه"""
        server_name = "سرور سامانه درون‌شهری" if self.active_server == "urban_main" else "سرور آنتن موبایل"
        print(f"[{server_name}] در حال پردازش پلاک گروه {group_num}: {plate_data}")
        
        # شبیه‌سازی ارتباط امن و پردازش درخواست
        time.sleep(0.5)
        
        # خروجی موفقیت عملیات
        return {
            "status": "success",
            "server": server_name,
            "group": group_num,
            "message": f"پلاک با موفقیت از طریق {server_name} ثبت شد."
        }

if __name__ == "__main__":
    engine = BarbargEngine()
    print("موتور پردازشی باربرگ بندر بارگذاری شد و آماده به کار است.")
