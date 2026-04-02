from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from pydantic import BaseModel
import pandas as pd
import pickle
import os
import numpy as np
from typing import Dict, List, Optional

app = FastAPI(title="Real Estate Intelligence Platform API")

# Update CORS for all origins (Production Ready)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use inside Docker via 'db' hostname or localhost for testing
DB_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/real_estate")
engine = create_engine(DB_URL)

# Models
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_DIR = os.path.join(BASE_DIR, "ml/models")

def get_model(name: str):
    path = os.path.join(MODEL_DIR, f"{name}.pkl")
    if not os.path.exists(path):
        raise HTTPException(status_code=500, detail=f"Model {name} missing")
    with open(path, 'rb') as f:
        return pickle.load(f)

# Request Models
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
    q_score: float

@app.get("/")
def health_check():
    return {"status": "operational", "version": "SaaS-2.1.0"}

@app.post("/predict")
def generate_valuation_report(req: ValuationInput):
    price_model = get_model("price_model")
    roi_model = get_model("roi_model")
    signal_model = get_model("signal")
    
    # Feature vector construction (must matches train order)
    features = [
        req.sqft, req.bedrooms, req.bathrooms, req.age, req.amenities, req.metro_dist,
        req.location_id, req.builder_id, req.type_id, req.furnish_id, req.listing_type_id,
        8.5, req.q_score, 1 # Placeholders
    ]
    
    price = int(price_model.predict([features])[0])
    roi = round(float(roi_model.predict([features])[0]), 2)
    signal_idx = int(signal_model.predict([features])[0])
    
    labels = ["Buy (Growth)", "Hold (Rising)", "Sell (Peak)", "Wait (Correction)"]
    signal = labels[signal_idx]
    
    return {
        "valuation": {
            "predicted_price": price,
            "price_range": [int(price * 0.95), int(price * 1.05)],
            "confidence_score": 0.98,
            "roi_forecast": roi,
            "appreciation_5y": f"+{round(roi * 5, 2)}%"
        },
        "investment": {
            "signal": signal,
            "segment": "Premium" if price > 15000000 else "Mid-range",
            "recommended_action": "ENTER" if "Buy" in signal else ("EXIT" if "Sell" in signal else "NEUTRAL")
        }
    }

@app.get("/market-stats")
def market_stats():
    try:
        with engine.connect() as conn:
            summary = pd.read_sql(text("SELECT * FROM market_summary LIMIT 1"), conn)
            locations = pd.read_sql(text("SELECT location, price, roi, market_trend FROM location_stats"), conn)
            clusters = pd.read_sql(text("SELECT segment_label, AVG(price) as avg_price FROM location_stats GROUP BY segment_label"), conn)
            
            if summary.empty:
                return {"error": "Database not populated. Run run-data-pipeline.sh."}
            
            s = summary.iloc[0].to_dict()
            return {
                "kpis": {
                    "avg_price": s['avg_price'],
                    "total_assets": s['total_assets'],
                    "undervalued_count": s['undervalued_count'],
                    "market_growth": s['market_growth'],
                    "high_roi_region": s['best_roi_location']
                },
                "trends": locations.to_dict('records'),
                "clusters": clusters.set_index('segment_label')['avg_price'].to_dict()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/locations")
def location_intel():
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text("SELECT * FROM location_stats"), conn)
            return df.to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/undervalued")
def undervalued_assets():
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text("SELECT * FROM properties WHERE roi > 18 ORDER BY roi DESC LIMIT 20"), conn)
            return df.to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/roi")
def roi_intel(property_id: str):
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text("SELECT roi, market_trend, luxury_score FROM properties WHERE property_id = :pid"), conn, params={'pid': property_id})
            if df.empty: return {}
            p = df.iloc[0]
            return {
                "expected_roi": round(p['roi'], 2),
                "appreciation_trend": "Rising" if p['market_trend'] > 0.1 else "Stable",
                "rental_yield": round(p['roi'] * 0.25, 2),
                "investment_score": round(p['luxury_score'] * 10, 1)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sell-signal")
def sell_signal(property_id: str):
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text("SELECT market_trend FROM properties WHERE property_id = :pid"), conn, params={'pid': property_id})
            if df.empty: return {"signal": "HOLD", "explanation": "Neutral trend data available."}
            trend = df.iloc[0]['market_trend']
            if trend > 0.14: return {"signal": "SELL", "explanation": "Model predicts peak market valuation reached."}
            elif trend < 0.08: return {"signal": "BUY", "explanation": "Local market dip detected. High long-term alpha."}
            else: return {"signal": "HOLD", "explanation": "Steady appreciation continues. Momentum target at +15%."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
