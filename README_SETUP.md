# การติดตั้งและใช้งาน STAF Automation Agent

## การติดตั้ง Dependencies

### 1. ติดตั้ง Python packages

```bash
cd /Users/socket9/Documents/STAF_Automation_Agent
pip3 install -r requirements.txt
```

### 2. ติดตั้ง Playwright browsers

หลังจากติดตั้ง playwright แล้ว ต้องติดตั้ง browsers ด้วย:

```bash
playwright install chromium
```

หรือติดตั้งทุก browsers:

```bash
playwright install
```

## การใช้งาน

### รัน test พื้นฐาน

```bash
pytest test_example.py -v
```

### รัน test พร้อมกำหนด base URL

```bash
pytest test_example.py --base-url=https://example.com -v
```

### รันแบบ headless

```bash
pytest test_example.py --headless -v
```

### รันพร้อม slow motion (เพื่อดูการทำงาน)

```bash
pytest test_example.py --slow-mo=500 -v
```

### รันทุก test files

```bash
pytest -v
```

## Features

- ✅ Auto Screenshot เมื่อ test fail (เก็บไว้ใน `screenshots/`)
- ✅ Microsoft 365 Persistent Context (ไม่ต้อง login ใหม่ทุกครั้ง)
- ✅ รองรับ command line arguments (`--base-url`, `--headless`, `--slow-mo`)

## Fixtures ที่พร้อมใช้งาน

- `page`: Page object พื้นฐาน
- `logged_in_page`: Page ที่ login แล้ว
- `base_url`: Base URL จาก command line
- `login_credentials`: Email และ password
