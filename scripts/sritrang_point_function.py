"""
sritrang_point_function.py — Test สร้างพอยท์งบประมาณ (ใช้ auth.json ไม่ต้อง login ใหม่)
ต้องรัน generate_auth.py ก่อนครั้งแรก เพื่อสร้าง scripts/auth.json
"""
import pytest
from pathlib import Path
from datetime import datetime
from playwright.sync_api import Page, expect

# --- CONFIGURATION ---
BASE_URL = "https://friendshop-qa.sritrang.socket9.com"
POINT_BUDGET_URL = "https://friendshop-qa.sritrang.socket9.com/point-budget"
AUTH_JSON_PATH = Path(__file__).resolve().parent / "auth.json"
TOTAL_POINTS_VALUE = "5000"

# ช่องวันที่: ตัวเปิด picker คือ div[aria-haspopup="true"].cursor-pointer ที่มีข้อความ "วว/ดด/ปปปป"
DATE_FIELD_TRIGGER = 'div[aria-haspopup="true"].cursor-pointer'
DATE_FIELD_TEXT = "วว/ดด/ปปปป"


@pytest.fixture(scope="function")
def auth_page(playwright, browser_context_args):
    """Page ที่โหลด session จาก auth.json (skip login). บังคับ headless=False เพื่อให้เห็น browser."""
    if not AUTH_JSON_PATH.exists():
        print("\n⚠️  ไม่พบ auth.json ที่:", AUTH_JSON_PATH)
        pytest.skip("auth.json ไม่พบ — รัน generate_auth.py ก่อน: python generate_auth.py")
    print("\n🔐 โหลด auth จาก", AUTH_JSON_PATH)
    print("🌐 กำลังเปิด browser (headed)...")
    browser = playwright.chromium.launch(headless=False, slow_mo=0)
    context = browser.new_context(**browser_context_args, storage_state=str(AUTH_JSON_PATH))
    page = context.new_page()
    page.set_default_timeout(30000)
    yield page
    page.close()
    context.close()
    browser.close()


def _fill_total_points(page: Page) -> None:
    """กรอกจำนวนพอยท์ทั้งหมด — ช่องจริงใช้ placeholder="0.00" (ยืนยันจาก F12 แล้ว)."""
    try:
        page.get_by_placeholder("0.00").fill(TOTAL_POINTS_VALUE)
        return
    except Exception:
        pass
    try:
        page.get_by_label("จำนวนพอยท์ทั้งหมด").fill(TOTAL_POINTS_VALUE)
        return
    except Exception:
        pass
    try:
        page.locator('div:has-text("จำนวนพอยท์ทั้งหมด")').locator('input[placeholder="0.00"]').first.fill(
            TOTAL_POINTS_VALUE
        )
        return
    except Exception:
        pass
    page.locator('div:has-text("จำนวนพอยท์ทั้งหมด")').locator("input").first.fill(TOTAL_POINTS_VALUE)


def _click_date_field(page: Page) -> None:
    """คลิกช่องระยะเวลาการใช้งาน เพื่อเปิด Date Picker."""
    try:
        page.locator(DATE_FIELD_TRIGGER).filter(has_text=DATE_FIELD_TEXT).first.click(timeout=6000)
        return
    except Exception:
        pass
    try:
        page.locator('div:has-text("ระยะเวลาการใช้งาน")').get_by_role("button").first.click(timeout=6000)
        return
    except Exception:
        pass
    try:
        page.locator('div.MuiInputBase-input.Mui-readOnly').filter(has_text=DATE_FIELD_TEXT).locator(
            'xpath=ancestor::div[contains(@class,"MuiOutlinedInput-root")][1]'
        ).first.click(timeout=6000)
        return
    except Exception:
        pass
    page.get_by_text(DATE_FIELD_TEXT, exact=False).first.click(timeout=6000)


def test_add_budget_point(auth_page: Page):
    """
    Test: สร้างพอยท์งบประมาณ
    ใส่ชื่อ → จำนวนพอยท์ → ระยะเวลา (Date Picker) → เปิดใช้งาน → บันทึก → validate ว่าชื่อขึ้นในตาราง
    """
    page = auth_page
    unique_name = f"QA-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    page.goto(POINT_BUDGET_URL, wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle", timeout=15000)
    page.wait_for_timeout(2000)

    page.get_by_role("button", name="เพิ่มพอยท์งบประมาณ").click()
    page.wait_for_timeout(1500)

    # ชื่อ + จำนวนพอยท์
    page.get_by_placeholder("ชื่องบประมาณ").fill(unique_name)
    page.wait_for_timeout(300)
    _fill_total_points(page)
    page.wait_for_timeout(300)

    # ระยะเวลา: เปิด picker → วันเริ่ม 17 เวลา 09:00 → วันสิ้นสุด 20 เวลา 18:00 → ตกลง
    print("  📅 เปิด Date Picker (คลิกช่องระยะเวลาการใช้งาน)...")
    _click_date_field(page)
    page.wait_for_timeout(1000)
    print("  📅 แท็บ วันเริ่มต้น...")
    try:
        page.get_by_role("tab", name="วันเริ่มต้น").click()
    except Exception:
        page.get_by_text("วันเริ่มต้น").first.click()
    page.wait_for_timeout(500)
    print("  📅 เลือกวันที่ 17...")
    page.get_by_text("17", exact=True).first.click()
    page.wait_for_timeout(500)
    # เวลาวันเริ่มต้น — ปล่อย default
    page.wait_for_timeout(600)
    print("  📅 แท็บ วันสิ้นสุด...")
    page.evaluate("""() => {
        const tabs = [...document.querySelectorAll('*')].filter(el => el.textContent?.trim() === 'วันสิ้นสุด');
        if (tabs[0]) tabs[0].click();
    }""")
    page.wait_for_timeout(500)
    print("  📅 เลือกวันที่ 20...")
    page.get_by_text("20", exact=True).first.click()
    page.wait_for_timeout(300)
    # เวลาวันสิ้นสุด — ปล่อย default
    print("  📅 กด ตกลง (ปิด Date Picker)...")
    page.get_by_role("button", name="ตกลง").click()
    page.wait_for_timeout(500)

    # เปิดใช้งาน → บันทึก
    try:
        switch = page.get_by_role("switch", name="เปิดใช้งาน")
        if switch.is_visible():
            if "Mui-checked" not in (switch.get_attribute("class") or ""):
                switch.click()
        else:
            page.get_by_text("เปิดใช้งาน").first.click()
    except Exception:
        page.get_by_text("เปิดใช้งาน").first.click()
    page.wait_for_timeout(300)
    print("  💾 กด บันทึก (ฟอร์ม)...")
    page.get_by_role("button", name="บันทึก").click()
    # รอ confirm popup ขึ้น แล้วกด บันทึก ใน popup
    print("  💾 รอ confirm popup...")
    dialog = page.get_by_role("dialog")
    dialog.wait_for(state="visible", timeout=10000)
    page.wait_for_timeout(500)
    print("  💾 กด บันทึก (ใน popup)...")
    dialog.get_by_role("button", name="บันทึก").click()
    page.wait_for_timeout(3000)

    # Validate: ชื่องบประมาณใหม่ต้องอยู่ในตาราง
    expect(page.get_by_text(unique_name)).to_be_visible(timeout=10000)
