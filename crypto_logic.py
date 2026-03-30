import pandas as pd
import numpy as np
import datetime

def load_and_clean_data(filepath="crypto.csv"):
    df = pd.read_csv(filepath)
    # Clean Data
    df['Date'] = pd.to_datetime(df['Date'], format='mixed', dayfirst=True, errors='coerce')
    cols = ["Price", "Open", "High", "Low"]
    for col in cols:
        df[col] = df[col].astype(str).str.replace(",", "", regex=False).astype(float)
    
    df['Change %'] = df['Change %'].astype(str).str.replace('%', '', regex=False).astype(float)
    
    def convert_volume(v):
        v = str(v)
        if "K" in v: return float(v.replace("K","")) * 1e3
        elif "M" in v: return float(v.replace("M","")) * 1e6
        elif "B" in v: return float(v.replace("B","")) * 1e9
        else: return float(v)
        
    df["Vol."] = df["Vol."].apply(convert_volume)
    df["Volatility"] = df["High"] - df["Low"]
    # Drop rows where Date is NaT to prevent serialization errors
    df = df.dropna(subset=['Date'])
    return df

def get_dashboard_data(filepath="crypto.csv"):
    df = load_and_clean_data(filepath)
    
    # 1. Price trend
    price_trend = {}
    for name in df['Name'].unique():
        crypto = df[df['Name'] == name].sort_values(by='Date')
        price_trend[name] = {
            'dates': crypto['Date'].dt.strftime('%Y-%m-%d').tolist(),
            'prices': crypto['Price'].tolist()
        }
    
    # 2. Risk comparison (Volatility)
    risk_data = df.groupby('Name')['Volatility'].apply(list).to_dict()
    
    # 3. Average Daily Returns
    avg_returns = df.groupby('Name')['Change %'].mean().to_dict()
    
    # 4. Price vs Volume
    price_vol = {}
    for name in df['Name'].unique():
        crypto = df[df['Name'] == name]
        price_vol[name] = {
            'volumes': crypto['Vol.'].tolist(),
            'prices': crypto['Price'].tolist()
        }
        
    return {
        'price_trend': price_trend,
        'risk_data': risk_data,
        'avg_returns': avg_returns,
        'price_vol': price_vol
    }

def calculate_portfolio(total_investment, filepath="crypto.csv"):
    df = load_and_clean_data(filepath)
    
    summary = df.groupby("Name").agg(
        Avg_Return=("Change %","mean"),
        Avg_Risk=("Volatility","mean"),
        Avg_Price=("Price","mean"),
        Avg_Volume=("Vol.","mean")
    ).reset_index()
    
    # Avoid division by zero if all values are same
    return_range = summary["Avg_Return"].max() - summary["Avg_Return"].min()
    risk_range = summary["Avg_Risk"].max() - summary["Avg_Risk"].min()
    
    summary["Return_Score"] = (summary["Avg_Return"] - summary["Avg_Return"].min()) / (return_range if return_range > 0 else 1)
    summary["Risk_Score"] = (summary["Avg_Risk"] - summary["Avg_Risk"].min()) / (risk_range if risk_range > 0 else 1)
    summary["Final_Score"] = summary["Return_Score"] - summary["Risk_Score"]
    
    weights = summary["Final_Score"] - summary["Final_Score"].min() + 0.01
    weights = weights / weights.sum()
    summary["Weight"] = weights
    
    summary["Investment"] = summary["Weight"] * total_investment
    summary["Coins_to_Buy"] = summary["Investment"] / summary["Avg_Price"]
    summary["Equal_Investment"] = total_investment / len(summary)
    
    summary = summary.sort_values(by="Final_Score", ascending=False)
    
    best_crypto = summary.iloc[0]["Name"]
    best_investment = float(summary.iloc[0]["Investment"])
    
    return {
        'portfolio': summary.to_dict(orient='records'),
        'best_crypto': best_crypto,
        'best_investment': best_investment,
        'labels': summary["Name"].tolist(),
        'investments': summary["Investment"].tolist(),
        'equal_investments': summary["Equal_Investment"].tolist()
    }
