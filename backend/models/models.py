from sqlalchemy import Boolean, Column, Integer, Float, String, DateTime
from database.database import Base
from datetime import datetime

class RawSensorData(Base):
    __tablename__ = "raw_sensor_data"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime)
    temperature = Column(Float)
    humidity = Column(Float)
    air_quality = Column(Float)

class VisualizedSensorData(Base):
    __tablename__ = "visualized_sensor_data"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime)
    temperature = Column(Float)
    humidity = Column(Float)
    air_quality = Column(Float)
    temperature_smooth = Column(Float)
    humidity_smooth = Column(Float)
    air_quality_smooth = Column(Float)
    temperature_anomaly = Column(Boolean)
    humidity_anomaly = Column(Boolean)
    air_quality_anomaly = Column(Boolean)

# export SensorData as a module
__all__ = ["RawSensorData", "VisualizedSensorData"]

