import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

def generate_production_data(num_records=20000):
    # Realistic locations inspired by major metros (e.g. Bangalore/Mumbai areas)
    locations = {
        'Whitefield': {'base_price': 8500, 'growth': 0.12, 'lat': 12.9698, 'lon': 77.7499, 'segment': 'Mid-range'},
        'Indiranagar': {'base_price': 18000, 'growth': 0.08, 'lat': 12.9719, 'lon': 77.6412, 'segment': 'Premium'},
        'Electronic City': {'base_price': 6000, 'growth': 0.15, 'lat': 12.8452, 'lon': 77.6635, 'segment': 'Emerging'},
        'Koramangala': {'base_price': 15000, 'growth': 0.07, 'lat': 12.9352, 'lon': 77.6245, 'segment': 'Premium'},
        'HSR Layout': {'base_price': 11000, 'growth': 0.10, 'lat': 12.9121, 'lon': 77.6446, 'segment': 'Mid-range'},
        'Sarjapur Road': {'base_price': 7500, 'growth': 0.14, 'lat': 12.9063, 'lon': 77.6823, 'segment': 'Emerging'},
        'Hebbal': {'base_price': 9500, 'growth': 0.11, 'lat': 13.0354, 'lon': 77.5988, 'segment': 'Mid-range'},
        'Bannerghatta': {'base_price': 7000, 'growth': 0.13, 'lat': 12.8711, 'lon': 77.5922, 'segment': 'Budget'}
    }
    
    property_types = ['Apartment', 'Villa', 'Penthouse', 'Builder Floor']
    builders = ['Prestige Group', 'Sobha Ltd', 'Brigade Group', 'Puravankara', 'Godrej Properties', 'Lodha Group']
    furnishing = ['Unfurnished', 'Semi-furnished', 'Fully-furnished']
    listing_types = ['Resale', 'New Launch', 'Ready to Move']
    
    data = []
    start_date = datetime(2022, 1, 1)
    
    for i in range(num_records):
        loc_name = random.choice(list(locations.keys()))
        loc_meta = locations[loc_name]
        
        sqft = random.randint(600, 4500)
        bedrooms = random.randint(1, 4) if sqft < 2500 else random.randint(3, 5)
        bathrooms = max(1, bedrooms - random.randint(0, 1))
        age = random.randint(0, 20)
        
        # Base logic + realistic variability
        price_per_sqft = loc_meta['base_price']
        if age < 2: price_per_sqft *= 1.15
        if age > 10: price_per_sqft *= 0.85
        
        # Amenities & Proximity
        dist_metro = round(random.uniform(0.2, 12.0), 2)
        amenities = random.randint(2, 18)
        
        # Calculate Price
        base_price = sqft * price_per_sqft
        base_price += (bedrooms * 400000) + (amenities * 150000)
        if dist_metro < 2: base_price *= 1.12
        
        # Market Noise
        actual_price = int(base_price * random.uniform(0.92, 1.08))
        
        # Derived Analysis Features
        roi = round((loc_meta['growth'] * 100) + random.uniform(-2, 3), 2)
        demand_score = random.randint(40, 95)
        liquidity_score = random.randint(30, 90)
        
        # Scores
        connectivity = round(10 - (dist_metro * 0.5), 1)
        safety = random.randint(6, 10)
        schools = random.randint(5, 10)
        
        listing_date = start_date + timedelta(days=random.randint(0, 730))
        
        data.append({
            'property_id': f"RE-{i+10001}",
            'location': loc_name,
            'builder_name': random.choice(builders),
            'property_type': random.choice(property_types),
            'furnishing': random.choice(furnishing),
            'listing_type': random.choice(listing_types),
            'sqft': sqft,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'age': age,
            'amenities_count': amenities,
            'distance_metro': dist_metro,
            'price': actual_price,
            'latitude': loc_meta['lat'] + random.uniform(-0.01, 0.01),
            'longitude': loc_meta['lon'] + random.uniform(-0.01, 0.01),
            'demand_score': demand_score,
            'liquidity_score': liquidity_score,
            'connectivity_score': connectivity,
            'safety_score': safety,
            'school_score': schools,
            'roi': roi,
            'market_trend': loc_meta['growth'] + random.uniform(-0.02, 0.02),
            'listing_date': listing_date.strftime('%Y-%m-%d'),
            'cluster_label': loc_meta['segment']
        })
    
    df = pd.DataFrame(data)
    os.makedirs('data/raw', exist_ok=True)
    df.to_csv('data/raw/production_properties.csv', index=False)
    print(f"Generated {num_records} premium records in data/raw/production_properties.csv")

if __name__ == "__main__":
    generate_production_data()
