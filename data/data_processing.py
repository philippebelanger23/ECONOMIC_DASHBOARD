# data/data_processing.py
import pandas as pd
from data.data_fetcher import fetch_fred_data

def get_economic_data():
    df = fetch_fred_data()
    
    # Interpolate missing values in the raw data
    df = df.interpolate(method='linear', limit_direction='both')
    
    # Resample to monthly frequency, taking the mean for each month
    df = df.resample("ME").mean()
    
    # Calculate MoM%, QoQ%, and YoY% for each column
    for col in df.columns:
        df[f"{col} MoM (%)"] = df[col].pct_change(periods=1) * 100   # Month-over-Month (1 month)
        df[f"{col} QoQ (%)"] = df[col].pct_change(periods=3) * 100   # Quarter-over-Quarter (3 months)
        df[f"{col} YoY (%)"] = df[col].pct_change(periods=12) * 100  # Year-over-Year (12 months)
    
    # Drop rows where ALL columns are NA
    df = df.dropna(how='all')
    
    return df

if __name__ == "__main__":
    df = get_economic_data()
    print("✅ Data processed. Available columns:", df.columns)
    print("Data available from:", df.index.min(), "to", df.index.max())