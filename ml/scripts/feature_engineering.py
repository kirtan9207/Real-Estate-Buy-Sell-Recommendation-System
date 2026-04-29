"""
Feature Engineering Pipeline
=============================
Generates 9+ engineered features:
- price_per_sqft, location_score, amenity_index, age_bucket
- market_trend_indicator, distance_composite, roi_estimate
- luxury_score, value_ratio
- Label + one-hot encoding for categoricals
- StandardScaler saved as artifact
"""

import pandas as pd
import numpy as np
import os
import pickle
from sklearn.preprocessing import LabelEncoder, StandardScaler


def engineer_features(
 input_path='data/processed/cleaned_properties.csv',
 output_path='data/processed/feature_engineered.csv',
 encoders_path='ml/models/encoders.pkl'
):
 df = pd.read_csv(input_path)
 print(f" Loaded {len(df)} rows for feature engineering")

 # ═══════════════════════════════════════════════════════
 # 1. Price Per Sqft (ensure it exists)
 # ═══════════════════════════════════════════════════════
 df['price_per_sqft'] = (df['price'] / df['sqft']).round(2)

 # ═══════════════════════════════════════════════════════
 # 2. Location Score (composite quality index)
 # ═══════════════════════════════════════════════════════
 df['location_score'] = (
 df['connectivity_score'] * 0.40 +
 df['safety_score'] * 0.30 +
 df['school_score'] * 0.30
 ).round(3)

 # ═══════════════════════════════════════════════════════
 # 3. Amenity Index (normalized 0-1)
 # ═══════════════════════════════════════════════════════
 df['amenity_index'] = (df['amenities_count'] / 20.0).round(3)

 # ═══════════════════════════════════════════════════════
 # 4. Age Bucketization
 # ═══════════════════════════════════════════════════════
 age_bins = [0, 2, 5, 10, 20, 100]
 age_labels = [0, 1, 2, 3, 4] # New, Recent, Mid, Old, Very Old
 df['age_bucket'] = pd.cut(
 df['age'], bins=age_bins, labels=age_labels, include_lowest=True
 ).astype(int)

 # ═══════════════════════════════════════════════════════
 # 5. Market Trend Indicator (categorical)
 # ═══════════════════════════════════════════════════════
 def classify_trend(trend):
 if trend >= 0.14:
 return 'Hot'
 elif trend >= 0.10:
 return 'Warm'
 elif trend >= 0.07:
 return 'Cool'
 else:
 return 'Cold'

 df['trend_category'] = df['market_trend'].apply(classify_trend)

 # ═══════════════════════════════════════════════════════
 # 6. Distance Composite (weighted proximity score)
 # ═══════════════════════════════════════════════════════
 df['distance_composite'] = (
 df['distance_metro'] * 0.35 +
 df['distance_school'] * 0.20 +
 df['distance_hospital'] * 0.20 +
 df['distance_cbd'] * 0.25
 ).round(3)

 # Inverted proximity score (higher = closer to everything)
 max_dist = df['distance_composite'].max()
 df['proximity_score'] = ((max_dist - df['distance_composite']) / max_dist * 10).round(2)

 # ═══════════════════════════════════════════════════════
 # 7. ROI Estimate
 # ═══════════════════════════════════════════════════════
 df['roi_estimate'] = (
 df['market_trend'] * 100 +
 df['demand_score'] * 0.05 +
 df['liquidity_score'] * 0.03
 ).round(2)

 # ═══════════════════════════════════════════════════════
 # 8. Luxury Score (composite)
 # ═══════════════════════════════════════════════════════
 furnish_map = {'Unfurnished': 0, 'Semi-furnished': 1, 'Fully-furnished': 2}
 df['furnish_numeric'] = df['furnishing'].map(furnish_map)

 sqft_norm = df['sqft'] / df['sqft'].max()
 amenity_norm = df['amenities_count'] / 20.0
 furnish_norm = df['furnish_numeric'] / 2.0
 balcony_norm = df['balconies'] / 3.0
 parking_norm = df['parking'] / 2.0

 df['luxury_score'] = (
 sqft_norm * 0.30 +
 amenity_norm * 0.25 +
 furnish_norm * 0.20 +
 balcony_norm * 0.15 +
 parking_norm * 0.10
 ).round(3)

 # ═══════════════════════════════════════════════════════
 # 9. Value Ratio (price vs location median)
 # ═══════════════════════════════════════════════════════
 location_median = df.groupby('location')['price'].transform('median')
 df['value_ratio'] = (df['price'] / location_median).round(3)

 # ═══════════════════════════════════════════════════════
 # ENCODING: Label Encoding for all categoricals
 # ═══════════════════════════════════════════════════════
 cat_cols = ['location', 'builder_name', 'property_type', 'furnishing',
 'listing_type', 'trend_category']

 encoders = {}
 for col in cat_cols:
 le = LabelEncoder()
 df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
 encoders[col] = le

 # ═══════════════════════════════════════════════════════
 # SCALING: Save StandardScaler for numeric features
 # ═══════════════════════════════════════════════════════
 scale_cols = [
 'sqft', 'bedrooms', 'bathrooms', 'age', 'amenities_count',
 'distance_metro', 'distance_school', 'distance_hospital', 'distance_cbd',
 'connectivity_score', 'safety_score', 'school_score',
 'location_score', 'amenity_index', 'luxury_score',
 'proximity_score', 'distance_composite'
 ]

 scaler = StandardScaler()
 scaler.fit(df[scale_cols])
 encoders['scaler'] = scaler
 encoders['scale_columns'] = scale_cols

 # ═══════════════════════════════════════════════════════
 # SAVE
 # ═══════════════════════════════════════════════════════
 os.makedirs(os.path.dirname(output_path), exist_ok=True)
 df.to_csv(output_path, index=False)

 os.makedirs(os.path.dirname(encoders_path), exist_ok=True)
 with open(encoders_path, 'wb') as f:
 pickle.dump(encoders, f)

 print(f"\n{'='*50}")
 print(f" FEATURE ENGINEERING SUMMARY")
 print(f"{'='*50}")
 print(f" Shape: {df.shape}")
 print(f" New features: price_per_sqft, location_score, amenity_index,")
 print(f" age_bucket, trend_category, distance_composite, proximity_score,")
 print(f" roi_estimate, luxury_score, value_ratio, furnish_numeric")
 print(f" Encoded columns: {len(cat_cols)}")
 print(f" Saved to: {output_path}")
 print(f" Encoders: {encoders_path}")

 return df


if __name__ == '__main__':
 engineer_features()
