from io import StringIO
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Query, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.database import SessionLocal
from models.models import RawSensorData, VisualizedSensorData
from datetime import datetime, timedelta
import pandas as pd

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.post("/upload")
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

    # save visualized_sensor_data
    from services.processor import process_sensor_data_pipeline
    processed = process_sensor_data_pipeline(df)

    for record in processed["graph_data"]:
        db.add(VisualizedSensorData(**record))

    db.commit()
    return {"message": "Data uploaded and processed successfully"}


@router.get("/visualized")
def get_visualized_data(
    db: Session = Depends(get_db),
    start_time: Optional[datetime] = Query(None, description="Start timestamp"),
    end_time: Optional[datetime] = Query(None, description="End timestamp"),
    metrics: List[str] = Query(default=[], description="Metrics to include (temperature, humidity, air_quality)"),
    smooth: bool = Query(True, description="Include smoothed values"),
    anomaly_only: bool = Query(False, description="Only include anomaly data")
):

    # Base query
    query = db.query(VisualizedSensorData)

    if start_time:
        query = query.filter(VisualizedSensorData.timestamp >= start_time)
    if end_time:
        query = query.filter(VisualizedSensorData.timestamp <= end_time)

    data = query.order_by(VisualizedSensorData.timestamp.asc()).all()

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

        # Add only if at least one metric is included
        if len(record) > 1:
            result.append(record)

    return result
