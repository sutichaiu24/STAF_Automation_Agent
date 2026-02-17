import asyncio
import json
import os
from playwright.async_api import async_playwright

async def dump_staf_login_dom():
    url = "https://friendshop-qa.sritrang.socket9.com/login"
    output_dir = "staf_dump"
    os.makedirs(output_dir, exist_ok=True)

    async with async_playwright() as p:
        # เปิด Browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"🚀 กำลังโหลดหน้า: {url}")
        # รอจน DOM โหลดเสร็จ
        await page.goto(url, wait_until="domcontentloaded")
        
        # รอให้ฟอร์ม Login ปรากฏ (ปรับ Selector ตามหน้าจริง)
        try:
            await page.wait_for_selector("input, button", timeout=10000)
        except:
            print("⚠️ คำเตือน: รอ Element นานเกินไป หน้าเว็บอาจจะโหลดช้า")

        # 1. ถ่าย Screenshot เพื่อใช้เทียบ
        screenshot_path = os.path.join(output_dir, "login_visual.png")
        await page.screenshot(path=screenshot_path, full_page=False)
        print(f"📸 บันทึก Screenshot แล้วที่: {screenshot_path}")

        # 2. สกัด DOM เฉพาะส่วนที่โต้ตอบได้ (Interactive Elements)
        # เราจะเก็บทั้ง Text, Tag, และพิกัด (Rect) เพื่อใช้จับคู่
        dom_structure = await page.evaluate("""
            () => {
                const interactiveElements = document.querySelectorAll('button, input, a, [role="button"]');
                return Array.from(interactiveElements).map(el => {
                    const rect = el.getBoundingClientRect();
                    return {
                        tag: el.tagName,
                        type: el.getAttribute('type') || '',
                        id: el.id || '',
                        class: el.className || '',
                        text: el.innerText || el.placeholder || el.getAttribute('aria-label') || '',
                        location: {
                            x: rect.left,
                            y: rect.top,
                            width: rect.width,
                            height: rect.height
                        }
                    };
                }).filter(item => item.location.width > 0); // กรองเฉพาะตัวที่มองเห็นจริง
            }
        """)

        # 3. บันทึกเป็นไฟล์ JSON
        json_path = os.path.join(output_dir, "login_dom.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(dom_structure, f, indent=2, ensure_ascii=False)
        
        print(f"📄 สกัด DOM เรียบร้อยแล้วที่: {json_path}")
        print(f"✅ พบ Element ทั้งหมด {len(dom_structure)} รายการ")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(dump_staf_login_dom())