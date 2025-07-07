import pandas as pd
import os
import time
from functools import wraps
from datetime import datetime, timedelta

DATA_DIR = "Data"
PROCESSED_DIR = "preprocessed_data"
os.makedirs(PROCESSED_DIR, exist_ok=True)

def log_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"[✓] {func.__name__} completed in {duration:.2f}s")
        return result
    return wrapper

@log_time
def preprocess_users():
    df = pd.read_csv(os.path.join(DATA_DIR, "users_data.csv"))
    df['preferences'] = df['preferences'].apply(lambda x: [p.strip() for p in x.replace('"', '').split(",")])
    df['socio_economic'] = df['socio_economic'].str.replace("'", "")
    df['loyalty'] = df['loyalty'].fillna("None")
    df['gender'] = df['gender'].astype('category')
    df.to_pickle(os.path.join(PROCESSED_DIR, "users_cleaned.pkl"))
    return df

@log_time
def preprocess_gps():
    df = pd.read_csv(os.path.join(DATA_DIR, "user_gps_data.csv"))
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df[df['accuracy'] <= 30]
    df.to_pickle(os.path.join(PROCESSED_DIR, "gps_cleaned.pkl"))
    return df

@log_time
def preprocess_history():
    df = pd.read_csv(os.path.join(DATA_DIR, "history_data.csv"))
    df['category'] = df['category'].str.replace("'", "")
    df['terminal'] = df['terminal'].str.replace("'", "")
    df['time_before_boarding'] = pd.to_timedelta(df['time_before_boarding'])
    df['amount_spent'] = pd.to_numeric(df['amount_spent'], errors='coerce')
    df.to_pickle(os.path.join(PROCESSED_DIR, "history_cleaned.pkl"))
    return df

@log_time
def preprocess_flights():
    today = datetime.now().strftime('%Y-%m-%d')
    path = os.path.join("processed_data", f"all_flights_{today}.csv")
    if not os.path.exists(path):
        print(f"[WARN] Today's flight data not found: {path}")
        return pd.DataFrame()

    df = pd.read_csv(path)
    df['departure_time'] = pd.to_datetime(df['departure_time'], errors='coerce')
    df['arrival_time'] = pd.to_datetime(df['arrival_time'], errors='coerce')
    df['delay'] = df['delay'].fillna(0).astype(float)
    df = df[df['flight_number'].notnull()]
    df['departure_airport'] = df['departure_airport'].str.strip()
    df['arrival_airport'] = df['arrival_airport'].str.strip()
    df['status'] = df['status'].astype('category')
    df = df[['flight_date', 'flight_number', 'departure_time', 'arrival_time', 'status', 'delay', 'flight_type']]
    df.to_pickle(os.path.join(PROCESSED_DIR, "flights_cleaned.pkl"))
    return df

if __name__ == "__main__":
    preprocess_users()
    preprocess_gps()
    preprocess_history()
    preprocess_flights()
