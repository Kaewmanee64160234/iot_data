# 📊 ระบบแดชบอร์ดแสดงข้อมูลเซ็นเซอร์ (Sensor Data Dashboard)

ระบบแสดงผลและวิเคราะห์ข้อมูลจากเซ็นเซอร์แบบ Real-time หรืออัปโหลดผ่านไฟล์ `.csv`  
พัฒนาโดยใช้ **FastAPI (Python)** สำหรับฝั่ง Backend และ **Vue 3 + ApexCharts** สำหรับฝั่ง Frontend  
รองรับการเลือกช่วงเวลา แสดงค่าสถิติ และตรวจจับค่าผิดปกติ (Anomaly)

---

## ✅ คุณสมบัติหลัก (Features)

- 📥 อัปโหลดไฟล์ .csv เพื่อประมวลผลข้อมูลเซ็นเซอร์
- 🧼 ตรวจสอบและทำความสะอาดข้อมูล เช่น ค่าที่ขาดหาย (`NaN`), ค่าผิดช่วง, timestamp ไม่ถูกต้อง
- 📈 คำนวณค่าสถิติ เช่น ค่าต่ำสุด (min), สูงสุด (max), และค่าเฉลี่ย (mean)
- 🔍 ตรวจจับข้อมูลผิดปกติด้วย **Z-Score** และ **IQR (Interquartile Range)**
- 📊 แสดงผลกราฟเชิงเวลา พร้อมจุดแสดงค่า Anomaly และเส้นค่า Smooth

---

## 🧩 ฟังก์ชันหลักในระบบ Sensor Data Pipeline

### 🔹 `validate_and_ingest(df)`
- ตรวจสอบว่ามีคอลัมน์ `timestamp`, `temperature`, `humidity`, `air_quality` ครบหรือไม่
- แปลง `timestamp` เป็น datetime
- ลบแถวที่มีค่าว่าง
- กรองข้อมูลที่อยู่นอกช่วง:
  - temperature: `-30°C` ถึง `60°C`
  - humidity: `0%` ถึง `100%`
  - air_quality: `0` ถึง `500`

---

### 🔹 `clean_weather_data(df, resample_window="1H")`
- ตั้ง `timestamp` เป็น index
- Resample ข้อมูลตามช่วงเวลา เช่น `1 ชั่วโมง`
- เติมค่าที่ขาดหาย (`NaN`) ด้วยการ interpolate แบบ time-based
- คำนวณค่า smooth โดยใช้ rolling average (ค่าเฉลี่ยกลิ้ง 3 จุด):
  - `temperature_smooth`, `humidity_smooth`, `air_quality_smooth`

---

### 🔹 `detect_anomalies_iqr(df)`
- ตรวจจับค่า **ผิดปกติ** โดยใช้เทคนิค IQR:
  - คำนวณ Q1 (25%) และ Q3 (75%)
  - คำนวณ IQR = Q3 - Q1
  - กำหนดค่าที่อยู่นอก `Q1 - 1.5*IQR` และ `Q3 + 1.5*IQR` เป็น anomaly
- สร้างคอลัมน์ boolean สำหรับแต่ละตัวแปร:
  - `temperature_anomaly`, `humidity_anomaly`, `air_quality_anomaly`

---

### 🔹 `prepare_visual_summary(df, start_date, end_date)`
- กรองข้อมูลตามช่วงวันที่ที่เลือก (หรือใช้ทั้งหมดหากไม่ระบุ)
- คำนวณค่าสถิติ min, max, mean
- แปลง timestamp เป็น string สำหรับ frontend
- ส่งออกข้อมูลที่พร้อมสำหรับการแสดงกราฟ

---

### 🔹 `process_sensor_data_pipeline(df)`
- ฟังก์ชันหลักที่เรียกฟังก์ชันย่อยเรียงตามลำดับ:
  1. `validate_and_ingest()`
  2. `clean_weather_data()`
  3. `detect_anomalies_iqr()`
  4. `prepare_visual_summary()`

- ส่งออกข้อมูลที่มีทั้งสรุปสถิติ และข้อมูลพร้อมสำหรับกราฟ

---

## 🔌 API ที่เปิดให้ใช้งาน

| Method | Endpoint | คำอธิบาย |
|--------|----------|-----------|
| `POST` | `/sensor/data` | อัปโหลดไฟล์ `.csv` และประมวลผลข้อมูล |
| `GET`  | `/sensor/processed` | ดึงข้อมูลที่ผ่านการ clean + anomaly เพื่อแสดงกราฟ |
| `GET`  | `/sensor/aggregated` | สรุปข้อมูล (min / max / mean) จากข้อมูลที่ clean แล้ว |

สามารถดูเอกสาร API Swagger ได้ที่: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🖥️ Frontend

| URL | ฟังก์ชัน |
|-----|----------|
| `http://localhost:5173/` | แสดงข้อมูลล่าสุดของสภาพอากาศ |
| `http://localhost:5173/sensor` | หน้าแดชบอร์ดหลัก สำหรับอัปโหลดและแสดงกราฟข้อมูล |

---

## 📂 รูปแบบไฟล์ CSV ที่รองรับ

```csv
timestamp,temperature,humidity,air_quality
2025-01-01T08:00:00Z,28.5,55,120
2025-01-01T09:00:00Z,29.0,58,125
...
## 🛠️ วิธีติดตั้ง (Installation)

### 🔹 1. ติดตั้งแบบ **ไม่ใช้ Docker**

#### ✅ Backend (FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # หรือ venv\Scripts\activate บน Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### 🔹 2. ติดตั้ง **Frontend (Vue 3)**
#### ✅ ขั้นตอนการติดตั้ง
```bash
cd frontend
npm install
npm run dev
```

หลังจากรันคำสั่ง `npm run dev` ระบบจะเปิดหน้าเว็บอัตโนมัติที่ [http://localhost:5173/](http://localhost:5173/)
หากไม่เปิด ให้เข้าไปที่ URL นี้ด้วยตนเอง

