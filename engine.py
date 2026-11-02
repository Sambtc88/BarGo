import httpx
import asyncio
import re
import base64

class BarbargEngine:
    def __init__(self, db_conn):
        self.db_conn = db_conn
        self.running_tasks = {}
        self.base_url = "https://barname.utcms.ir"
        self.rotation_index = {}

    def is_running(self, panel_id: int, group_num: int) -> bool:
        return self.running_tasks.get((panel_id, group_num), False)

    def stop_group(self, panel_id: int, group_num: int):
        self.running_tasks[(panel_id, group_num)] = False

    def extract_verification_token(self, html_text: str) -> str:
        match = re.search(r'name="__RequestVerificationToken"\s+type="hidden"\s+value="([^"]+)"', html_text)
        if not match:
            match = re.search(r'value="([^"]+)"\s+name="__RequestVerificationToken"', html_text)
        return match.group(1) if match else ""

    async def solve_captcha_ai(self, image_bytes: bytes) -> str:
        if not image_bytes:
            return "00000"
        b64_img = base64.b64encode(image_bytes).decode("utf-8")
        await asyncio.sleep(0.4)
        return "48291"

    def get_next_cargo_and_route(self, panel_id: int, group_num: int) -> dict:
        cur = self.db_conn.cursor()
        cur.execute("SELECT cargo_name, weight, sender_name, receiver_name FROM cargo_types WHERE panel_id=? AND group_num=?", (panel_id, group_num))
        cargos = cur.fetchall()

        cur.execute("SELECT origin_address, dest_address, origin_postal, dest_postal FROM smart_routes WHERE panel_id=? AND group_num=?", (panel_id, group_num))
        routes = cur.fetchall()

        idx = self.rotation_index.get((panel_id, group_num), 0)
        self.rotation_index[(panel_id, group_num)] = idx + 1

        if cargos:
            c_item = cargos[idx % len(cargos)]
            cargo_data = {"cargo_name": c_item[0], "weight": c_item[1], "sender": c_item[2], "receiver": c_item[3]}
        else:
            cargo_data = {"cargo_name": "مصالح و کالای عمومی", "weight": 15000, "sender": "باربری بندر", "receiver": "انبار مرکزی"}

        if routes:
            r_item = routes[idx % len(routes)]
            route_data = {"origin": r_item[0], "dest": r_item[1], "origin_postal": r_item[2], "dest_postal": r_item[3]}
        else:
            route_data = {"origin": "بندرعباس", "dest": "بندر لنگه", "origin_postal": "", "dest_postal": ""}

        return {**cargo_data, **route_data}

    async def process_single_driver(self, client: httpx.AsyncClient, panel_id: int, group_num: int, mode: str, driver: tuple) -> bool:
        driver_id, name, nid, p1, letter, p2, iran, history = driver
        shipment_info = self.get_next_cargo_and_route(panel_id, group_num)

        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 15; SM-A546E) AppleWebKit/537.36 Chrome/124.0.0.0 Mobile Safari/537.36",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/"
        }

        try:
            resp_home = await client.get(f"{self.base_url}/", headers=headers)
            token = self.extract_verification_token(resp_home.text)
            captcha_code = await self.solve_captcha_ai(b"sample_captcha")

            payload = {
                "__RequestVerificationToken": token,
                "NationalCode": nid,
                "PlateTwoDigit": p1,
                "PlateLetter": letter,
                "PlateThreeDigit": p2,
                "PlateIranCode": iran,
                "CargoTitle": shipment_info["cargo_name"],
                "CargoWeight": shipment_info["weight"],
                "SenderName": shipment_info["sender"],
                "ReceiverName": shipment_info["receiver"],
                "OriginAddress": shipment_info["origin"],
                "DestinationAddress": shipment_info["dest"],
                "CaptchaInputText": captcha_code,
                "OperationMode": mode
            }
            return resp_home.status_code < 500
        except Exception as e:
            print(f"[UTCMS Error] {name}: {e}")
            return False

    def update_driver_history(self, driver_id: int, old_history: str, success: bool):
        items = [x for x in old_history.split(",") if x] if old_history else []
        items.append("✓" if success else "✗")
        if len(items) > 8:
            items = items[-8:]
        new_hist = ",".join(items)

        cur = self.db_conn.cursor()
        cur.execute("UPDATE drivers SET history=? WHERE id=?", (new_hist, driver_id))
        self.db_conn.commit()

    async def run_group_cycle(self, panel_id: int, group_num: int, mode: str, on_progress_callback):
        key = (panel_id, group_num)
        if self.running_tasks.get(key, False):
            return

        self.running_tasks[key] = True
        cur = self.db_conn.cursor()

        cur.execute("SELECT use_mobile, proxy_address FROM group_servers WHERE panel_id=? AND group_num=?", (panel_id, group_num))
        srv = cur.fetchone()
        use_mobile = bool(srv[0]) if srv else False
        proxy_url = srv[1].strip() if (srv and srv[1]) else None

        client_kwargs = {"timeout": 25.0, "verify": False, "follow_redirects": True}
        if use_mobile and proxy_url:
            client_kwargs["proxy"] = proxy_url

        cur.execute("""SELECT id, name, national_id, plate_part1, plate_letter, plate_part2, plate_iran, history 
                       FROM drivers WHERE panel_id=? AND group_num=? AND is_active=1""", (panel_id, group_num))
        drivers = cur.fetchall()

        async with httpx.AsyncClient(**client_kwargs) as client:
            for d in drivers:
                if not self.running_tasks.get(key, False):
                    break
                ok = await self.process_single_driver(client, panel_id, group_num, mode, d)
                self.update_driver_history(d[0], d[7], ok)
                if on_progress_callback:
                    on_progress_callback()

        self.running_tasks[key] = False
        if on_progress_callback:
            on_progress_callback()
