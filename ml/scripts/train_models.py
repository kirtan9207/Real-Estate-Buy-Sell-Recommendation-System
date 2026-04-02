import pandas as pd
import numpy as np
import os
import pickle
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor, XGBClassifier
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def train_production_models(input_path='data/processed/feature_engineered_properties.csv'):
    df = pd.read_csv(input_path)
    
    # 1. Price Prediction Features
    price_features = [
        'sqft', 'bedrooms', 'bathrooms', 'age', 'amenities_count', 
        'distance_metro', 'location_encoded', 'builder_name_encoded', 
        'property_type_encoded', 'furnishing_encoded', 'listing_type_encoded', 
        'location_score', 'luxury_score', 'age_bucket'
    ]
    X_price = df[price_features]
    y_price = df['price']
    
    X_train, X_test, y_train, y_test = train_test_split(X_price, y_price, test_size=0.2, random_state=42)
    
    price_model = XGBRegressor(n_estimators=1000, learning_rate=0.05, max_depth=7, n_jobs=-1, random_state=42)
    price_model.fit(X_train, y_train)
    
    preds = price_model.predict(X_test)
    print(f"Price Model - RMSE: {np.sqrt(mean_squared_error(y_test, preds))}, R2: {r2_score(y_test, preds)}")
    
    # 2. ROI Prediction Features (using similar features but targeting ROI)
    y_roi = df['roi']
    X_train_roi, X_test_roi, y_train_roi, y_test_roi = train_test_split(X_price, y_roi, test_size=0.2, random_state=42)
    
    roi_model = XGBRegressor(n_estimators=500, learning_rate=0.1, max_depth=5, n_jobs=-1, random_state=42)
    roi_model.fit(X_train_roi, y_train_roi)
    
    # 3. Sell Signal Classification (Rising, Stable, Peak, Falling)
    # Target: market_trend categorized
    def classify_trend(t):
        if t > 0.13: return 0 # Buy (Early Growth)
        if t > 0.10: return 1 # Hold (Rising)
        if t > 0.08: return 2 # Sell (Peak)
        return 3 # Wait (Falling)
    
    df['sell_signal'] = df['market_trend'].apply(classify_trend)
    y_signal = df['sell_signal']
    
    X_train_sig, X_test_sig, y_train_sig, y_test_sig = train_test_split(X_price, y_signal, test_size=0.2, random_state=42)
    signal_model = XGBClassifier(n_estimators=300, random_state=42)
    signal_model.fit(X_train_sig, y_train_sig)
    
    # 4. Clustering (Segmentation)
    segment_data = df[['price', 'roi', 'location_score', 'luxury_score', 'demand_score']]
    scaler = StandardScaler()
    segment_scaled = scaler.fit_transform(segment_data)
    
    kmeans = KMeans(n_clusters=4, random_state=42, n_init='auto')
    df['segment_label'] = kmeans.fit_predict(segment_scaled)
    
    # Save all models
    os.makedirs('ml/models', exist_ok=True)
    models = {
        'price_model.pkl': price_model,
        'roi_model.pkl': roi_model,
        'signal_model.pkl': signal_model,
        'cluster_model.pkl': kmeans,
        'scaler.pkl': scaler
    }
    
    for name, model in models.items():
        with open(os.path.join('ml/models', name), 'wb') as f:
            pickle.dump(model, f)
            
    # Save final dataset with inference baseline
    df.to_csv('data/processed/production_final.csv', index=False)
    print("All production models trained and saved.")

if __name__ == "__main__":
    train_production_models()
