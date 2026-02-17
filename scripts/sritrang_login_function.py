import pytest
import os
import json
from datetime import datetime
from playwright.sync_api import Page, expect

# --- CONFIGURATION ---
EMAIL = 'admin@socket9.com'
PASSWORD = 'admin@12345$'
SCREENSHOT_DIR = "screenshots"
BASE_URL = 'https://friendshop-qa.sritrang.socket9.com'

@pytest.fixture(scope="function", autouse=True)
def setup_teardown():
    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR)
    yield


def test_login_with_username_password(page: Page):
    """
    Test Case 1: ตรวจสอบการ Login ด้วย Username/Password และเลือกร้านค้า
    
    ขั้นตอนการทดสอบ:
    1. ไปยังหน้า Login
    2. คลิก dropdown "จัดการร้านค้าของฉัน" แล้วเลือก "จัดการระบบศรีตรัง" (option ที่สอง)
    3. กรอก email (admin@socket9.com)
    4. กรอกรหัสผ่าน (admin@12345$)
    5. คลิกปุ่ม "เข้าสู่ระบบ"
    6. ตรวจสอบว่า URL เปลี่ยนจากหน้า login หรือไม่
    
    Expected Result:
    - Login สำเร็จ และ URL เปลี่ยนจากหน้า login
    - สามารถเลือก dropdown "จัดการร้านค้าของฉัน" และเลือก "จัดการระบบศรีตรัง" ได้
    """
    
    status = "SUCCESS"
    reason = ""
    
    try:
        # ===== ขั้นตอนที่ 1: ไปยังหน้า Login =====
        print('\n🚀 ขั้นตอนที่ 1: กำลังไปยังหน้า login...')
        page.goto(f'{BASE_URL}/login', wait_until='domcontentloaded')
        
        # ===== ขั้นตอนที่ 2: คลิก dropdown "จัดการร้านค้าของฉัน" แล้วเลือก "จัดการระบบศรีตรัง" =====
        print('🏪 ขั้นตอนที่ 2: คลิก dropdown "จัดการร้านค้าของฉัน" แล้วเลือก "จัดการระบบศรีตรัง"...')
        
        # รอให้หน้าโหลดเสร็จและ element พร้อม
        page.wait_for_load_state('networkidle', timeout=10000)
        page.wait_for_timeout(2000)  # รอ 2 วินาทีเพื่อให้ dropdown พร้อม
        
        # 2.1: คลิก dropdown "จัดการร้านค้าของฉัน"
        print('  📌 2.1: กำลังคลิก dropdown "จัดการร้านค้าของฉัน"...')
        dropdown = page.get_by_text('จัดการร้านค้าของฉัน', exact=False)
        dropdown.wait_for(state='visible', timeout=2000)
        dropdown.click()
        print('  ✅ คลิก dropdown สำเร็จ')
        
        # 2.2: รอให้ dropdown menu เปิดขึ้นมา แล้วเลือก "จัดการระบบศรีตรัง"
        print('  ⏳ รอให้ dropdown menu เปิดขึ้นมา...')
        page.wait_for_timeout(2000)  # รอ 2 วินาที
        
        print('  📌 2.2: กำลังเลือก "จัดการระบบศรีตรัง"...')
        # หา option ที่มี text "จัดการระบบศรีตรัง"
        sritrang_option = page.locator('li.MuiMenuItem-root:has-text("จัดการระบบศรีตรัง")').first
        sritrang_option.wait_for(state='visible', timeout=2000)
        sritrang_option.click()
        print('  ✅ เลือก "จัดการระบบศรีตรัง" สำเร็จ')
        
        page.wait_for_timeout(1000)
        print('✅ ขั้นตอนที่ 2 สำเร็จ: คลิก dropdown "จัดการร้านค้าของฉัน" → เลือก "จัดการระบบศรีตรัง"')
        
        # ===== ขั้นตอนที่ 3: กรอกอีเมล =====
        print(f'📧 ขั้นตอนที่ 3: กำลังกรอกอีเมล: {EMAIL}')
        try:
            page.get_by_placeholder('อีเมล').fill(EMAIL)
        except:
            page.locator('input#\\:r3\\:').fill(EMAIL)
        
        page.wait_for_timeout(500)
        
        # ===== ขั้นตอนที่ 4: กรอกรหัสผ่าน =====
        print('🔑 ขั้นตอนที่ 4: กำลังกรอกรหัสผ่าน...')
        try:
            page.locator('input#\\:r4\\:').fill(PASSWORD)
        except:
            page.locator('input[type="password"]').fill(PASSWORD)
        
        page.wait_for_timeout(500)
        
        # ===== ขั้นตอนที่ 5: คลิกปุ่ม "เข้าสู่ระบบ" =====
        print('🔘 ขั้นตอนที่ 5: คลิกปุ่ม "เข้าสู่ระบบ"...')
        try:
            page.get_by_role('button', name='เข้าสู่ระบบ', exact=True).click()
        except:
            page.locator('button.MuiButton-contained:has-text("เข้าสู่ระบบ")').filter(
                lambda el: 'เข้าสู่ระบบผ่าน' not in el.inner_text()
            ).click()
        
        # ===== ขั้นตอนที่ 6: รอให้หน้าเปลี่ยนและตรวจสอบผลลัพธ์ =====
        page.wait_for_timeout(3000)
        
        # ตรวจสอบผลลัพธ์ - เช็คว่า URL เปลี่ยนจากหน้า login หรือไม่
        current_url = page.url
        print(f'📍 URL ปัจจุบัน: {current_url}')
        
        if "/login" not in current_url.lower():
            print('✅ Login สำเร็จ! URL เปลี่ยนจากหน้า login')
            status = "SUCCESS"
        else:
            raise Exception("LOGIN_FAILED: ระบบยังค้างอยู่ที่หน้า Login - URL ไม่เปลี่ยน")

    except Exception as e:
        status = "FAIL"
        reason = str(e)
        print(f'❌ Error: {reason}')
        
        # ถ่าย Screenshot หน้าปัจจุบันไว้ให้ AI Agent วิเคราะห์
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_path = os.path.join(SCREENSHOT_DIR, f'login_fail_{timestamp}.png')
        page.screenshot(path=screenshot_path, full_page=True)
        
        # --- JSON OUTPUT FOR N8N ---
        output = {
            "test_name": "Login with Username/Password",
            "status": status,
            "reason": reason,
            "screenshot": os.path.abspath(screenshot_path),
            "timestamp": datetime.now().isoformat()
        }
        print(f"\nN8N_DATA:{json.dumps(output)}")
        
        # สั่งให้ Pytest มาร์คว่า Fail
        pytest.fail(reason)


@pytest.mark.xfail(reason="ปุ่ม Microsoft 365 ยังอยู่ในระหว่างการพัฒนา - mark เป็น fail ไว้ก่อน")
def test_microsoft_365_button(page: Page):
    """
    Test Case 2: ตรวจสอบปุ่ม Microsoft 365
    - คลิกปุ่ม "เข้าสู่ระบบผ่าน Microsoft 365"
    - ดักจับ Popup ที่เปิดขึ้นมา
    - เช็คว่า Popup โหลดหน้ากรอกอีเมลหรือไม่
    """
    
    status = "SUCCESS"
    reason = ""
    
    try:
        # 1. ไปยังหน้า Login
        print('\n🚀 Test Case 2: กำลังไปยังหน้า login...')
        page.goto(f'{BASE_URL}/login', wait_until='domcontentloaded')
        
        # 2. คลิกปุ่ม Microsoft 365 และจัดการ Popup
        print('🖱 คลิกปุ่ม Microsoft 365 และรอ Popup...')
        
        # ดักจับ Popup ที่จะเปิดขึ้นมา
        with page.expect_popup() as popup_info:
            page.get_by_role('button', name='เข้าสู่ระบบผ่าน Microsoft 365').click()
        
        popup = popup_info.value
        
        # 💡 ดักจับอาการค้าง: ถ้าหน้า Popup ไม่โหลดช่อง Email ใน 10 วิ ให้ถือว่า Fail
        try:
            expect(popup.get_by_placeholder("อีเมล")).to_be_visible(timeout=10000)
            print('✅ Popup พร้อมใช้งาน - โหลดหน้ากรอกอีเมลสำเร็จ')
            status = "SUCCESS"
        except Exception:
            raise Exception("BUTTON_HANG: ปุ่ม Microsoft 365 ค้าง หรือ Popup ไม่โหลดหน้ากรอกอีเมล")

    except Exception as e:
        status = "FAIL"
        reason = str(e)
        print(f'❌ Error: {reason}')
        
        # ถ่าย Screenshot หน้าปัจจุบันไว้ให้ AI Agent วิเคราะห์
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_path = os.path.join(SCREENSHOT_DIR, f'ms365_button_fail_{timestamp}.png')
        page.screenshot(path=screenshot_path, full_page=True)
        
        # --- JSON OUTPUT FOR N8N ---
        output = {
            "test_name": "Microsoft 365 Button Test",
            "status": status,
            "reason": reason,
            "screenshot": os.path.abspath(screenshot_path),
            "timestamp": datetime.now().isoformat()
        }
        print(f"\nN8N_DATA:{json.dumps(output)}")
        
        # สั่งให้ Pytest มาร์คว่า Fail
        pytest.fail(reason)

if __name__ == '__main__':
    # สำหรับรันเทสสดๆ
    os.system("pytest scripts/sritrang_critical_function.py --html=qa_report.html --self-contained-html")
