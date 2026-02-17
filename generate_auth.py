"""
generate_auth.py — สร้าง auth.json (เก็บ session หลัง login)
รันครั้งเดียวเมื่อต้องการปั๊ม auth state เพื่อให้ test อื่นใช้ skip login

Usage:
  cd STAF_Automation_Agent
  python generate_auth.py
"""
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

# --- กำหนดค่า (ให้ตรงกับ sritrang_login_function.py) ---
EMAIL = "admin@socket9.com"
PASSWORD = "admin@12345$"
BASE_URL = "https://friendshop-qa.sritrang.socket9.com"
# เก็บ auth ไว้ที่ scripts/auth.json
AUTH_PATH = Path(__file__).resolve().parent / "scripts" / "auth.json"


def main():
    print("📂 บันทึก auth ที่:", AUTH_PATH)
    os.makedirs(AUTH_PATH.parent, exist_ok=True)
    print("🌐 กำลังเปิด browser (headed)...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=True,
        )
        page = context.new_page()
        page.set_default_timeout(30000)

        try:
            # 1. ไปหน้า Login
            print("🚀 กำลังไปยังหน้า login...")
            page.goto(f"{BASE_URL}/login", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle", timeout=15000)
            page.wait_for_timeout(2000)

            # 2. Dropdown "จัดการร้านค้าของฉัน" → "จัดการระบบศรีตรัง"
            print("🏪 เลือก dropdown 'จัดการร้านค้าของฉัน' → 'จัดการระบบศรีตรัง'...")
            dropdown = page.get_by_text("จัดการร้านค้าของฉัน", exact=False)
            dropdown.wait_for(state="visible", timeout=5000)
            dropdown.click()
            page.wait_for_timeout(2000)
            sritrang_option = page.locator('li.MuiMenuItem-root:has-text("จัดการระบบศรีตรัง")').first
            sritrang_option.wait_for(state="visible", timeout=5000)
            sritrang_option.click()
            page.wait_for_timeout(1000)

            # 3. กรอกอีเมล
            print(f"📧 กรอกอีเมล: {EMAIL}")
            try:
                page.get_by_placeholder("อีเมล").fill(EMAIL)
            except Exception:
                page.locator("input#\\:r3\\:").fill(EMAIL)
            page.wait_for_timeout(500)

            # 4. กรอกรหัสผ่าน
            print("🔑 กรอกรหัสผ่าน...")
            try:
                page.locator("input#\\:r4\\:").fill(PASSWORD)
            except Exception:
                page.locator('input[type="password"]').fill(PASSWORD)
            page.wait_for_timeout(500)

            # 5. คลิก "เข้าสู่ระบบ"
            print("🔘 คลิกปุ่ม 'เข้าสู่ระบบ'...")
            try:
                page.get_by_role("button", name="เข้าสู่ระบบ", exact=True).click()
            except Exception:
                page.locator('button.MuiButton-contained:has-text("เข้าสู่ระบบ")').first.click()

            # 6. รอให้ login สำเร็จ — รอ sidebar / dashboard ปรากฏ
            print("⏳ รอ sidebar / dashboard...")
            page.wait_for_timeout(3000)
            # รอ element ที่มีหลัง login (sidebar มี "ภาพรวม" หรือ "พอยท์งบประมาณ")
            page.get_by_text("ภาพรวม").first.wait_for(state="visible", timeout=15000)
            print("✅ Login สำเร็จ — พบ sidebar / dashboard")

            # 7. บันทึก storage state
            context.storage_state(path=str(AUTH_PATH))
            print(f"💾 บันทึก auth state แล้วที่: {AUTH_PATH}")
        except Exception as e:
            print(f"❌ Error: {e}")
            raise
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    main()
