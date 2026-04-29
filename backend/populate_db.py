import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
import os


def populate_db(csv_path='data/processed/final_dataset.csv'):
    # For Docker local testing, we'll use sqlite if postgres is not reachable or specify env
    DB_URL = os.getenv(
        "DATABASE_URL", "postgresql://user:password@localhost:5432/real_estate")

    try:
        engine = create_engine(DB_URL)
        df = pd.read_csv(csv_path)

        # 1. Properties Table
        # Select matching columns
        props_df = df[[
            'property_id', 'location', 'latitude', 'longitude', 'sqft', 'bedrooms',
            'bathrooms', 'balconies', 'parking', 'age', 'floor', 'total_floors',
            'furnished', 'amenities_count', 'distance_metro', 'distance_school',
            'distance_hospital', 'listing_date', 'sale_date', 'price'
        ]]
        props_df.to_sql('properties', engine, if_exists='append',
                        index=False, method='multi')

        print("Database populated successfully.")
    except Exception as e:
        print(f"Error populating database: {e}")
        # For local run without Postgres, we'll skip DB but the API should handle fallback


if __name__ == "__main__":
    populate_db()
