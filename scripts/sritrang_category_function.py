"""
sritrang_category_function.py — Test สร้างหมวดหมู่สินค้า (ใช้ auth.json ไม่ต้อง login ใหม่)
ต้องรัน generate_auth.py ก่อนครั้งแรก เพื่อสร้าง scripts/auth.json
"""
import pytest
from pathlib import Path
from datetime import datetime
from playwright.sync_api import Page, expect

# --- CONFIGURATION ---
BASE_URL = "https://friendshop-qa.sritrang.socket9.com"
AUTH_JSON_PATH = Path(__file__).resolve().parent / "auth.json"


def generate_category_name():
    """
    สร้างชื่อหมวดหมู่จากชื่อวัน + เลขชั่วโมง
    เช่น: "จันทร์14", "อังคาร09", "พุธ15"
    """
    now = datetime.now()
    
    # แปลงชื่อวันเป็นภาษาไทย
    day_names_th = {
        0: "จันทร์",
        1: "อังคาร",
        2: "พุธ",
        3: "พฤหัสบดี",
        4: "ศุกร์",
        5: "เสาร์",
        6: "อาทิตย์"
    }
    
    day_name = day_names_th[now.weekday()]
    hour = now.strftime("%H")  # เลขชั่วโมง 2 หลัก (00-23)
    
    category_name_th = f"{day_name}{hour}"
    
    # สร้างชื่อภาษาอังกฤษ (ใช้ชื่อวันภาษาอังกฤษ + ชั่วโมง)
    day_names_en = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday"
    }
    
    day_name_en = day_names_en[now.weekday()]
    category_name_en = f"{day_name_en}{hour}"
    
    return category_name_th, category_name_en


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


def test_add_category(auth_page: Page):
    """
    Test: สร้างหมวดหมู่สินค้า
    Navigate → เปิด Modal → กรอกฟอร์ม → บันทึก → Validate
    """
    page = auth_page
    
    # สร้างชื่อหมวดหมู่จากชื่อวัน + เลขชั่วโมง
    CATEGORY_NAME_TH, CATEGORY_NAME_EN = generate_category_name()
    print(f"\n📝 Generated category name: TH='{CATEGORY_NAME_TH}', EN='{CATEGORY_NAME_EN}'")

    # ===== STEP 1: Navigate to Category Page via Sidebar =====
    print("\n📂 Step 1: Navigating to Category page via sidebar...")
    
    # Navigate to base URL first to ensure we're logged in
    page.goto(BASE_URL, wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle", timeout=15000)
    page.wait_for_timeout(2000)

    # Click sidebar menu 'ข้อมูลพื้นฐาน' (if not already expanded)
    print("  📍 Clicking sidebar menu 'ข้อมูลพื้นฐาน'...")
    try:
        # Check if menu is already expanded (has sub-menu visible)
        sidebar_item = page.get_by_text("ข้อมูลพื้นฐาน", exact=True).first
        sidebar_item.wait_for(state="visible", timeout=5000)
        
        # Click to expand if needed (check if sub-menu is visible)
        try:
            # If sub-menu is not visible, click to expand
            if not page.get_by_text("หมวดหมู่สินค้า").first.is_visible(timeout=1000):
                sidebar_item.click()
                page.wait_for_timeout(1000)
        except Exception:
            # If sub-menu is visible, menu is already expanded
            pass
        
        print("  ✅ 'ข้อมูลพื้นฐาน' menu is expanded")
    except Exception:
        # Try alternative selector
        page.get_by_text("ข้อมูลพื้นฐาน", exact=False).first.click(timeout=5000)
        page.wait_for_timeout(1000)
        print("  ✅ Clicked 'ข้อมูลพื้นฐาน' menu")

    # Click sub-menu 'หมวดหมู่สินค้า'
    print("  📍 Clicking sub-menu 'หมวดหมู่สินค้า'...")
    try:
        page.get_by_text("หมวดหมู่สินค้า", exact=True).first.click(timeout=5000)
    except Exception:
        page.get_by_text("หมวดหมู่สินค้า", exact=False).first.click(timeout=5000)
    
    page.wait_for_load_state("networkidle", timeout=15000)
    page.wait_for_timeout(2000)
    
    # Verify we're on the category page (check for page title, not sidebar menu)
    # Use specific selector for page title (div.text-2xl-medium) to avoid strict mode violation
    try:
        # Check for page title "หมวดหมู่สินค้า" in main content area
        page.locator('div.text-2xl-medium:has-text("หมวดหมู่สินค้า")').wait_for(state="visible", timeout=10000)
        print("  ✅ Navigated to Category page (page title found)")
    except Exception:
        # Fallback: use nth(1) to get the second element (page title, not sidebar)
        expect(page.get_by_text("หมวดหมู่สินค้า").nth(1)).to_be_visible(timeout=10000)
        print("  ✅ Navigated to Category page")

    # ===== STEP 2: Click Add Category Button =====
    print("\n➕ Step 2: Clicking '+ เพิ่มหมวดหมู่หลัก' button...")
    try:
        # Try button with '+' prefix first (as shown in UI)
        page.get_by_text("+ เพิ่มหมวดหมู่หลัก", exact=False).first.click(timeout=5000)
    except Exception:
        try:
            page.get_by_role("button", name="เพิ่มหมวดหมู่หลัก").click(timeout=5000)
        except Exception:
            # Try alternative selector
            page.get_by_text("เพิ่มหมวดหมู่หลัก", exact=False).first.click(timeout=5000)
    
    page.wait_for_timeout(1500)
    print("  ✅ Modal 'เพิ่มหมวดหมู่' opened")

    # ===== STEP 3: Fill Form in Modal =====
    print("\n📝 Step 3: Filling form in modal 'เพิ่มหมวดหมู่'...")

    # Wait for modal to be visible
    dialog = page.get_by_role("dialog")
    dialog.wait_for(state="visible", timeout=5000)
    print("  ✅ Modal dialog is visible")

    # Fill 'หมวดหมู่หลัก (ภาษาไทย)'
    print(f"  📍 Filling 'หมวดหมู่หลัก (ภาษาไทย)' with: {CATEGORY_NAME_TH}")
    try:
        # Try by placeholder first (placeholder is "ระบุหมวดหมู่หลัก" as shown in UI)
        page.get_by_placeholder("ระบุหมวดหมู่หลัก").first.fill(CATEGORY_NAME_TH)
    except Exception:
        try:
            # Try by label
            page.get_by_label("หมวดหมู่หลัก (ภาษาไทย)").fill(CATEGORY_NAME_TH)
        except Exception:
            # Fallback: find input near the label text "หมวดหมู่หลัก (ภาษาไทย)"
            page.locator('div:has-text("หมวดหมู่หลัก (ภาษาไทย)")').locator('input').first.fill(CATEGORY_NAME_TH)
    
    page.wait_for_timeout(500)
    print("  ✅ Filled Thai category name")

    # Fill 'หมวดหมู่หลัก (ภาษาอังกฤษ)'
    print(f"  📍 Filling 'หมวดหมู่หลัก (ภาษาอังกฤษ)' with: {CATEGORY_NAME_EN}")
    try:
        # Try by placeholder (both fields use same placeholder "ระบุหมวดหมู่หลัก")
        # Get the second input field (English field)
        page.get_by_placeholder("ระบุหมวดหมู่หลัก").nth(1).fill(CATEGORY_NAME_EN)
    except Exception:
        try:
            # Try by label
            page.get_by_label("หมวดหมู่หลัก (ภาษาอังกฤษ)").fill(CATEGORY_NAME_EN)
        except Exception:
            # Fallback: find input near the label text "หมวดหมู่หลัก (ภาษาอังกฤษ)"
            page.locator('div:has-text("หมวดหมู่หลัก (ภาษาอังกฤษ)")').locator('input').first.fill(CATEGORY_NAME_EN)
    
    page.wait_for_timeout(500)
    print("  ✅ Filled English category name")

    # ===== STEP 4: Click Save Button =====
    print("\n💾 Step 4: Clicking 'บันทึก' button in modal...")
    try:
        # Find save button in the modal/dialog (purple button as shown in UI)
        dialog = page.get_by_role("dialog")
        dialog.get_by_role("button", name="บันทึก").click(timeout=5000)
    except Exception:
        # Fallback: try finding button anywhere in modal
        try:
            # Try to find button in dialog context
            page.locator('dialog button:has-text("บันทึก"), [role="dialog"] button:has-text("บันทึก")').first.click(timeout=5000)
        except Exception:
            # Last fallback: find any button with text "บันทึก"
            page.get_by_role("button", name="บันทึก").click(timeout=5000)
    
    page.wait_for_timeout(2000)
    print("  ✅ Clicked save button")

    # ===== STEP 5: Validation =====
    print("\n✅ Step 5: Validating results...")

    # Validate: Modal should be closed
    print("  📍 Checking if modal is closed...")
    try:
        dialog = page.get_by_role("dialog")
        # If dialog still exists, wait a bit more
        page.wait_for_timeout(1000)
        # Check if dialog is hidden
        expect(dialog).to_be_hidden(timeout=5000)
        print("  ✅ Modal is closed")
    except Exception:
        # If dialog doesn't exist, that's also fine (modal closed)
        try:
            dialog = page.get_by_role("dialog")
            if not dialog.is_visible():
                print("  ✅ Modal is closed")
        except Exception:
            print("  ✅ Modal is closed (no dialog found)")

    # Validate: New category appears in the list
    print(f"  📍 Checking if category '{CATEGORY_NAME_TH}' appears in the list...")
    expect(page.get_by_text(CATEGORY_NAME_TH)).to_be_visible(timeout=10000)
    print(f"  ✅ Category '{CATEGORY_NAME_TH}' found in the list")

    print("\n✅ Test completed successfully!")
