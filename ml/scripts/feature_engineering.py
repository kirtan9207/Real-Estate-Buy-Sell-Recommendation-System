import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import StandardScaler, LabelEncoder

def engineer_features(input_path='data/processed/cleaned_properties.csv', output_path='data/processed/feature_engineered_properties.csv'):
    df = pd.read_csv(input_path)
    
    # price_per_sqft (already created in cleaning, but ensuring)
    df['price_per_sqft'] = df['price'] / df['sqft']
    
    # location_avg_price
    location_avg = df.groupby('location')['price'].transform('mean')
    df['location_avg_price'] = location_avg
    
    # location_score (normalized average price of location)
    df['location_score'] = (df['location_avg_price'] - df['location_avg_price'].min()) / (df['location_avg_price'].max() - df['location_avg_price'].min())
    
    # amenity_score (amenities_count normalized)
    df['amenity_score'] = (df['amenity_count'] if 'amenity_count' in df.columns else df['amenities_count']) / 15.0 # Max possible in generator
    
    # age_bucket
    def bucket_age(age):
        if age == 0: return 'new'
        if age <= 5: return '0-5 years'
        if age <= 10: return '5-10 years'
        return '10+ years'
    df['age_bucket'] = df['age'].apply(bucket_age)
    
    # distance_score (weighted score of metro, school, hospital distance)
    # Lower distance is better, so 1 / (d+1)
    df['distance_score'] = ( (1 / (df['distance_metro'] + 1)) * 0.5 + 
                          (1 / (df['distance_school'] + 1)) * 0.25 + 
                          (1 / (df['distance_hospital'] + 1)) * 0.25 )
    
    # floor_ratio
    df['floor_ratio'] = df['floor'] / df['total_floors'].replace(0, 1)
    
    # luxury_score (combination of sqft, amenities, and location score)
    # Using Min-Max to combine
    sqft_norm = (df['sqft'] - df['sqft'].min()) / (df['sqft'].max() - df['sqft'].min())
    df['luxury_score'] = (sqft_norm * 0.4 + df['amenity_score'] * 0.3 + df['location_score'] * 0.3)
    
    # roi (estimated return on investment) - simplistic: (Location Score / Distance Score) * sqft
    df['roi'] = (df['location_score'] * df['distance_score'] * 100).round(2)
    
    # market_trend (rolling average price trend of that location - assuming date sort)
    df = df.sort_values(by=['location', 'listing_date'])
    df['market_trend'] = df.groupby('location')['price_per_sqft'].transform(lambda x: x.rolling(5, min_periods=1).mean())
    
    # Save cleaned categorical labels for later use
    label_encoders = {}
    for col in ['location', 'age_bucket']:
        le = LabelEncoder()
        df[col + '_encoded'] = le.fit_transform(df[col])
        label_encoders[col] = le
        
    # Scaling numeric features
    numeric_cols = ['sqft', 'bedrooms', 'bathrooms', 'amenities_count', 'distance_metro', 'age', 'luxury_score', 'roi']
    scaler = StandardScaler()
    df[ [c + '_scaled' for c in numeric_cols] ] = scaler.fit_transform(df[numeric_cols])
    
    # Save processed data
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"Feature engineering complete. Data saved to {output_path}")
    return df

if __name__ == "__main__":
    engineer_features()
