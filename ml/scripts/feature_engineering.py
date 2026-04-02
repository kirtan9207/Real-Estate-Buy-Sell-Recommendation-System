import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import LabelEncoder, StandardScaler

def engineer_features(input_path='data/processed/cleaned_properties.csv', output_path='data/processed/feature_engineered_properties.csv'):
    df = pd.read_csv(input_path)
    
    # 1. New Location Scoring (using raw quality fields)
    df['location_score'] = (df['connectivity_score'] * 0.4 + df['safety_score'] * 0.3 + df['school_score'] * 0.3)
    
    # 2. Luxury Scoring (using sqft, amenities, and furnishing)
    furnish_map = {'Unfurnished': 0, 'Semi-furnished': 1, 'Fully-furnished': 2}
    df['luxury_score'] = ( (df['sqft'] / df['sqft'].max()) * 0.4 + 
                          (df['amenities_count'] / 18.0) * 0.3 + 
                          (df['furnishing'].map(furnish_map) / 2.0) * 0.3 )
    
    # 3. Market Momentum Logic
    # Price trend calculation (growth based on location trend * age factor)
    # Already provided in generator but ensuring consistency here.
    
    # 4. Encoding
    cat_cols = ['location', 'builder_name', 'property_type', 'furnishing', 'listing_type', 'cluster_label']
    for col in cat_cols:
        le = LabelEncoder()
        df[col + '_encoded'] = le.fit_transform(df[col])
        # Save encoders if needed for production
        
    # age bucket
    df['age_bucket'] = pd.cut(df['age'], bins=[0, 2, 5, 10, 20, 100], labels=[0, 1, 2, 3, 4], include_lowest=True).astype(int)
    
    # Save processed data
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Feature engineering complete. Data shape: {df.shape}")
    return df

if __name__ == "__main__":
    engineer_features()
