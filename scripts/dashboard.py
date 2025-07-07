import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

st.set_page_config(page_title="Airport Analytics Dashboard", layout="wide")
st.title("✈️ Airport Analytics Dashboard")

# ---------- Fix relative path ----------
processed_dir = os.path.join(os.path.dirname(__file__), "../processed_data")
processed_dir = os.path.abspath(processed_dir)

today = datetime.now().strftime("%Y-%m-%d")
today_file = os.path.join(processed_dir, f"all_flights_{today}.csv")


def get_latest_file():
    files = [f for f in os.listdir(processed_dir) if f.startswith("all_flights_") and f.endswith(".csv")]
    if not files:
        return None
    latest = sorted(files)[-1]
    return os.path.join(processed_dir, latest)

# Load data
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df['departure_time'] = pd.to_datetime(df['departure_time'], errors='coerce')
    df['arrival_time'] = pd.to_datetime(df['arrival_time'], errors='coerce')
    return df.dropna(subset=['departure_time', 'arrival_time'])

if os.path.exists(today_file):
    df = load_data(today_file)
    st.success(f"Loaded data for today ({today})")
else:
    fallback = get_latest_file()
    if fallback:
        df = load_data(fallback)
        st.warning(f"Today's file not found. Loaded latest: {os.path.basename(fallback)}")
    else:
        st.error("No data files found in processed_data/")
        st.stop()

# ---------- Sidebar Filters ----------
st.sidebar.header("Filters")
selected_type = st.sidebar.multiselect("Flight Type", options=df['flight_type'].unique(), default=df['flight_type'].unique())
df = df[df['flight_type'].isin(selected_type)]

# ---------- Most Delayed Flights ----------
st.subheader("🚨 Most Delayed Flights")
delayed_flights = df[df['delay'].notnull()].sort_values(by='delay', ascending=False).head(10)
st.dataframe(delayed_flights[['airline', 'flight_number', 'departure_airport', 'arrival_airport', 'delay']])

# -------- Airline Delay Trends --------
st.subheader("📉 Average Delay by Airline")
airline_delays = df[df['delay'].notnull()].groupby('airline')['delay'].mean().sort_values(ascending=False)
st.bar_chart(airline_delays)

# -------- Peak Arrival and Departure Hours --------
st.subheader("📈 Peak Arrival & Departure Hours")

df['dep_hour'] = df['departure_time'].dt.hour
df['arr_hour'] = df['arrival_time'].dt.hour

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Departures per Hour**")
    dep_count = df['dep_hour'].value_counts().sort_index()
    st.bar_chart(dep_count)

with col2:
    st.markdown("**Arrivals per Hour**")
    arr_count = df['arr_hour'].value_counts().sort_index()
    st.bar_chart(arr_count)
