# STAF Automation Agent

QA Automation สำหรับ STAF (ศรีตรัง) ด้วย Pytest + Playwright

## การติดตั้ง

```bash
pip install -r requirements.txt
playwright install chromium
```

## การใช้งาน

```bash
pytest playwright_microsoft_login.py -s -v
```

## Test Cases

- **test_login_with_username_password**: Login ด้วย username/password และเลือก dropdown "จัดการระบบศรีตรัง"
- **test_microsoft_365_button**: ทดสอบปุ่ม Microsoft 365 (xfail)
