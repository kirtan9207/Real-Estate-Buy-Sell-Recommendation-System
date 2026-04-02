import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

def generate_synthetic_data(num_records=5000):
    locations = ['Downtown', 'Suburbs', 'Green Valley', 'Industrial Zone', 'Riverside', 'Hilltop', 'Tech Park', 'Historic District']
    
    data = []
    start_date = datetime(2020, 1, 1)
    
    for i in range(num_records):
        property_id = f"PROP_{i+1000}"
        location = random.choice(locations)
        
        # Base price per sqft depends on location
        base_price_map = {
            'Downtown': 10000,
            'Suburbs': 5000,
            'Green Valley': 7000,
            'Industrial Zone': 4000,
            'Riverside': 8500,
            'Hilltop': 9000,
            'Tech Park': 8000,
            'Historic District': 9500
        }
        
        sqft = random.randint(500, 5000)
        bedrooms = random.randint(1, 5)
        bathrooms = max(1, bedrooms - random.randint(0, 1))
        balconies = random.randint(0, 3)
        parking = random.randint(0, 2)
        age = random.randint(0, 30)
        total_floors = random.randint(1, 20)
        floor = random.randint(0, total_floors)
        furnished = random.choice([0, 1, 2]) # 0: Unfurnished, 1: Semi, 2: Full
        amenities_count = random.randint(0, 15)
        
        distance_metro = round(random.uniform(0.1, 15.0), 2)
        distance_school = round(random.uniform(0.1, 10.0), 2)
        distance_hospital = round(random.uniform(0.1, 12.0), 2)
        
        # Latitude/Longitude (Approx for a city)
        latitude = round(random.uniform(12.8, 13.2), 6)
        longitude = round(random.uniform(77.4, 77.8), 6)
        
        listing_date = start_date + timedelta(days=random.randint(0, 1500))
        # Some are sold, some not
        is_sold = random.random() > 0.3
        sale_date = listing_date + timedelta(days=random.randint(10, 180)) if is_sold else None
        
        # Calculate price with some logic + noise
        price = (sqft * base_price_map[location]) 
        price += (bedrooms * 500000)
        price += (amenities_count * 100000)
        price -= (age * 50000)
        price -= (distance_metro * 200000)
        
        # Add random noise
        noise = random.uniform(0.9, 1.1)
        price = int(price * noise)
        
        data.append({
            'property_id': property_id,
            'location': location,
            'latitude': latitude,
            'longitude': longitude,
            'sqft': sqft,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'balconies': balconies,
            'parking': parking,
            'age': age,
            'floor': floor,
            'total_floors': total_floors,
            'furnished': furnished,
            'amenities_count': amenities_count,
            'distance_metro': distance_metro,
            'distance_school': distance_school,
            'distance_hospital': distance_hospital,
            'listing_date': listing_date.strftime('%Y-%m-%d'),
            'sale_date': sale_date.strftime('%Y-%m-%d') if sale_date else None,
            'price': price
        })
    
    df = pd.DataFrame(data)
    os.makedirs('data/raw', exist_ok=True)
    df.to_csv('data/raw/raw_properties.csv', index=False)
    print(f"Generated {num_records} records in data/raw/raw_properties.csv")

if __name__ == "__main__":
    generate_synthetic_data()
