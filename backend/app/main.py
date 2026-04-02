from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import pickle
import os
from typing import List, Optional, Dict
import numpy as np

app = FastAPI(title="Real Estate Intelligence Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Model Paths
MODEL_DIR = os.path.join(BASE_DIR, "ml/models")
PRICE_MODEL_PATH = os.path.join(MODEL_DIR, "price_model.pkl")
CLUSTER_MODEL_PATH = os.path.join(MODEL_DIR, "cluster_model.pkl")

# Data Path
DATA_PATH = os.path.join(BASE_DIR, "data/processed/final_dataset.csv")

def load_data():
    if not os.path.exists(DATA_PATH):
        raise HTTPException(status_code=500, detail=f"Data file not found at {DATA_PATH}")
    return pd.read_csv(DATA_PATH)

def load_model(path):
    if not os.path.exists(path):
        raise HTTPException(status_code=500, detail=f"Model file not found at {path}")
    with open(path, 'rb') as f:
        return pickle.load(f)

# Request Models
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

class RecommendationRequest(BaseModel):
    budget: int
    location: str
    bedrooms: int
    amenities_min: int
    max_distance_metro: float

@app.get("/")
def read_root():
    return {"status": "online", "version": "2.0.0"}

@app.post("/predict")
def predict_price(req: PropertyRequest):
    try:
        model = load_model(PRICE_MODEL_PATH)
        features = [
            req.sqft, req.bedrooms, req.bathrooms, req.balconies, req.parking, req.age,
            req.floor, req.total_floors, req.furnished, req.amenities_count,
            req.distance_metro, req.distance_school, req.distance_hospital,
            req.location_encoded, req.age_bucket_encoded, req.luxury_score, req.roi
        ]
        prediction = model.predict([features])[0]
        
        # Calculate label
        # In a real app we'd compare to a baseline or user-provided actual if applicable
        return {
            "predicted_price": int(prediction),
            "price_range": [int(prediction * 0.95), int(prediction * 1.05)],
            "valuation_label": "Fair Market Value"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/undervalued")
def list_undervalued():
    df = load_data()
    # Logic: Real prediction gap (simulated using ROI > 20 as proxy for high growth gap)
    undervalued = df[df['roi'] > 22].sort_values(by='roi', ascending=False).head(15)
    return undervalued.to_dict('records')

@app.post("/recommend")
def recommend_properties(req: RecommendationRequest):
    df = load_data()
    # Filter based on user preferences
    matches = df[
        (df['price'] <= req.budget * 1.1) & 
        (df['location'].str.contains(req.location, case=False)) &
        (df['bedrooms'] >= req.bedrooms) &
        (df['amenities_count'] >= req.amenities_min) &
        (df['distance_metro'] <= req.max_distance_metro)
    ]
    
    # Calculate match score based on ROI and price proximity
    matches = matches.copy()
    matches['match_score'] = (1 - (abs(matches['price'] - req.budget) / req.budget)) * 50 + (matches['roi'] / 50) * 50
    matches['match_score'] = matches['match_score'].clip(0, 100).round(1)
    
    return matches.sort_values(by='match_score', ascending=False).head(5).to_dict('records')

@app.get("/clusters")
def get_clusters():
    df = load_data()
    summary = df.groupby('cluster_label').agg({
        'price': ['mean', 'min', 'max'],
        'property_id': 'count',
        'roi': 'mean'
    }).to_dict('index')
    return summary

@app.get("/market-stats")
def market_stats():
    df = load_data()
    return {
        "avg_price": int(df['price'].mean()),
        "total_properties": len(df),
        "best_roi_location": df.groupby('location')['roi'].mean().idxmax(),
        "undervalued_count": len(df[df['roi'] > 22]),
        "market_growth": "4.8%",
        "recommended_action": "Buy (Emerging Areas)"
    }

@app.get("/locations")
def get_locations():
    df = load_data()
    loc_stats = df.groupby('location').agg({
        'price': 'mean',
        'roi': 'mean',
        'market_trend': 'mean',
        'cluster_label': lambda x: x.mode()[0],
        'latitude': 'first',
        'longitude': 'first'
    }).reset_index()
    return loc_stats.to_dict('records')

@app.get("/trend")
def get_trend(location: str):
    df = load_data()
    loc_df = df[df['location'].str.contains(location, case=False)].sort_values('listing_date')
    return loc_df[['listing_date', 'price_per_sqft', 'price']].to_dict('records')

@app.get("/roi")
def get_roi_analysis(property_id: str):
    df = load_data()
    prop = df[df['property_id'] == property_id]
    if prop.empty:
        raise HTTPException(status_code=404, detail="Property not found")
    
    p = prop.iloc[0]
    return {
        "expected_roi": p['roi'],
        "appreciation_trend": "Rising" if p['market_trend'] > 1 else "Stable",
        "rental_yield": round(p['roi'] * 0.2, 2),
        "investment_score": round(p['luxury_score'] * 10, 1)
    }

@app.get("/sell-signal")
def get_sell_signal(property_id: str):
    df = load_data()
    prop = df[df['property_id'] == property_id]
    if prop.empty:
        raise HTTPException(status_code=404, detail="Property not found")
    
    p = prop.iloc[0]
    trend = p['market_trend']
    
    if trend > 1.2:
        return {"signal": "SELL", "explanation": "Market has reached peak valuation. High liquidation potential."}
    elif trend < 0.8:
        return {"signal": "BUY", "explanation": "Significant market dip found. Perfect entry point."}
    elif trend > 1.05:
        return {"signal": "HOLD", "explanation": "Steady appreciation continues. Wait for 15% further target."}
    else:
        return {"signal": "WAIT", "explanation": "Market consolidating. Neutral momentum."}
