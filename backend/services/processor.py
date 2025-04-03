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
        df[f"{col}_anomaly"] = abs(z) > 3  # ✅ True = ผิดปกติ

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
    """
    Fill missing data, interpolate, resample and smooth time-series.
    """
    df.set_index("timestamp", inplace=True)

    # Resample and fill missing with interpolate
    df = df.resample(resample_window).mean()
    df = df.interpolate(method="time")

    # Rolling average (smoothing)
    df["temperature_smooth"] = df["temperature"].rolling(3, min_periods=1).mean()
    df["humidity_smooth"] = df["humidity"].rolling(3, min_periods=1).mean()
    df["air_quality_smooth"] = df["air_quality"].rolling(3, min_periods=1).mean()

    df.reset_index(inplace=True)
    return df


def detect_anomalies_iqr(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect anomalies using IQR method. test
    """
    for col in ["temperature", "humidity", "air_quality"]:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        df[f"{col}_anomaly"] = ~df[col].between(q1 - 1.5 * iqr, q3 + 1.5 * iqr)
    return df


def prepare_visual_summary(df: pd.DataFrame):
    """
    Prepare visualization-ready data: stats, anomaly points, chart structure.
    """
    today = df["timestamp"].dt.date.max()
    df_today = df[df["timestamp"].dt.date == today]

    summary = {
        "today_summary": {
            "temperature": {
                "min": round(df_today["temperature"].min(), 2),
                "max": round(df_today["temperature"].max(), 2),
                "mean": round(df_today["temperature"].mean(), 2)
            },
            "humidity": {
                "min": round(df_today["humidity"].min(), 2),
                "max": round(df_today["humidity"].max(), 2),
                "mean": round(df_today["humidity"].mean(), 2)
            },
            "air_quality": {
                "min": round(df_today["air_quality"].min(), 2),
                "max": round(df_today["air_quality"].max(), 2),
                "mean": round(df_today["air_quality"].mean(), 2)
            }
        },
        "graph_data": df.to_dict(orient="records")
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