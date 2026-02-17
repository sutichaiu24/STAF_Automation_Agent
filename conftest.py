"""
conftest.py สำหรับ Pytest + Playwright
- ถ่าย Screenshot อัตโนมัติเมื่อ Test Case Fail
- จัดการ Microsoft 365 Session (Persistent Context)
- รองรับการรับค่า base_url ผ่าน command line argument
"""

import pytest
from playwright.sync_api import Playwright, Browser, BrowserContext, Page
import os
from datetime import datetime
from pathlib import Path


def pytest_addoption(parser):
    """เพิ่ม command line options สำหรับ pytest"""
    # เช็คว่า option มีอยู่แล้วหรือไม่ (จาก pytest-base-url plugin)
    try:
        parser.addoption(
            "--base-url",
            action="store",
            default="https://friendshop-qa.sritrang.socket9.com",
            help="Base URL สำหรับทดสอบ (default: https://friendshop-qa.sritrang.socket9.com)"
        )
    except ValueError:
        # Option มีอยู่แล้วจาก plugin อื่น (เช่น pytest-base-url)
        pass
    
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="รัน browser แบบ headless"
    )
    parser.addoption(
        "--slow-mo",
        action="store",
        type=int,
        default=0,
        help="ชะลอการทำงาน (milliseconds)"
    )


@pytest.fixture(scope="session")
def base_url(request):
    """Fixture สำหรับ base_url จาก command line argument"""
    # ใช้ base_url จาก pytest-base-url plugin ถ้ามี
    try:
        return request.config.getoption("--base-url")
    except ValueError:
        # ถ้าไม่มี option ให้ใช้ default
        return "https://friendshop-qa.sritrang.socket9.com"


@pytest.fixture(scope="session")
def headless(request):
    """Fixture สำหรับ headless mode จาก command line argument"""
    return request.config.getoption("--headless")


@pytest.fixture(scope="session")
def slow_mo(request):
    """Fixture สำหรับ slow_mo จาก command line argument"""
    return request.config.getoption("--slow-mo")


@pytest.fixture(scope="session")
def playwright() -> Playwright:
    """Fixture สำหรับ Playwright instance"""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as playwright_instance:
        yield playwright_instance


@pytest.fixture(scope="session")
def browser_type_launch_args(headless, slow_mo):
    """Fixture สำหรับ browser launch arguments"""
    return {
        "headless": headless,
        "slow_mo": slow_mo,
    }


@pytest.fixture(scope="session")
def browser_context_args():
    """Fixture สำหรับ browser context arguments"""
    return {
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="session")
def persistent_context_dir():
    """Fixture สำหรับ directory ของ persistent context"""
    context_dir = Path(__file__).parent / ".playwright" / "ms365_context"
    context_dir.mkdir(parents=True, exist_ok=True)
    return str(context_dir)


@pytest.fixture(scope="session")
def ms365_context(
    playwright: Playwright,
    browser_type_launch_args,
    browser_context_args,
    persistent_context_dir
) -> BrowserContext:
    """
    Fixture สำหรับ Microsoft 365 Persistent Context
    จะสร้าง context ที่ persist session เพื่อไม่ต้อง login ใหม่ทุกครั้ง
    """
    # ลองใช้ persistent context ที่มีอยู่แล้ว
    try:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=persistent_context_dir,
            **browser_type_launch_args,
            **browser_context_args
        )
        yield context
        context.close()
    except Exception as e:
        # ถ้าไม่สามารถใช้ persistent context ได้ ให้สร้างใหม่
        print(f"ไม่สามารถใช้ persistent context ได้: {e}")
        browser = playwright.chromium.launch(**browser_type_launch_args)
        context = browser.new_context(**browser_context_args)
        yield context
        context.close()
        browser.close()


@pytest.fixture(scope="function")
def page(ms365_context: BrowserContext, base_url: str) -> Page:
    """
    Fixture สำหรับ Page object
    ใช้ persistent context เพื่อรักษา session
    """
    page = ms365_context.new_page()
    page.set_default_timeout(30000)  # 30 seconds timeout
    
    yield page
    
    # ปิด page หลังจาก test เสร็จ
    page.close()


@pytest.fixture(scope="function", autouse=True)
def setup_screenshots_dir():
    """Fixture สำหรับสร้างโฟลเดอร์ screenshots ถ้ายังไม่มี"""
    screenshots_dir = Path(__file__).parent / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)
    return screenshots_dir


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook สำหรับถ่าย Screenshot อัตโนมัติเมื่อ Test Case Fail
    """
    # Execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()
    
    # ถ่าย screenshot เฉพาะเมื่อ test fail
    if rep.when == "call" and rep.failed:
        # ดึง page object จาก fixture
        if "page" in item.fixturenames:
            page = item.funcargs.get("page")
            if page:
                try:
                    # สร้างชื่อไฟล์ screenshot
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    test_name = item.name.replace(" ", "_").replace("::", "_")
                    screenshots_dir = Path(__file__).parent / "screenshots"
                    screenshot_path = screenshots_dir / f"FAILED_{test_name}_{timestamp}.png"
                    
                    # ถ่าย screenshot
                    page.screenshot(path=str(screenshot_path), full_page=True)
                    print(f"\n📸 Screenshot บันทึกไว้ที่: {screenshot_path}")
                except Exception as e:
                    print(f"\n⚠️  ไม่สามารถถ่าย screenshot ได้: {e}")


@pytest.fixture(scope="function")
def login_credentials():
    """Fixture สำหรับ login credentials"""
    return {
        "email": "admin@socket9.com",
        "password": "admin@12345$"
    }


@pytest.fixture(scope="function")
def logged_in_page(page: Page, base_url: str, login_credentials: dict):
    """
    Fixture สำหรับ page ที่ login แล้ว
    ใช้ persistent context เพื่อไม่ต้อง login ใหม่ทุกครั้ง
    """
    # ไปยังหน้า login
    login_url = f"{base_url}/login"
    page.goto(login_url, wait_until="networkidle")
    
    # เช็คว่า login แล้วหรือยัง (ถ้า URL ไม่ใช่ /login แสดงว่า login แล้ว)
    if "/login" not in page.url.lower():
        print("✅ ใช้ session ที่มีอยู่แล้ว (ไม่ต้อง login ใหม่)")
        return page
    
    # ถ้ายังไม่ได้ login ให้ทำการ login
    try:
        print("🔐 กำลัง login...")
        
        # คลิกปุ่ม Microsoft 365 (ถ้ามี)
        try:
            ms365_button = page.get_by_role('button', name='เข้าสู่ระบบผ่าน Microsoft 365', timeout=5000)
            if ms365_button.is_visible():
                ms365_button.click()
                page.wait_for_timeout(2000)
        except:
            pass  # ถ้าไม่มีปุ่ม Microsoft 365 ก็ข้าม
        
        # กรอก email
        try:
            page.get_by_placeholder('อีเมล').fill(login_credentials["email"])
        except:
            page.locator('input#\\:r3\\:').fill(login_credentials["email"])
        
        page.wait_for_timeout(500)
        
        # กรอก password
        try:
            page.locator('input#\\:r4\\:').fill(login_credentials["password"])
        except:
            page.locator('input[type="password"]').fill(login_credentials["password"])
        
        page.wait_for_timeout(500)
        
        # คลิกปุ่ม login
        page.get_by_role('button', name='เข้าสู่ระบบ').click()
        
        # รอให้ login เสร็จ
        page.wait_for_timeout(3000)
        
        # เช็คว่า login สำเร็จหรือไม่
        if "/login" not in page.url.lower():
            print("✅ Login สำเร็จ!")
        else:
            print("⚠️  อาจจะ login ไม่สำเร็จ ยังอยู่ที่หน้า login")
            
    except Exception as e:
        print(f"⚠️  เกิดข้อผิดพลาดในการ login: {e}")
    
    return page
