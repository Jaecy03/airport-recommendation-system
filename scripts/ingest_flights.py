import pandas as pd
import os
import requests
import logging
import threading
from datetime import datetime
from sqlalchemy import create_engine
from concurrent.futures import ThreadPoolExecutor
import time

API_KEY = os.getenv('AVIATION_STACK_API_KEY', 'your_api_key_here')
today = datetime.now().strftime('%Y-%m-%d')

raw_dir = 'raw_data'
processed_dir = 'processed_data'
os.makedirs(raw_dir, exist_ok=True)
os.makedirs(processed_dir, exist_ok=True)

files = [
    ('delhi_to_domestic', 'domestic_departure'),
    ('delhi_to_international', 'international_departure'),
    ('domestic_to_delhi', 'domestic_arrival'),
    ('international_to_delhi', 'international_arrival')
]

db_url = os.getenv('DATABASE_URL', "postgresql+psycopg2://username:password@localhost:5432/airport_db")
table_name = "flights"
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/ingestion.log"),
        logging.StreamHandler()
    ]
)
def log_time(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        logging.info(f"Starting: {func.__name__}")
        result = func(*args, **kwargs)
        end = round(time.time() - start, 2)
        logging.info(f"Completed: {func.__name__} in {end} seconds\n")
        return result
    return wrapper
@log_time
def fetch_flights_from_api(flight_type):
    base_url = 'http://api.aviationstack.com/v1/flights'
    params = {
        'access_key': API_KEY,
        'limit': 100,
    }

    if flight_type == 'delhi_to_domestic':
        params.update({'dep_iata': 'DEL', 'arr_country_iso2': 'IN'})
    elif flight_type == 'delhi_to_international':
        params.update({'dep_iata': 'DEL', 'arr_country_iso2': '!IN'})
    elif flight_type == 'domestic_to_delhi':
        params.update({'arr_iata': 'DEL', 'dep_country_iso2': 'IN'})
    elif flight_type == 'international_to_delhi':
        params.update({'arr_iata': 'DEL', 'dep_country_iso2': '!IN'})

    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        logging.error(f"API failed for {flight_type}")
        return

    data = response.json().get('data', [])
    records = [{
        'flight_date': f.get('flight_date'),
        'airline': f.get('airline', {}).get('name'),
        'flight_number': f.get('flight', {}).get('iata'),
        'departure_airport': f.get('departure', {}).get('airport'),
        'arrival_airport': f.get('arrival', {}).get('airport'),
        'departure_time': f.get('departure', {}).get('scheduled'),
        'arrival_time': f.get('arrival', {}).get('scheduled'),
        'status': f.get('flight_status'),
        'delay': f.get('departure', {}).get('delay')
    } for f in data]

    df = pd.DataFrame(records)
    out_path = os.path.join(raw_dir, f"{flight_type}_{today}.csv")
    df.to_csv(out_path, index=False)
    logging.info(f"Saved {len(df)} records to {out_path}")

@log_time
def daily_ingestion():
    all_data = []
    for fname, flight_type in files:
        path = os.path.join(raw_dir, f"{fname}_{today}.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
            df['flight_type'] = flight_type
            all_data.append(df)

    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df['flight_number'] = combined_df['flight_number'].fillna('Unknown')
        combined_df['departure_time'] = pd.to_datetime(combined_df['departure_time'], errors='coerce')
        combined_df['arrival_time'] = pd.to_datetime(combined_df['arrival_time'], errors='coerce')
        output_path = os.path.join(processed_dir, f"all_flights_{today}.csv")
        combined_df.to_csv(output_path, index=False)
        logging.info(f"Ingested and saved {len(combined_df)} rows to {output_path}")
    else:
        logging.warning("No input files found for today's ingestion.")

def load_chunk_to_postgres(chunk_df, engine):
    try:
        with engine.begin() as conn:
            chunk_df.to_sql(table_name, conn, if_exists='append', index=False)
    except Exception as e:
        logging.error(f"Failed to load chunk: {e}")

@log_time
def load_to_postgres(csv_file, db_url):
    if not os.path.exists(csv_file):
        logging.error(f"File not found: {csv_file}")
        return

    df = pd.read_csv(csv_file)
    logging.info(f"Loaded DataFrame with {len(df)} rows")

    engine = create_engine(db_url)
    chunk_size = 100
    chunks = [df[i:i+chunk_size] for i in range(0, len(df), chunk_size)]

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(load_chunk_to_postgres, chunk, engine) for chunk in chunks]
        for f in futures:
            f.result()  # wait for all

    logging.info(f"[✓] Loaded {len(df)} rows to PostgreSQL table '{table_name}'.")

def lookup_flight(flight_number):
    all_data = []
    for name, ftype in files:
        matches = [f for f in os.listdir(raw_dir) if f.startswith(name)]
        if matches:
            df = pd.read_csv(os.path.join(raw_dir, sorted(matches)[-1]))
            df['flight_type'] = ftype
            all_data.append(df)

    if not all_data:
        return {"status": "error", "message": "No flight data available."}

    combined = pd.concat(all_data, ignore_index=True)
    combined['flight_number'] = combined['flight_number'].astype(str).str.upper()
    result = combined[combined['flight_number'] == flight_number.upper()]

    if result.empty:
        return {"status": "error", "message": f"No flight found for '{flight_number}'."}

    return {
        "status": "success",
        "flights": [{
            "flight_number": row.get("flight_number", "Unknown"),
            "flight_type": row.get("flight_type", "Unknown"),
            "departure_airport": row.get("departure_airport", "N/A"),
            "arrival_airport": row.get("arrival_airport", "N/A"),
            "departure_time": row.get("departure_time", "N/A"),
            "arrival_time": row.get("arrival_time", "N/A"),
            "status": f"Delayed by {int(row['delay'])} mins" if pd.notna(row['delay']) and row['delay'] > 0 else "On Time"
        } for _, row in result.iterrows()]
    }
if __name__ == "__main__":

    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(lambda x: fetch_flights_from_api(x[0]), files)

    daily_ingestion()

    csv_path = os.path.join(processed_dir, f'all_flights_{today}.csv')
    load_to_postgres(csv_path, db_url)

    if input("Do you want to look up a flight? (y/n): ").strip().lower() == 'y':
        flight_no = input("Enter flight number (e.g., AI302): ").strip().upper()
        print(lookup_flight(flight_no))
