from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel
import pandas as pd
import pickle
import os
from typing import List, Optional
import numpy as np

app = FastAPI(title="Real Estate Intelligence Platform")

# Model Paths
MODEL_DIR = os.path.join(os.path.dirname(__file__), "../../../ml/models")
PRICE_MODEL_PATH = os.path.join(MODEL_DIR, "price_model.pkl")
CLUSTER_MODEL_PATH = os.path.join(MODEL_DIR, "cluster_model.pkl")

# Data Path for fallback if DB is not used
DATA_PATH = os.path.join(os.path.dirname(__file__), "../../../data/processed/final_dataset.csv")

def load_data():
    return pd.read_csv(DATA_PATH)

def load_model(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

# Request Model
class PropertyRequest(BaseModel):
    sqft: int
    bedrooms: int
    bathrooms: int
    balconies: int
    parking: int
    age: int
    floor: int
    total_floors: int
    furnished: int
    amenities_count: int
    distance_metro: float
    distance_school: float
    distance_hospital: float
    location_encoded: int
    age_bucket_encoded: int
    luxury_score: float
    roi: float

@app.get("/")
def read_root():
    return {"message": "Real Estate Recommender API is Live"}

@app.post("/predict")
def predict_price(req: PropertyRequest):
    try:
        model = load_model(PRICE_MODEL_PATH)
        # Prepare input
        features = list(req.dict().values())
        prediction = model.predict([features])[0]
        return {"predicted_price": int(prediction)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/undervalued")
def list_undervalued():
    df = load_data()
    # Assuming we have predictions already or we calculate it on the fly
    # Simple logic: If predicted > actual * 1.1, recommend buy
    # Since we need to predict for all, I'll just use a pre-calculated column if it exists 
    # Or simulate it for this demo.
    undervalued = df[df['roi'] > 25].head(10) # ROI as proxy for now
    return undervalued.to_dict('records')

@app.post("/recommend")
def recommend_properties(budget: int, location: str, bedrooms: int):
    df = load_data()
    # Content based filtering (Simple budget + location match)
    matches = df[
        (df['price'] <= budget * 1.1) & 
        (df['location'].str.contains(location, case=False)) &
        (df['bedrooms'] >= bedrooms)
    ].sort_values(by=['roi'], ascending=False).head(5)
    
    return matches.to_dict('records')

@app.get("/clusters")
def get_clusters():
    df = load_data()
    summary = df.groupby('cluster_label')['price'].agg(['mean', 'count']).to_dict('index')
    return summary

@app.get("/trend")
def get_trend(location: str):
    df = load_data()
    loc_df = df[df['location'].str.contains(location, case=False)].sort_values('listing_date')
    return loc_df[['listing_date', 'price_per_sqft']].to_dict('records')

@app.get("/sell-signal")
def get_sell_signal(property_id: str):
    df = load_data()
    prop = df[df['property_id'] == property_id]
    if prop.empty:
        return {"signal": "Property not found"}
    
    trend = prop['market_trend'].values[0]
    avg_trend = df[df['location'] == prop['location'].values[0]]['market_trend'].mean()
    
    if trend > avg_trend * 1.15:
        return {"signal": "SELL", "reason": "Market peaked, high market value reached"}
    elif trend < avg_trend * 0.85:
        return {"signal": "BUY", "reason": "Property undervalued, market dip found"}
    else:
        return {"signal": "HOLD", "reason": "Stable prices, wait for appreciation"}
