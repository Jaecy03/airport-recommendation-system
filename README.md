# Airport Recommendation System

A comprehensive data pipeline and analytics system for airport flight data, designed to process real-time flight information and provide insights through interactive dashboards.

## 🚀 Project Overview

This project implements an end-to-end data pipeline that:
- Fetches real-time flight data from Aviation Stack API
- Processes and cleans multiple data sources
- Provides interactive analytics dashboard
- Supports both domestic and international flight tracking for Delhi (IGI) airport

## 📁 Project Structure

```
airport-recommendation-system/
├── Data/                          # Static datasets
│   ├── history_data.csv          # User purchase history at airport
│   ├── user_gps_data.csv         # User location tracking data
│   └── users_data.csv            # User demographic and preference data
├── scripts/                       # Core processing scripts
│   ├── igi_flight_data.py        # Flight data fetching from Aviation Stack API
│   ├── ingest_flights.py         # Data ingestion and processing pipeline
│   ├── preprocess.py             # Data preprocessing and cleaning
│   └── dashboard.py              # Streamlit analytics dashboard
├── raw_data/                      # Raw flight data from API
├── processed_data/                # Processed and consolidated flight data
├── preprocessed_data/             # Cleaned datasets (pickle format)
├── logs/                          # Application logs
└── requirements.txt               # Python dependencies
```

## 🛠 Features

### Data Collection
- **Real-time Flight Data**: Fetches live flight information using Aviation Stack API
- **Multi-route Coverage**: 
  - Delhi to Domestic destinations
  - Delhi to International destinations  
  - Domestic to Delhi arrivals
  - International to Delhi arrivals
- **Automated Data Pipeline**: Scheduled data collection and processing

### Data Processing
- **Data Ingestion**: Consolidates multiple raw data sources into unified format
- **Data Cleaning**: Handles missing values, data type conversions, and validation
- **Multi-threading**: Parallel processing for improved performance
- **Database Integration**: PostgreSQL support for data storage

### Analytics Dashboard
- **Interactive Visualizations**: Real-time flight statistics and trends
- **Flight Type Filtering**: Separate analysis for domestic/international flights
- **Performance Metrics**: Delay analysis, airline performance, route popularity
- **Responsive Design**: Web-based dashboard using Streamlit

## 📊 Data Sources

### Static Data
1. **Users Data** (100K+ records)
   - Demographics (age, gender, nationality)
   - Preferences (food, lounge, shopping, etc.)
   - Loyalty program status
   - Socio-economic classification

2. **GPS Data**
   - User location tracking
   - Timestamp and accuracy information
   - Movement patterns within airport

3. **Purchase History**
   - Transaction records at airport facilities
   - Category-wise spending patterns
   - Terminal and timing information

### Dynamic Data
- **Flight Information**: Real-time data from Aviation Stack API
- **Route Coverage**: 17+ domestic airports across India
- **Data Points**: Flight status, delays, airline info, schedules

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL (optional, for database storage)
- Aviation Stack API key

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/Jaecy03/airport-recommendation-system.git
   cd airport-recommendation-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   - Copy the example environment file: `cp .env.example .env`
   - Sign up at [Aviation Stack](https://aviationstack.com/) to get your API key
   - Update `.env` file with your API key and database credentials

5. **Setup Database (Optional)**
   - Install PostgreSQL
   - Update database URL in `scripts/ingest_flights.py`

## 🚀 Usage

### Data Collection
```bash
# Fetch latest flight data
python scripts/igi_flight_data.py

# Process and ingest data
python scripts/ingest_flights.py
```

### Data Preprocessing
```bash
# Clean and preprocess all datasets
python scripts/preprocess.py
```

### Launch Dashboard
```bash
# Start the analytics dashboard
streamlit run scripts/dashboard.py
```

## 📈 Dashboard Features

The interactive dashboard provides:
- **Flight Statistics**: Total flights, delays, on-time performance
- **Airline Analysis**: Performance comparison across carriers
- **Route Popularity**: Most frequent destinations and origins
- **Time-based Trends**: Peak hours and seasonal patterns
- **Real-time Updates**: Latest flight status and delays

## 🔄 Data Pipeline Workflow

1. **Data Fetching**: `igi_flight_data.py` collects raw flight data from API
2. **Data Ingestion**: `ingest_flights.py` processes and consolidates data
3. **Data Cleaning**: `preprocess.py` cleans and validates all datasets
4. **Visualization**: `dashboard.py` provides interactive analytics

## 📝 Logging & Monitoring

- Comprehensive logging system with file and console output
- Performance timing for all major operations
- Error handling and data validation
- Automated log rotation and management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Aviation Stack API](https://aviationstack.com/) for flight data
- [Streamlit](https://streamlit.io/) for dashboard framework
- [Pandas](https://pandas.pydata.org/) for data processing

## 📞 Contact

**Jahnavi Sharma** - [GitHub](https://github.com/Jaecy03)

Project Link: [https://github.com/Jaecy03/airport-recommendation-system](https://github.com/Jaecy03/airport-recommendation-system)
