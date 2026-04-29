"""
Recommendation Engine
======================
- Overpriced / Underpriced detection (predicted vs actual gap)
- Buyer preference matching (cosine similarity)
- Sell timing signal (trend-based logic)
"""

import pandas as pd
import numpy as np
import os
import pickle
import json
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler


def run_recommendation_engine(
    input_path='data/processed/production_final.csv',
    output_dir='ml/models',
    report_path='ml/reports/recommendation_report.json'
):
    df = pd.read_csv(input_path)
    print(f"📂 Loaded {len(df)} rows for recommendations")

    # ═══════════════════════════════════════════════════════
    # 1. OVERPRICED / UNDERPRICED DETECTION
    # ═══════════════════════════════════════════════════════
    if 'predicted_price' not in df.columns:
        print("⚠️ predicted_price column missing. Run train_models.py first.")
        return

    df['price_gap'] = df['price'] - df['predicted_price']
    df['price_gap_pct'] = ((df['price_gap'] / df['predicted_price']) * 100).round(2)

    df['valuation_label'] = 'Fair Value'
    df.loc[df['price_gap_pct'] < -10, 'valuation_label'] = 'Underpriced'
    df.loc[df['price_gap_pct'] > 10, 'valuation_label'] = 'Overpriced'

    underpriced = df[df['valuation_label'] == 'Underpriced'].sort_values('price_gap_pct')
    overpriced = df[df['valuation_label'] == 'Overpriced'].sort_values('price_gap_pct', ascending=False)

    valuation_stats = {
        'underpriced_count': len(underpriced),
        'overpriced_count': len(overpriced),
        'fair_value_count': len(df[df['valuation_label'] == 'Fair Value']),
        'top_underpriced': underpriced.head(20)[
            ['property_id', 'location', 'price', 'predicted_price', 'price_gap_pct', 'sqft', 'bedrooms']
        ].to_dict('records'),
        'top_overpriced': overpriced.head(20)[
            ['property_id', 'location', 'price', 'predicted_price', 'price_gap_pct', 'sqft', 'bedrooms']
        ].to_dict('records'),
    }
    print(f"   Underpriced: {len(underpriced)} | Overpriced: {len(overpriced)}")

    # ═══════════════════════════════════════════════════════
    # 2. BUYER PREFERENCE MATCHING (Cosine Similarity)
    # ═══════════════════════════════════════════════════════
    match_features = ['bedrooms', 'sqft', 'location_score', 'amenity_index',
                       'luxury_score', 'proximity_score', 'price']

    # Only use rows with all features available
    match_df = df[match_features].fillna(0)

    scaler = MinMaxScaler()
    match_scaled = scaler.fit_transform(match_df)

    # Save matching artifacts
    match_artifacts = {
        'scaler': scaler,
        'feature_columns': match_features,
        'property_ids': df['property_id'].tolist(),
        'match_matrix': match_scaled,
    }

    with open(os.path.join(output_dir, 'recommendation_artifacts.pkl'), 'wb') as f:
        pickle.dump(match_artifacts, f)

    print(f"   Buyer matching artifacts saved ({len(match_features)} features)")

    # ═══════════════════════════════════════════════════════
    # 3. SELL TIMING SIGNAL
    # ═══════════════════════════════════════════════════════
    def compute_sell_signal(row):
        trend = row.get('market_trend', 0.1)
        roi = row.get('roi', 10)
        demand = row.get('demand_score', 50)

        score = 0
        # High growth = BUY signal
        if trend > 0.14:
            score += 2
        elif trend > 0.10:
            score += 1
        elif trend < 0.07:
            score -= 2
        else:
            score -= 1

        # High ROI = BUY signal
        if roi > 15:
            score += 1
        elif roi < 8:
            score -= 1

        # High demand = BUY signal
        if demand > 75:
            score += 1
        elif demand < 40:
            score -= 1

        if score >= 3:
            return 'STRONG BUY'
        elif score >= 1:
            return 'BUY'
        elif score >= 0:
            return 'HOLD'
        elif score >= -2:
            return 'SELL'
        else:
            return 'STRONG SELL'

    df['sell_signal'] = df.apply(compute_sell_signal, axis=1)

    signal_dist = df['sell_signal'].value_counts().to_dict()
    print(f"   Sell signals: {signal_dist}")

    # ═══════════════════════════════════════════════════════
    # SAVE
    # ═══════════════════════════════════════════════════════
    df.to_csv(input_path, index=False)  # Update production_final with new columns

    report = {
        'valuation': valuation_stats,
        'sell_signal_distribution': signal_dist,
        'matching_features': match_features,
    }
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n{'='*50}")
    print(f"🎯 RECOMMENDATION ENGINE COMPLETE")
    print(f"{'='*50}")
    print(f"   Underpriced deals: {len(underpriced)}")
    print(f"   Overpriced properties: {len(overpriced)}")
    print(f"   Signal distribution: {signal_dist}")
    print(f"   Report: {report_path}")
    return report


def match_buyer_preferences(budget, bedrooms, min_sqft, preferred_location=None, top_n=10):
    """Match buyer preferences to best properties using cosine similarity."""
    with open('ml/models/recommendation_artifacts.pkl', 'rb') as f:
        artifacts = pickle.load(f)

    df = pd.read_csv('data/processed/production_final.csv')

    # Create buyer preference vector
    buyer_pref = {
        'bedrooms': bedrooms,
        'sqft': min_sqft,
        'location_score': 8.0,
        'amenity_index': 0.6,
        'luxury_score': 0.5,
        'proximity_score': 7.0,
        'price': budget,
    }

    buyer_vec = artifacts['scaler'].transform(
        pd.DataFrame([buyer_pref])[artifacts['feature_columns']]
    )

    similarities = cosine_similarity(buyer_vec, artifacts['match_matrix'])[0]
    df['match_score'] = similarities

    # Filter by budget
    candidates = df[df['price'] <= budget * 1.1]
    if preferred_location:
        loc_matches = candidates[candidates['location'] == preferred_location]
        if len(loc_matches) >= top_n:
            candidates = loc_matches

    top = candidates.nlargest(top_n, 'match_score')
    return top[['property_id', 'location', 'price', 'sqft', 'bedrooms',
                'match_score', 'valuation_label', 'sell_signal']].to_dict('records')


if __name__ == '__main__':
    run_recommendation_engine()
