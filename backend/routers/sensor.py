from io import StringIO
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.database import SessionLocal
from models.models import RawSensorData, VisualizedSensorData
from services.processor import prepare_visual_summary, process_sensor_data_pipeline
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.post("/data")
async def upload_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    df = pd.read_csv(StringIO(content.decode()))

    # savw raw_sensor_data
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp", "temperature", "humidity", "air_quality"])

    for _, row in df.iterrows():
        db.add(RawSensorData(
            timestamp=row["timestamp"],
            temperature=row["temperature"],
            humidity=row["humidity"],
            air_quality=row["air_quality"]
        ))
    db.commit()

  
    processed = process_sensor_data_pipeline(df)
    for record in processed["graph_data"]:
        db.add(VisualizedSensorData(**record))
    db.commit()
    return {"message": "Data uploaded and processed successfully"}


class SensorOutput(BaseModel):
    timestamp: datetime
    temperature: Optional[float]
    temperature_smooth: Optional[float]
    temperature_anomaly: Optional[bool]
    humidity: Optional[float]
    humidity_smooth: Optional[float]
    humidity_anomaly: Optional[bool]
    air_quality: Optional[float]
    air_quality_smooth: Optional[float]
    air_quality_anomaly: Optional[bool]

    class Config:
        orm_mode = True

@router.get("/processed", response_model=List[SensorOutput])
def get_visualized_data(
    db: Session = Depends(get_db),
    start_time: Optional[datetime] = Query(None, description="Start timestamp"),
    end_time: Optional[datetime] = Query(None, description="End timestamp"),
    metrics: List[str] = Query(default=[], description="Metrics to include (temperature, humidity, air_quality)"),
    smooth: bool = Query(True, description="Include smoothed values"),
    anomaly_only: bool = Query(False, description="Only include anomaly data"),
    latest_only: bool = Query(False, description="Only fetch the latest record"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max number of records to return")
):
    if start_time and end_time and end_time < start_time:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")

    query = db.query(VisualizedSensorData)

    if start_time:
        query = query.filter(VisualizedSensorData.timestamp >= start_time)
    if end_time:
        query = query.filter(VisualizedSensorData.timestamp <= end_time)

    if latest_only:
        data = query.order_by(VisualizedSensorData.timestamp.desc()).limit(1).all()
    else:
        data = query.order_by(VisualizedSensorData.timestamp.asc()).offset(skip).limit(limit).all()

    result = []
    for row in data:
        record = {"timestamp": row.timestamp}

        if not metrics or "temperature" in metrics:
            if not anomaly_only or row.temperature_anomaly:
                record["temperature"] = row.temperature
                if smooth:
                    record["temperature_smooth"] = row.temperature_smooth
                record["temperature_anomaly"] = row.temperature_anomaly

        if not metrics or "humidity" in metrics:
            if not anomaly_only or row.humidity_anomaly:
                record["humidity"] = row.humidity
                if smooth:
                    record["humidity_smooth"] = row.humidity_smooth
                record["humidity_anomaly"] = row.humidity_anomaly

        if not metrics or "air_quality" in metrics:
            if not anomaly_only or row.air_quality_anomaly:
                record["air_quality"] = row.air_quality
                if smooth:
                    record["air_quality_smooth"] = row.air_quality_smooth
                record["air_quality_anomaly"] = row.air_quality_anomaly

        if len(record) > 1:
            result.append(record)

    return result

# create a all data that clean save in db by make paginate
@router.get("/visualized")
def get_visualized_data_all(
    db: Session = Depends(get_db),
    start_time: Optional[datetime] = Query(None, description="Start timestamp"),
    end_time: Optional[datetime] = Query(None, description="End timestamp"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max number of records to return"),
    order: str = Query("asc", description="Order by timestamp: 'asc' or 'desc'")
):
    query = db.query(VisualizedSensorData)

    if start_time:
        query = query.filter(VisualizedSensorData.timestamp >= start_time)
    if end_time:
        query = query.filter(VisualizedSensorData.timestamp <= end_time)

    total = query.count()  # Get the total count of records

    if order == "desc":
        query = query.order_by(VisualizedSensorData.timestamp.desc())
    else:
        query = query.order_by(VisualizedSensorData.timestamp.asc())

    data = query.offset(skip).limit(limit).all()
    return {"total": total, "data": data}

@router.get("/7day-comparison")
def get_7day_comparison(db: Session = Depends(get_db)):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    query = db.query(VisualizedSensorData).filter(
        VisualizedSensorData.timestamp >= start_date,
        VisualizedSensorData.timestamp <= end_date
    ).order_by(VisualizedSensorData.timestamp.asc())

    data = query.all()

    # กลุ่มข้อมูลตามวัน
    grouped: Dict[str, List[Dict]] = {}

    for d in data:
        day_key = d.timestamp.strftime("%Y-%m-%d")
        hour = d.timestamp.hour

        if day_key not in grouped:
            grouped[day_key] = []

        grouped[day_key].append({
            "hour": hour,
            "temperature": d.temperature
        })

    # จัดรูปแบบให้เหมาะกับ ApexCharts
    result = []
    for day, values in grouped.items():
        result.append({
            "name": day,
            "data": sorted([{"x": v["hour"], "y": v["temperature"]} for v in values], key=lambda x: x["x"])
        })

    return result

@router.get("/aggregated")
def get_summary_statistics(
    db: Session = Depends(get_db),
    start_time: Optional[datetime] = Query(None, description="Start timestamp"),
    end_time: Optional[datetime] = Query(None, description="End timestamp"),
):
    query = db.query(VisualizedSensorData)
    if start_time:
        query = query.filter(VisualizedSensorData.timestamp >= start_time)
    if end_time:
        query = query.filter(VisualizedSensorData.timestamp <= end_time)

    data = query.all()
    if not data:
        return {
            "temperature": {"min": None, "max": None, "mean": None},
            "humidity": {"min": None, "max": None, "mean": None},
            "air_quality": {"min": None, "max": None, "mean": None},
        }

    df = pd.DataFrame([{
        "temperature": d.temperature,
        "humidity": d.humidity,
        "air_quality": d.air_quality
    } for d in data])

    def summary(series: pd.Series):
        return {
            "min": round(series.min(), 2),
            "max": round(series.max(), 2),
            "mean": round(series.mean(), 2)
        }

    return {
        "temperature": summary(df["temperature"]),
        "humidity": summary(df["humidity"]),
        "air_quality": summary(df["air_quality"])
    }

@router.get("/aggregated-insight")
def get_aggregated_insight(
    db: Session = Depends(get_db),
    window: str = Query("1h", description="Aggregation window (e.g., 10min, 1h, 1d)"),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
):
    query = db.query(VisualizedSensorData)

    if start_time:
        query = query.filter(VisualizedSensorData.timestamp >= start_time)
    if end_time:
        query = query.filter(VisualizedSensorData.timestamp <= end_time)

    data = query.all()
    if not data:
        return {"message": "No data found"}

    df = pd.DataFrame([{
        "timestamp": d.timestamp,
        "temperature": d.temperature,
        "humidity": d.humidity,
        "air_quality": d.air_quality,
    } for d in data])

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.set_index("timestamp", inplace=True)

    # Resample based on user input
    try:
        grouped = df.resample(window).agg(['min', 'max', 'mean', 'median'])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid window format: {window}")

    grouped.columns = ['_'.join(col).strip() for col in grouped.columns.values]
    grouped = grouped.reset_index()

    # Convert result to dictionary for JSON response
    return grouped.to_dict(orient="records")
