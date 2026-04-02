import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

def clean_data(input_path='data/raw/raw_properties.csv', output_path='data/processed/cleaned_properties.csv'):
    df = pd.read_csv(input_path)
    
    report = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'rows_before': len(df),
        'missing_values_filled': 0,
        'duplicates_removed': 0,
        'outliers_removed': 0,
        'invalid_coords_removed': 0
    }
    
    # 1. Remove duplicates
    initial_len = len(df)
    df.drop_duplicates(inplace=True)
    report['duplicates_removed'] = initial_len - len(df)
    
    # 2. Handle missing values
    # Fill numeric with median, categoric with mode
    for col in df.columns:
        if df[col].isnull().any():
            if df[col].dtype in [np.float64, np.int64]:
                df[col].fillna(df[col].median(), inplace=True)
                report['missing_values_filled'] += 1
            else:
                df[col].fillna(df[col].mode()[0], inplace=True)
                report['missing_values_filled'] += 1
                
    # 3. Coordinate validation
    # Assuming standard lat/long ranges (-90 to 90, -180 to 180)
    initial_len = len(df)
    df = df[(df['latitude'].between(-90, 90)) & (df['longitude'].between(-180, 180))]
    report['invalid_coords_removed'] = initial_len - len(df)
    
    # 4. Outlier detection using price per sqft
    df['price_per_sqft'] = df['price'] / df['sqft']
    
    initial_len = len(df)
    def remove_location_outliers(group):
        median_val = group['price_per_sqft'].median()
        return group[group['price_per_sqft'] <= 3 * median_val]
    
    df = df.groupby('location').apply(remove_location_outliers).reset_index(drop=True)
    report['outliers_removed'] = initial_len - len(df)
    
    # 5. Date validation (listing_date should be <= current date)
    df['listing_date'] = pd.to_datetime(df['listing_date'], errors='coerce')
    df = df[df['listing_date'] <= datetime.now()]
    
    report['rows_after'] = len(df)
    
    # Save processed data
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    
    # Write log
    os.makedirs('data/logs', exist_ok=True)
    with open('data/logs/cleaning_report.txt', 'w') as f:
        f.write("--- DATA CLEANING REPORT ---\n")
        for key, val in report.items():
            f.write(f"{key}: {val}\n")
    
    print(f"Cleaning complete. Report saved to data/logs/cleaning_report.txt")
    return df

if __name__ == "__main__":
    clean_data()
