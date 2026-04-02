import pandas as pd
import numpy as np
import os
from datetime import datetime

def clean_production_data(input_path='data/raw/production_properties.csv', output_path='data/processed/cleaned_properties.csv'):
    df = pd.read_csv(input_path)
    
    # 1. Basic Cleaning
    df.drop_duplicates(subset=['property_id'], inplace=True)
    
    # 2. Impute missing (if any)
    for col in df.columns:
        if df[col].isnull().any():
            if df[col].dtype in [np.float64, np.int64]:
                df[col].fillna(df[col].median(), inplace=True)
            else:
                df[col].fillna(df[col].mode()[0], inplace=True)
    
    # 3. Handle outliers in price per sqft
    df['price_per_sqft'] = df['price'] / df['sqft']
    def remove_group_outliers(group):
        median = group['price_per_sqft'].median()
        return group[group['price_per_sqft'] <= 2.5 * median]
        
    df = df.groupby('location').apply(remove_group_outliers).reset_index(drop=True)
    
    # 4. Date parsing
    df['listing_date'] = pd.to_datetime(df['listing_date'])
    
    # 5. Save cleaned version
    os.makedirs('data/processed', exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Data cleaned. Total clean records: {len(df)}")
    return df

if __name__ == "__main__":
    clean_production_data()
