from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import pickle
import os
import numpy as np
from typing import Dict, List, Optional

app = FastAPI(title="Bangalore Real Estate Intelligence Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── File paths (CSV-based, no DB required) ──────────────
BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "data/processed/production_final.csv")
MODEL_DIR = os.path.join(BASE_DIR, "ml/models")


def load_data():
    """Load production data (CSV fallback — no database needed)."""
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    raise HTTPException(
        status_code=500, detail="Data not found. Run python run_pipeline.py first.")


def get_model(name: str):
    path = os.path.join(MODEL_DIR, f"{name}.pkl")
    if not os.path.exists(path):
        raise HTTPException(
            status_code=500, detail=f"Model {name} not found. Run pipeline first.")
    with open(path, 'rb') as f:
        return pickle.load(f)


class ValuationInput(BaseModel):
    sqft: int
    bedrooms: int
    bathrooms: int
    balconies: int = 1
    parking: int = 1
    age: int = 3
    floor: int = 5
    total_floors: int = 15
    amenities: int = 8
    distance_metro: float = 2.0
    distance_school: float = 1.5
    distance_hospital: float = 2.0
    distance_cbd: float = 10.0
    location: str = "Whitefield"
    property_type: str = "Apartment"
    furnishing: str = "Semi-furnished"
    listing_type: str = "Ready to Move"


@app.get("/")
def health_check():
    return {"status": "operational", "version": "3.0.0", "city": "Bangalore"}


@app.post("/predict")
def predict_price(req: ValuationInput):
    model = get_model("price_model")
    encoders = get_model("encoders")

    # Compute derived features
    connectivity = max(1.0, 10.0 - (req.distance_metro *
                       0.4 + req.distance_cbd * 0.15))
    loc_score = connectivity * 0.4 + 7 * 0.3 + 7 * 0.3
    amenity_idx = req.amenities / 20.0
    furnish_map = {'Unfurnished': 0, 'Semi-furnished': 1, 'Fully-furnished': 2}
    furnish_num = furnish_map.get(req.furnishing, 1)
    luxury = ((req.sqft / 5000) * 0.3 + (req.amenities / 20) * 0.25 +
              (furnish_num / 2) * 0.2 + (req.balconies / 3) * 0.15 + (req.parking / 2) * 0.1)
    dist_comp = req.distance_metro * 0.35 + req.distance_school * \
        0.2 + req.distance_hospital * 0.2 + req.distance_cbd * 0.25
    prox = max(0, (15 - dist_comp) / 15 * 10)
    age_bucket = 0 if req.age <= 2 else 1 if req.age <= 5 else 2 if req.age <= 10 else 3 if req.age <= 20 else 4

    loc_enc = encoders['location'].transform(
        [req.location])[0] if req.location in encoders['location'].classes_ else 0
    type_enc = encoders['property_type'].transform([req.property_type])[
        0] if req.property_type in encoders['property_type'].classes_ else 0
    furnish_enc = encoders['furnishing'].transform(
        [req.furnishing])[0] if req.furnishing in encoders['furnishing'].classes_ else 0
    listing_enc = encoders['listing_type'].transform([req.listing_type])[
        0] if req.listing_type in encoders['listing_type'].classes_ else 0

    features = [
        req.sqft, req.bedrooms, req.bathrooms, req.balconies, req.parking,
        req.age, req.floor, req.total_floors, req.amenities,
        req.distance_metro, req.distance_school, req.distance_hospital, req.distance_cbd,
        loc_score, luxury, amenity_idx, prox,
        age_bucket, furnish_num,
        loc_enc, 0, type_enc, furnish_enc, listing_enc
    ]

    price = int(model.predict([features])[0])

    # ROI prediction
    try:
        roi_model = get_model("roi_model")
        roi = round(float(roi_model.predict([features])[0]), 2)
    except:
        roi = 12.0

    # Signal
    try:
        signal_model = get_model("signal_model")
        signal_idx = int(signal_model.predict([features])[0])
        labels = ["BUY (Growth)", "HOLD (Steady)",
                  "SELL (Peak)", "WAIT (Correction)"]
        signal = labels[signal_idx]
    except:
        signal = "HOLD"

    return {
        "valuation": {
            "predicted_price": price,
            "price_range": [int(price * 0.92), int(price * 1.08)],
            "roi_forecast": roi,
        },
        "investment": {
            "signal": signal,
            "segment": "Premium" if price > 15000000 else "Mid-range" if price > 6000000 else "Budget",
        }
    }


@app.get("/market-stats")
def market_stats():
    df = load_data()
    loc_stats = df.groupby('location').agg(
        price=('price', 'mean'), roi=('roi', 'mean'), market_trend=('market_trend', 'mean')
    ).reset_index()

    return {
        "kpis": {
            "avg_price": int(df['price'].mean()),
            "total_assets": len(df),
            "undervalued_count": int(len(df[df.get('valuation_label', pd.Series(dtype=str)) == 'Underpriced'])) if 'valuation_label' in df.columns else 0,
            "market_growth": f"+{df['market_trend'].mean()*100:.1f}%",
            "high_roi_region": df.groupby('location')['roi'].mean().idxmax()
        },
        "trends": loc_stats.to_dict('records'),
    }


@app.get("/locations")
def location_intel():
    df = load_data()
    return df.groupby('location').agg(
        price=('price', 'mean'), roi=('roi', 'mean'),
        latitude=('latitude', 'mean'), longitude=('longitude', 'mean'),
        market_trend=('market_trend', 'mean'), demand_score=('demand_score', 'mean'),
        count=('property_id', 'count')
    ).reset_index().to_dict('records')


@app.get("/undervalued")
def undervalued_assets():
    df = load_data()
    if 'valuation_label' in df.columns:
        uv = df[df['valuation_label'] == 'Underpriced'].sort_values(
            'price_gap_pct').head(20)
        return uv.to_dict('records')
    return df.nlargest(20, 'roi').to_dict('records')


@app.get("/sell-signal")
def sell_signal(property_id: str):
    df = load_data()
    prop = df[df['property_id'] == property_id]
    if prop.empty:
        return {"signal": "HOLD", "explanation": "Property not found."}
    p = prop.iloc[0]
    trend = p['market_trend']
    if trend > 0.14:
        return {"signal": "BUY", "explanation": f"High growth trend ({trend*100:.1f}%). Strong buy opportunity."}
    elif trend < 0.07:
        return {"signal": "SELL", "explanation": f"Slowing growth ({trend*100:.1f}%). Consider selling at current valuation."}
    return {"signal": "HOLD", "explanation": f"Steady growth ({trend*100:.1f}%). Continue holding for appreciation."}
