# Test Steps: test_add_budget_point (สร้างพอยท์งบประมาณ)

## Pre-condition
- มีไฟล์ `scripts/auth.json` (รัน `python generate_auth.py` ก่อนครั้งแรก)
- Browser เปิดแบบ headed (เห็นหน้าจอ)

---

## Steps

| # | Step | รายละเอียดในโค้ด |
|---|------|-------------------|
| 1 | ไปที่หน้า point-budget | `page.goto(POINT_BUDGET_URL)` |
| 2 | รอหน้าโหลด | `wait_for_load_state("networkidle")` + รอ 2 วินาที |
| 3 | คลิกปุ่ม "เพิ่มพอยท์งบประมาณ" | `get_by_role("button", name="เพิ่มพอยท์งบประมาณ").click()` |
| 4 | รอฟอร์มโหลด | รอ 1.5 วินาที |
| 5 | กรอก **ชื่องบประมาณ** | `get_by_placeholder("ชื่องบประมาณ").fill(unique_name)` → เช่น `QA-20260212-143052` |
| 6 | กรอก **จำนวนพอยท์ทั้งหมด** | `_fill_total_points(page)` → ค่า **5000** (ช่อง `placeholder="0.00"`) |
| 7 | คลิกช่อง **ระยะเวลาการใช้งาน** | `_click_date_field(page)` → เปิด Date Picker (`div[aria-haspopup="true"].cursor-pointer`) |
| 8 | รอ Date Picker เปิด | รอ 1 วินาที |
| 9 | เลือกแท็บ **วันเริ่มต้น** | `get_by_role("tab", name="วันเริ่มต้น")` หรือ `get_by_text("วันเริ่มต้น")` |
| 10 | เลือก **วันที่ 17** | `get_by_text("17", exact=True).first.click()` |
| 11 | กรอกเวลา **09:00** (วันเริ่มต้น) | `get_by_placeholder("00:00").first.fill("09:00")` (ถ้ามี) |
| 12 | รอ | รอ 600 ms |
| 13 | เลือกแท็บ **วันสิ้นสุด** | `page.evaluate`: หา element ที่ `textContent.trim() === 'วันสิ้นสุด'` แล้วคลิกตัวแรก |
| 14 | รอ | รอ 500 ms |
| 15 | เลือก **วันที่ 20** | `get_by_text("20", exact=True).first.click()` |
| 16 | กรอกเวลา **18:00** (วันสิ้นสุด) | `get_by_placeholder("00:00").nth(1).fill("18:00")` (ถ้ามี) |
| 17 | ปิด Date Picker | `get_by_role("button", name="ตกลง").click()` |
| 18 | รอ | รอ 500 ms |
| 19 | เปิด Toggle **เปิดใช้งาน** | หา switch "เปิดใช้งาน" → คลิกถ้ายังไม่ ON |
| 20 | คลิกปุ่ม **บันทึก** | `get_by_role("button", name="บันทึก").click()` |
| 21 | รอหลังบันทึก | รอ 3 วินาที |
| 22 | **Validate** | ตรวจว่า `unique_name` (ชื่องบประมาณที่สร้าง) **ปรากฏในตาราง** → `expect(page.get_by_text(unique_name)).to_be_visible()` |

---

## Test Data

| ฟิลด์ | ค่า |
|--------|-----|
| ชื่องบประมาณ | `QA-YYYYMMDD-HHMMSS` (จากเวลาตอนรัน) |
| จำนวนพอยท์ทั้งหมด | `5000` (ช่อง `placeholder="0.00"`) |
| วันเริ่มต้น | วันที่ **17** เวลา **09:00** |
| วันสิ้นสุด | วันที่ **20** เวลา **18:00** |
| สถานะการใช้งาน | **เปิดใช้งาน** (ON) |

---

## หมายเหตุ
- **จำนวนพอยท์:** ใช้ `input[placeholder="0.00"]` (ยืนยันจาก F12)
- **ช่องวันที่:** ใช้ `div[aria-haspopup="true"].cursor-pointer` ที่มีข้อความ "วว/ดด/ปปปป"
- **วันสิ้นสุด:** ใช้ JS ใน browser เหมือน F12 — `querySelectorAll('*')` filter `textContent.trim() === 'วันสิ้นสุด'` แล้วคลิกตัวแรก
