-- Setup schema for Real Estate Intelligence Platform
CREATE TABLE IF NOT EXISTS properties (
    property_id VARCHAR(50) PRIMARY KEY,
    location VARCHAR(100),
    builder_name VARCHAR(100),
    property_type VARCHAR(50),
    furnishing VARCHAR(50),
    listing_type VARCHAR(50),
    sqft INTEGER,
    bedrooms INTEGER,
    bathrooms INTEGER,
    age INTEGER,
    amenities_count INTEGER,
    distance_metro FLOAT,
    price BIGINT,
    latitude FLOAT,
    longitude FLOAT,
    demand_score INTEGER,
    liquidity_score INTEGER,
    connectivity_score FLOAT,
    safety_score INTEGER,
    school_score INTEGER,
    roi FLOAT,
    market_trend FLOAT,
    listing_date DATE,
    cluster_label VARCHAR(50),
    segment_label INTEGER
);

CREATE TABLE IF NOT EXISTS location_stats (
    location VARCHAR(100) PRIMARY KEY,
    avg_price BIGINT,
    avg_roi FLOAT,
    market_trend FLOAT,
    demand_score FLOAT,
    latitude FLOAT,
    longitude FLOAT,
    segment_label INTEGER
);

CREATE TABLE IF NOT EXISTS market_summary (
    id SERIAL PRIMARY KEY,
    total_assets INTEGER,
    avg_price BIGINT,
    undervalued_count INTEGER,
    market_growth VARCHAR(10),
    best_roi_location VARCHAR(100)
);
