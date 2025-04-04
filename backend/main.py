from fastapi import FastAPI
from routers import sensor
from database.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware
import models.models
Base.metadata.create_all(bind=engine)
app = FastAPI(title="IoT Data API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# get / hello world
@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(sensor.router, prefix="/sensor")
