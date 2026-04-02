CREATE TABLE IF NOT EXISTS properties (
    property_id VARCHAR(50) PRIMARY KEY,
    location VARCHAR(100),
    latitude FLOAT,
    longitude FLOAT,
    sqft INT,
    bedrooms INT,
    bathrooms INT,
    balconies INT,
    parking INT,
    age INT,
    floor INT,
    total_floors INT,
    furnished INT,
    amenities_count INT,
    distance_metro FLOAT,
    distance_school FLOAT,
    distance_hospital FLOAT,
    listing_date DATE,
    sale_date DATE,
    price BIGINT
);

CREATE TABLE IF NOT EXISTS predictions (
    prediction_id SERIAL PRIMARY KEY,
    property_id VARCHAR(50) REFERENCES properties(property_id),
    predicted_price BIGINT,
    price_gap FLOAT,
    undervalued_flag BOOLEAN,
    roi FLOAT,
    cluster_label VARCHAR(50),
    buy_recommendation VARCHAR(50),
    sell_recommendation VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS buyer_preferences (
    buyer_id SERIAL PRIMARY KEY,
    budget BIGINT,
    preferred_location VARCHAR(100),
    bedrooms INT,
    amenities_min INT,
    max_distance_metro FLOAT
);
