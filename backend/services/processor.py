from datetime import date
import pandas as pd
import numpy as np

def process_clean_and_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    # delete duplicated 
    df = df.drop_duplicates()

    # delete NaN value
    df = df.dropna(subset=["temperature", "humidity", "air_quality"])

    # anomaly z-score
    for col in ["temperature", "humidity", "air_quality"]:
        z = (df[col] - df[col].mean()) / df[col].std()
        df[f"{col}_anomaly"] = abs(z) > 3 

    return df


def validate_and_ingest(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate schema and filter sensor data from CSV/JSON/stream source.
    """
    required_columns = ["timestamp", "temperature", "humidity", "air_quality"]
    df = df[[col for col in required_columns if col in df.columns]]

    # Validate timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Drop invalid or missing values
    df = df.dropna(subset=required_columns)

    # Filter valid ranges
    df = df[
        df["temperature"].between(-30, 60) &
        df["humidity"].between(0, 100) &
        df["air_quality"].between(0, 500)
    ]

    return df


def clean_weather_data(df: pd.DataFrame, resample_window: str = "1H") -> pd.DataFrame:

    # Fill missing value

    df.set_index("timestamp", inplace=True)

    # Resample and fill missing with interpolate
    df = df.resample(resample_window).mean()
    df = df.interpolate(method="time")

    # Rolling average 
    df["temperature_smooth"] = df["temperature"].rolling(3, min_periods=1).mean()
    df["humidity_smooth"] = df["humidity"].rolling(3, min_periods=1).mean()
    df["air_quality_smooth"] = df["air_quality"].rolling(3, min_periods=1).mean()

    df.reset_index(inplace=True)
    return df


def detect_anomalies_iqr(df: pd.DataFrame) -> pd.DataFrame:
    #  IQR method
    for col in ["temperature", "humidity", "air_quality"]:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        df[f"{col}_anomaly"] = ~df[col].between(q1 - 1.5 * iqr, q3 + 1.5 * iqr)
    return df

def prepare_visual_summary(df: pd.DataFrame, start_date: date = None, end_date: date = None):
    """
    Prepare visualization-ready data with summary and graph-ready records.
    """
    df = df.copy()

    # ✅ ใช้ช่วงเวลาทั้งหมดถ้าไม่ระบุช่วงเวลา
    if start_date is None or end_date is None:
        start_date = df["timestamp"].dt.date.min()
        end_date = df["timestamp"].dt.date.max()

    # Filter date range
    mask = (df["timestamp"].dt.date >= start_date) & (df["timestamp"].dt.date <= end_date)
    df_range = df[mask]

    # Convert timestamp to string for front-end (ISO format)
    df_range["timestamp"] = df_range["timestamp"].astype(str)

    summary = {
        "date_range": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "summary": {
            "temperature": {
                "min": round(df_range["temperature"].min(), 2),
                "max": round(df_range["temperature"].max(), 2),
                "mean": round(df_range["temperature"].mean(), 2)
            },
            "humidity": {
                "min": round(df_range["humidity"].min(), 2),
                "max": round(df_range["humidity"].max(), 2),
                "mean": round(df_range["humidity"].mean(), 2)
            },
            "air_quality": {
                "min": round(df_range["air_quality"].min(), 2),
                "max": round(df_range["air_quality"].max(), 2),
                "mean": round(df_range["air_quality"].mean(), 2)
            }
        },
        "graph_data": df_range.to_dict(orient="records")
    }
    return summary

def process_sensor_data_pipeline(df: pd.DataFrame, resample_window: str = "1H") -> dict:
    """
    Main function to clean, detect anomaly, and prepare for visualization.
    Can be used for CSV upload or IoT streaming.
    """
    df = validate_and_ingest(df)
    df = clean_weather_data(df, resample_window)
    df = detect_anomalies_iqr(df)
    summary = prepare_visual_summary(df)
    return summary