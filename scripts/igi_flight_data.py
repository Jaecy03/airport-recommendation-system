import requests
import csv
import os
from datetime import datetime

# Get API key from environment variable for security
API_KEY = os.getenv('AVIATION_STACK_API_KEY', 'your_api_key_here')
API_URL = 'http://api.aviationstack.com/v1/flights'
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

# List of Indian domestic IATA airport codes
domestic_airports = ['BOM', 'BLR', 'HYD', 'MAA', 'CCU', 'PNQ', 'GOI', 'AMD', 'SXR',
                     'IXC', 'IXJ', 'LKO', 'PAT', 'BHU', 'NAG', 'RAJ', 'DEL']

# Save CSV
def save_to_csv(flights, filename):
    if not flights:
        print(f"⚠️ No data for {filename}")
        return

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=flights[0].keys())
        writer.writeheader()
        writer.writerows(flights)

    print(f"Saved {len(flights)} rows to {filename}")


def extract_info(flight):
    return {
        'flight_date': flight.get('flight_date'),
        'airline': flight.get('airline', {}).get('name'),
        'flight_number': flight.get('flight', {}).get('iata'),
        'from': flight.get('departure', {}).get('airport'),
        'to': flight.get('arrival', {}).get('airport'),
        'departure_time': flight.get('departure', {}).get('scheduled'),
        'arrival_time': flight.get('arrival', {}).get('scheduled'),
        'status': flight.get('flight_status'),
        'delay_departure_minutes': flight.get('departure', {}).get('delay')
    }

def fetch_flights(params, filter_fn=None):
    response = requests.get(API_URL, params=params)
    if response.status_code != 200:
        print(f" API error: {response.status_code}")
        return []

    data = response.json().get('data', [])
    result = []

    for f in data:
        try:
            if filter_fn is None or filter_fn(f):
                result.append(extract_info(f))
        except Exception as e:
            print(f"Skipping due to error: {e}")

    return result


int_departures = fetch_flights(
    {'access_key': API_KEY, 'dep_iata': 'DEL', 'limit': 100},
    filter_fn=lambda f: f.get('arrival', {}).get('iata') not in domestic_airports
)
save_to_csv(int_departures, f'delhi_to_international_{timestamp}.csv')

dom_departures = fetch_flights(
    {'access_key': API_KEY, 'dep_iata': 'DEL', 'limit': 100},
    filter_fn=lambda f: f.get('arrival', {}).get('iata') in domestic_airports and f.get('arrival', {}).get('iata') != 'DEL'
)
save_to_csv(dom_departures, f'delhi_to_domestic_{timestamp}.csv')

int_arrivals = fetch_flights(
    {'access_key': API_KEY, 'arr_iata': 'DEL', 'limit': 100},
    filter_fn=lambda f: f.get('departure', {}).get('iata') not in domestic_airports
)
save_to_csv(int_arrivals, f'international_to_delhi_{timestamp}.csv')

dom_arrivals = fetch_flights(
    {'access_key': API_KEY, 'arr_iata': 'DEL', 'limit': 100},
    filter_fn=lambda f: f.get('departure', {}).get('iata') in domestic_airports and f.get('departure', {}).get('iata') != 'DEL'
)
save_to_csv(dom_arrivals, f'domestic_to_delhi_{timestamp}.csv')
