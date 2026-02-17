
import asyncio
import json
import os
from playwright.async_api import async_playwright

# --- กำหนดค่า (แก้ได้ตามต้องการ) ---
EMAIL = "admin@socket9.com"
PASSWORD = "admin@12345$"
BASE_URL = "https://friendshop-qa.sritrang.socket9.com"
# หน้าที่ต้องการ dump หลัง login (ถ้าไม่ redirect มาที่นี่อัตโนมัติ จะไปให้)
TARGET_URL_AFTER_LOGIN = "https://friendshop-qa.sritrang.socket9.com/point-budget"
OUTPUT_DIR = "staf_dump"


async def login_then_dump():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    async with async_playwright() as p:
        # เปิด Browser (headless=False เพื่อให้เห็นและกด enter ได้ถ้าต้องการ)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # ========== STEP 1: ไปหน้า Login ==========
        login_url = f"{BASE_URL}/login"
        print(f"🚀 Step 1: ไปยังหน้า login... {login_url}")
        await page.goto(login_url, wait_until="domcontentloaded")
        await page.wait_for_load_state("networkidle", timeout=15000)
        await asyncio.sleep(2)

        # ========== STEP 2: เลือก dropdown "จัดการร้านค้าของฉัน" → "จัดการระบบศรีตรัง" ==========
        print("🏪 Step 2: เลือก dropdown 'จัดการร้านค้าของฉัน' → 'จัดการระบบศรีตรัง'...")
        dropdown = page.get_by_text("จัดการร้านค้าของฉัน", exact=False)
        await dropdown.wait_for(state="visible", timeout=5000)
        await dropdown.click()
        await asyncio.sleep(2)

        sritrang_option = page.locator('li.MuiMenuItem-root:has-text("จัดการระบบศรีตรัง")').first
        await sritrang_option.wait_for(state="visible", timeout=5000)
        await sritrang_option.click()
        await asyncio.sleep(1)
        print("  ✅ เลือก 'จัดการระบบศรีตรัง' แล้ว")

        # ========== STEP 3: กรอกอีเมล ==========
        print(f"📧 Step 3: กรอกอีเมล: {EMAIL}")
        try:
            await page.get_by_placeholder("อีเมล").fill(EMAIL)
        except Exception:
            await page.locator('input#\\:r3\\:').fill(EMAIL)
        await asyncio.sleep(0.5)

        # ========== STEP 4: กรอกรหัสผ่าน ==========
        print("🔑 Step 4: กรอกรหัสผ่าน...")
        try:
            await page.locator('input#\\:r4\\:').fill(PASSWORD)
        except Exception:
            await page.locator('input[type="password"]').fill(PASSWORD)
        await asyncio.sleep(0.5)

        # ========== STEP 5: คลิกปุ่ม "เข้าสู่ระบบ" ==========
        print("🔘 Step 5: คลิกปุ่ม 'เข้าสู่ระบบ'...")
        try:
            await page.get_by_role("button", name="เข้าสู่ระบบ", exact=True).click()
        except Exception:
            await page.locator('button.MuiButton-contained:has-text("เข้าสู่ระบบ")').first.click()
        await asyncio.sleep(3)

        # เช็คว่าอยู่หน้า login ยัง (ถ้ายัง = login อาจไม่สำเร็จ)
        if "/login" in page.url.lower():
            print("⚠️  ยังอยู่ที่หน้า login อาจจะ login ไม่สำเร็จ หรือรอ redirect ช้า")
            print("   กด Enter ใน terminal เพื่อลอง dump หน้าปัจจุบันต่อ หรือรอสักครู่...")
            # รอให้ user กด Enter (optional)
            await asyncio.sleep(5)
        else:
            print("✅ Login สำเร็จ (URL เปลี่ยนจากหน้า login)")

        # ========== STEP 6: ไปหน้าที่ต้องการ dump (ถ้ายังไม่อยู่ที่นั้น) ==========
        if TARGET_URL_AFTER_LOGIN and page.url.rstrip("/") != TARGET_URL_AFTER_LOGIN.rstrip("/"):
            print(f"🌐 Step 6: ไปยังหน้าเป้าหมาย... {TARGET_URL_AFTER_LOGIN}")
            await page.goto(TARGET_URL_AFTER_LOGIN, wait_until="domcontentloaded")
            await page.wait_for_load_state("networkidle", timeout=15000)
            await asyncio.sleep(2)
        else:
            print("📌 Step 6: อยู่หน้าที่ต้องการแล้ว ไม่ต้อง navigate")

        # ========== STEP 7: รอให้ user กด Enter (optional) ==========
        print("\n⏸️  พร้อม dump แล้ว กด Enter ใน terminal เพื่อเริ่ม extract DOM + screenshot...")
        # รอใน thread แยก: ให้ main thread รอ input จาก user
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, input)

        # ========== STEP 8: ถ่าย Screenshot ==========
        screenshot_path = os.path.join(OUTPUT_DIR, "login_visual.png")
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"📸 บันทึก Screenshot แล้วที่: {screenshot_path}")

        # ========== STEP 9: สกัด DOM (Interactive Elements) ==========
        dom_structure = await page.evaluate("""
            () => {
                const interactiveElements = document.querySelectorAll('button, input, a, [role="button"], select, [role="menuitem"]');
                return Array.from(interactiveElements).map(el => {
                    const rect = el.getBoundingClientRect();
                    return {
                        tag: el.tagName,
                        type: el.getAttribute('type') || '',
                        id: el.id || '',
                        class: el.className || '',
                        text: el.innerText?.trim().slice(0, 200) || el.getAttribute('placeholder') || el.getAttribute('aria-label') || '',
                        location: {
                            x: rect.left,
                            y: rect.top,
                            width: rect.width,
                            height: rect.height
                        }
                    };
                }).filter(item => item.location.width > 0 && item.location.height > 0);
            }
        """)

        json_path = os.path.join(OUTPUT_DIR, "extract_dom.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(dom_structure, f, indent=2, ensure_ascii=False)

        print(f"📄 สกัด DOM เรียบร้อยที่: {json_path}")
        print(f"✅ พบ Element ทั้งหมด {len(dom_structure)} รายการ")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(login_then_dump())
