from io import StringIO
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Query, UploadFile
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


def get_chart_data(
    db: Session = Depends(get_db),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    resolution: str = Query("hourly", description="hourly or daily")
):
    query = db.query(VisualizedSensorData)
    if start_time:
        query = query.filter(VisualizedSensorData.timestamp >= start_time)
    if end_time:
        query = query.filter(VisualizedSensorData.timestamp <= end_time)

    data = query.order_by(VisualizedSensorData.timestamp.asc()).all()
    if not data:
        return {"graph": [], "anomalies": []}

    df = pd.DataFrame([{
        "timestamp": d.timestamp,
        "temperature": d.temperature,
        "humidity": d.humidity,
        "air_quality": d.air_quality,
        "anomaly": (
            d.temperature_anomaly or
            d.humidity_anomaly or
            d.air_quality_anomaly
        )
    } for d in data])

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["anomaly"] = df["anomaly"].astype(bool)

    df = df.set_index("timestamp")

    if resolution == "daily":
        resampled = df.resample("D").mean()
    else:
        resampled = df.resample("H").mean()

    resampled.replace([np.inf, -np.inf], np.nan, inplace=True)
    resampled = resampled.fillna(value=np.nan)
    resampled = resampled.where(pd.notnull(resampled), None)

    resampled = resampled.reset_index()

    anomaly_points = resampled[resampled["anomaly"] == True][["timestamp", "temperature"]]
    anomaly_points = anomaly_points.replace([np.inf, -np.inf], np.nan)
    anomaly_points = anomaly_points.where(pd.notnull(anomaly_points), None)

    return {
        "graph": resampled.to_dict(orient="records"),
        "anomalies": anomaly_points.to_dict(orient="records")
    }
