from fastapi import FastAPI
from routers import sensor
from database.database import engine, Base
import models.models
Base.metadata.create_all(bind=engine)
app = FastAPI(title="IoT Data API")

app.include_router(sensor.router, prefix="/sensor")
