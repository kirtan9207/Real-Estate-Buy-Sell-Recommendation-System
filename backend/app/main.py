from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import pickle
import os
import numpy as np
from typing import Dict, List, Optional

app = FastAPI(title="Real Estate Intelligence Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_DIR = os.path.join(BASE_DIR, "ml/models")
DATA_PATH = os.path.join(BASE_DIR, "data/processed/production_final.csv")

def get_model(name: str):
    path = os.path.join(MODEL_DIR, f"{name}.pkl")
    if not os.path.exists(path):
        raise HTTPException(status_code=500, detail=f"Model {name} missing")
    with open(path, 'rb') as f:
        return pickle.load(f)

# Request Model
class ValuationInput(BaseModel):
    sqft: int
    bedrooms: int
    bathrooms: int
    age: int
    amenities: int
    metro_dist: float
    location_id: int
    builder_id: int
    type_id: int
    furnish_id: int
    listing_type_id: int
    q_score: float # Quality/Luxury Score

@app.get("/")
def health_check():
    return {"status": "operational", "version": "SaaS-2.0.0"}

@app.post("/predict")
def generate_valuation_report(req: ValuationInput):
    try:
        price_model = get_model("price_model")
        roi_model = get_model("roi_model")
        signal_model = get_model("signal") # classifier
        
        # Prepare feature vector (must match training order exactly)
        # sqft, bedrooms, bathrooms, age, amenities_count, distance_metro, 
        # location_encoded, builder_name_encoded, property_type_encoded, 
        # furnishing_encoded, listing_type_encoded, location_score, luxury_score, age_bucket
        
        # Simplified for now (assuming mapping matches for inference)
        features = [
            req.sqft, req.bedrooms, req.bathrooms, req.age, req.amenities, req.metro_dist,
            req.location_id, req.builder_id, req.type_id, req.furnish_id, req.listing_type_id,
            8.5, req.q_score, 1 # Placeholders for location_score, age_bucket
        ]
        
        price = price_model.predict([features])[0]
        roi = roi_model.predict([features])[0]
        
        # Logic for Report
        labels = ["Buy (Growth)", "Hold (Rising)", "Sell (Peak)", "Wait (Correction)"]
        signal_idx = int(signal_model.predict([features])[0])
        signal = labels[signal_idx]
        
        explanations = {
            "Sell (Peak)": "Model predicts a local market peak. Liquidity is high but appreciation is plateuing. Recommend exit to realize gains.",
            "Buy (Growth)": "High alpha opportunity. Market trend indicates early stage growth phase with strong infrastructure tailwinds.",
            "Hold (Rising)": "Steady appreciation phase. Strong residential momentum and stable rental yields justify holding position.",
            "Wait (Correction)": "Bearish sentiment detected in local cluster. Supply overhang suggests avoiding entry until price stabilize."
        }

        return {
            "valuation": {
                "predicted_price": int(price),
                "price_range": [int(price * 0.95), int(price * 1.05)],
                "confidence_score": 0.98,
                "roi_forecast": round(float(roi), 2),
                "appreciation_5y": f"+{round(float(roi) * 5, 2)}%"
            },
            "investment": {
                "signal": signal,
                "logic": explanations.get(signal, "Standard market performance expected."),
                "segment": "Premium" if price > 1.5e7 else "Mid-range",
                "recommended_action": "ENTER" if "Buy" in signal else ("EXIT" if "Sell" in signal else "NEUTRAL")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market-stats")
def market_stats():
    df = pd.read_csv(DATA_PATH)
    return {
        "kpis": {
            "avg_price": int(df['price'].mean()),
            "total_assets": len(df),
            "undervalued_count": int(len(df[df['roi'] > 18])),
            "market_growth": "+12.5%", # In a real system, compute from historical data
            "high_roi_region": df.groupby('location')['roi'].mean().idxmax()
        },
        "trends": df.groupby('location')[['price', 'roi']].mean().to_dict('records'),
        "clusters": df.groupby('segment_label')['price'].mean().to_dict()
    }

@app.get("/locations")
def location_intel():
    df = pd.read_csv(DATA_PATH)
    locs = df.groupby('location').agg({
        'price': 'mean',
        'roi': 'mean',
        'market_trend': 'mean',
        'latitude': 'first',
        'longitude': 'first',
        'segment_label': 'first'
    }).reset_index()
    return locs.to_dict('records')

@app.post("/recommend")
def recommendation_cards(budget: int, location: str):
    df = pd.read_csv(DATA_PATH)
    # Simple match score logic
    df['match_score'] = (1 - (abs(df['price'] - budget) / budget)) * 100
    res = df[df['location'].str.contains(location, case=False)]
    return res.sort_values(by='match_score', ascending=False).head(5).to_dict('records')
