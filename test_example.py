"""
ตัวอย่างการใช้งาน conftest.py สำหรับทดสอบ
"""

import pytest


def test_example_with_page(page, base_url):
    """ตัวอย่าง test ที่ใช้ page fixture"""
    # ไปยังหน้า login
    page.goto(f"{base_url}/login")
    
    # ทดสอบว่าหน้า login โหลดเสร็จ
    assert "login" in page.url.lower()
    print("✅ Test ผ่าน: หน้า login โหลดสำเร็จ")


def test_example_with_logged_in_page(logged_in_page, base_url):
    """ตัวอย่าง test ที่ใช้ logged_in_page fixture (login แล้ว)"""
    # ไปยังหน้าหลัก
    logged_in_page.goto(f"{base_url}")
    
    # ทดสอบว่าหน้าโหลดเสร็จ
    assert logged_in_page.url.startswith(base_url)
    print("✅ Test ผ่าน: หน้าโหลดสำเร็จ")


def test_example_fail_for_screenshot(page, base_url):
    """ตัวอย่าง test ที่ fail เพื่อทดสอบ auto screenshot"""
    page.goto(f"{base_url}/login")
    
    # Test ที่จะ fail เพื่อทดสอบ screenshot
    assert False, "Test นี้ fail เพื่อทดสอบ auto screenshot"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
