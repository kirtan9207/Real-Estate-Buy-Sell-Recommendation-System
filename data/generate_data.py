"""
Bangalore Real Estate Dataset Generator
========================================
Generates 20,000+ realistic property listings across 20 Bangalore localities.
Grain: 1 row = 1 property listing.
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

# ─── Bangalore Location Configurations ───────────────────────────────────────
LOCATIONS = {
 'Whitefield': {'base_price': 8500, 'growth': 0.12, 'lat': 12.9698, 'lon': 77.7499, 'segment': 'Mid-range', 'metro_dist_range': (0.5, 6.0)},
 'Indiranagar': {'base_price': 18000, 'growth': 0.08, 'lat': 12.9719, 'lon': 77.6412, 'segment': 'Premium', 'metro_dist_range': (0.2, 3.0)},
 'Electronic City': {'base_price': 6000, 'growth': 0.15, 'lat': 12.8452, 'lon': 77.6635, 'segment': 'Emerging', 'metro_dist_range': (1.0, 10.0)},
 'Koramangala': {'base_price': 15000, 'growth': 0.07, 'lat': 12.9352, 'lon': 77.6245, 'segment': 'Premium', 'metro_dist_range': (0.3, 4.0)},
 'HSR Layout': {'base_price': 11000, 'growth': 0.10, 'lat': 12.9121, 'lon': 77.6446, 'segment': 'Mid-range', 'metro_dist_range': (0.5, 5.0)},
 'Sarjapur Road': {'base_price': 7500, 'growth': 0.14, 'lat': 12.9063, 'lon': 77.6823, 'segment': 'Emerging', 'metro_dist_range': (2.0, 12.0)},
 'Hebbal': {'base_price': 9500, 'growth': 0.11, 'lat': 13.0354, 'lon': 77.5988, 'segment': 'Mid-range', 'metro_dist_range': (0.3, 5.0)},
 'Bannerghatta Road': {'base_price': 7000, 'growth': 0.13, 'lat': 12.8711, 'lon': 77.5922, 'segment': 'Budget', 'metro_dist_range': (2.0, 10.0)},
 'Marathahalli': {'base_price': 8000, 'growth': 0.11, 'lat': 12.9591, 'lon': 77.7009, 'segment': 'Mid-range', 'metro_dist_range': (0.5, 6.0)},
 'JP Nagar': {'base_price': 9000, 'growth': 0.09, 'lat': 12.9063, 'lon': 77.5857, 'segment': 'Mid-range', 'metro_dist_range': (0.3, 5.0)},
 'Jayanagar': {'base_price': 14000, 'growth': 0.06, 'lat': 12.9250, 'lon': 77.5838, 'segment': 'Premium', 'metro_dist_range': (0.2, 3.0)},
 'BTM Layout': {'base_price': 9500, 'growth': 0.10, 'lat': 12.9166, 'lon': 77.6101, 'segment': 'Mid-range', 'metro_dist_range': (0.3, 4.0)},
 'Yelahanka': {'base_price': 5500, 'growth': 0.16, 'lat': 13.1007, 'lon': 77.5963, 'segment': 'Emerging', 'metro_dist_range': (2.0, 12.0)},
 'KR Puram': {'base_price': 5000, 'growth': 0.14, 'lat': 13.0098, 'lon': 77.6967, 'segment': 'Budget', 'metro_dist_range': (1.0, 8.0)},
 'Rajajinagar': {'base_price': 12000, 'growth': 0.07, 'lat': 12.9866, 'lon': 77.5527, 'segment': 'Premium', 'metro_dist_range': (0.2, 3.0)},
 'Malleswaram': {'base_price': 13000, 'growth': 0.06, 'lat': 13.0035, 'lon': 77.5648, 'segment': 'Premium', 'metro_dist_range': (0.2, 3.0)},
 'Basavanagudi': {'base_price': 11500, 'growth': 0.08, 'lat': 12.9422, 'lon': 77.5737, 'segment': 'Mid-range', 'metro_dist_range': (0.5, 5.0)},
 'Devanahalli': {'base_price': 4500, 'growth': 0.18, 'lat': 13.1124, 'lon': 77.7130, 'segment': 'Emerging', 'metro_dist_range': (5.0, 15.0)},
 'Kanakapura Road': {'base_price': 5500, 'growth': 0.15, 'lat': 12.8684, 'lon': 77.5578, 'segment': 'Budget', 'metro_dist_range': (3.0, 12.0)},
 'Hennur': {'base_price': 6500, 'growth': 0.13, 'lat': 13.0452, 'lon': 77.6388, 'segment': 'Emerging', 'metro_dist_range': (1.0, 8.0)},
}

PROPERTY_TYPES = ['Apartment', 'Villa', 'Penthouse', 'Builder Floor', 'Plot']
PROPERTY_TYPE_WEIGHTS = [0.55, 0.15, 0.05, 0.15, 0.10]

BUILDERS = [
 'Prestige Group', 'Sobha Ltd', 'Brigade Group', 'Puravankara',
 'Godrej Properties', 'Lodha Group', 'Salarpuria Sattva',
 'Mantri Developers', 'Shriram Properties', 'Assetz Property Group'
]

FURNISHING = ['Unfurnished', 'Semi-furnished', 'Fully-furnished']
FURNISHING_WEIGHTS = [0.35, 0.40, 0.25]

LISTING_TYPES = ['Resale', 'New Launch', 'Ready to Move']
LISTING_TYPE_WEIGHTS = [0.40, 0.25, 0.35]

# MG Road CBD coordinates for distance calculation
CBD_LAT, CBD_LON = 12.9716, 77.5946


def haversine_km(lat1, lon1, lat2, lon2):
 """Approximate distance in km between two lat/lon points."""
 R = 6371
 dlat = np.radians(lat2 - lat1)
 dlon = np.radians(lon2 - lon1)
 a = np.sin(dlat / 2) ** 2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2) ** 2
 return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))


def generate_production_data(num_records=20000, seed=42):
 """Generate realistic Bangalore property dataset."""
 np.random.seed(seed)
 random.seed(seed)

 data = []
 start_date = datetime(2020, 1, 1)
 location_names = list(LOCATIONS.keys())

 for i in range(num_records):
 loc_name = random.choice(location_names)
 loc = LOCATIONS[loc_name]

 # ── Property characteristics ──
 prop_type = random.choices(PROPERTY_TYPES, weights=PROPERTY_TYPE_WEIGHTS, k=1)[0]

 if prop_type == 'Plot':
 sqft = random.randint(600, 3000)
 bedrooms = 0
 bathrooms = 0
 balconies = 0
 floor = 0
 total_floors = 0
 elif prop_type == 'Villa':
 sqft = random.randint(1800, 5000)
 bedrooms = random.randint(3, 5)
 bathrooms = random.randint(2, 4)
 balconies = random.randint(1, 3)
 floor = random.randint(1, 3)
 total_floors = random.randint(2, 4)
 elif prop_type == 'Penthouse':
 sqft = random.randint(2500, 5000)
 bedrooms = random.randint(3, 5)
 bathrooms = random.randint(3, 4)
 balconies = random.randint(2, 3)
 total_floors = random.randint(15, 30)
 floor = total_floors # Penthouse is top floor
 else: # Apartment, Builder Floor
 sqft = random.randint(500, 3000)
 bedrooms = random.randint(1, 3) if sqft < 1500 else random.randint(2, 5)
 bathrooms = max(1, bedrooms - random.randint(0, 1))
 balconies = random.randint(0, 2)
 total_floors = random.randint(3, 25)
 floor = random.randint(1, total_floors)

 parking = random.randint(0, 1) if prop_type in ['Apartment', 'Builder Floor'] else random.randint(1, 2)
 age = random.randint(0, 25)
 furnish = random.choices(FURNISHING, weights=FURNISHING_WEIGHTS, k=1)[0]
 listing_type = random.choices(LISTING_TYPES, weights=LISTING_TYPE_WEIGHTS, k=1)[0]
 builder = random.choice(BUILDERS)
 amenities = random.randint(2, 20)

 # ── Distance features ──
 dist_metro = round(random.uniform(*loc['metro_dist_range']), 2)
 dist_school = round(random.uniform(0.2, 8.0), 2)
 dist_hospital = round(random.uniform(0.3, 10.0), 2)

 lat = loc['lat'] + random.uniform(-0.015, 0.015)
 lon = loc['lon'] + random.uniform(-0.015, 0.015)
 dist_cbd = round(haversine_km(lat, lon, CBD_LAT, CBD_LON), 2)

 # ── Derived scores ──
 connectivity = round(max(1.0, 10.0 - (dist_metro * 0.4 + dist_cbd * 0.15)), 1)
 safety = random.randint(5, 10)
 school_sc = random.randint(4, 10)

 # ── Price computation ──
 ppsqft = loc['base_price']

 # Age adjustment
 if age == 0:
 ppsqft *= 1.20 # Under-construction premium
 elif age <= 2:
 ppsqft *= 1.12
 elif age <= 5:
 ppsqft *= 1.0
 elif age <= 10:
 ppsqft *= 0.92
 elif age <= 15:
 ppsqft *= 0.85
 else:
 ppsqft *= 0.78

 # Property type multiplier
 type_mult = {'Apartment': 1.0, 'Villa': 1.35, 'Penthouse': 1.55, 'Builder Floor': 0.95, 'Plot': 0.70}
 ppsqft *= type_mult[prop_type]

 # Furnishing premium
 furnish_mult = {'Unfurnished': 1.0, 'Semi-furnished': 1.08, 'Fully-furnished': 1.18}
 ppsqft *= furnish_mult[furnish]

 base_price = sqft * ppsqft
 base_price += bedrooms * 350000
 base_price += amenities * 120000
 base_price += balconies * 150000
 base_price += parking * 300000

 # Metro proximity premium
 if dist_metro < 1.0:
 base_price *= 1.15
 elif dist_metro < 2.0:
 base_price *= 1.08
 elif dist_metro < 3.0:
 base_price *= 1.03

 # High-floor premium for apartments
 if prop_type in ['Apartment', 'Penthouse'] and floor > 10:
 base_price *= 1.05

 # Builder reputation factor
 premium_builders = ['Prestige Group', 'Sobha Ltd', 'Godrej Properties', 'Brigade Group']
 if builder in premium_builders:
 base_price *= 1.06

 # Market noise (±10%)
 actual_price = int(base_price * random.uniform(0.90, 1.10))

 # ── Market features ──
 roi = round((loc['growth'] * 100) + random.uniform(-3, 4), 2)
 roi = max(3.0, roi) # Floor at 3%
 demand_score = random.randint(30, 98)
 liquidity_score = random.randint(25, 95)
 market_trend = round(loc['growth'] + random.uniform(-0.03, 0.03), 4)
 market_trend = max(0.03, market_trend)

 listing_date = start_date + timedelta(days=random.randint(0, 1825)) # 5 years

 data.append({
 'property_id': f"BLR-{i + 10001}",
 'location': loc_name,
 'latitude': round(lat, 6),
 'longitude': round(lon, 6),
 'builder_name': builder,
 'property_type': prop_type,
 'furnishing': furnish,
 'listing_type': listing_type,
 'sqft': sqft,
 'bedrooms': bedrooms,
 'bathrooms': bathrooms,
 'balconies': balconies,
 'parking': parking,
 'floor': floor,
 'total_floors': total_floors,
 'age': age,
 'amenities_count': amenities,
 'distance_metro': dist_metro,
 'distance_school': dist_school,
 'distance_hospital': dist_hospital,
 'distance_cbd': dist_cbd,
 'connectivity_score': connectivity,
 'safety_score': safety,
 'school_score': school_sc,
 'price': actual_price,
 'demand_score': demand_score,
 'liquidity_score': liquidity_score,
 'roi': roi,
 'market_trend': market_trend,
 'listing_date': listing_date.strftime('%Y-%m-%d'),
 })

 df = pd.DataFrame(data)

 # Save raw data
 os.makedirs('data/raw', exist_ok=True)
 output_path = 'data/raw/bangalore_properties.csv'
 df.to_csv(output_path, index=False)

 print(f" Generated {num_records} Bangalore property records")
 print(f" Locations: {df['location'].nunique()}")
 print(f" Price range: ₹{df['price'].min():,.0f} — ₹{df['price'].max():,.0f}")
 print(f" Saved to: {output_path}")
 return df


if __name__ == '__main__':
 generate_production_data()
