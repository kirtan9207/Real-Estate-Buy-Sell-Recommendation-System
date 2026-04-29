"""
Model Training Pipeline
========================
Trains 6 models:
1. Linear Regression (baseline parametric)
2. Decision Tree Regressor (interpretable)
3. Random Forest Regressor (ensemble)
4. XGBoost Regressor (primary production model)
5. ROI Regressor (XGBoost) — predicts expected ROI
6. Sell Signal Classifier (XGBoost) — Buy/Hold/Sell/Wait

All models + metadata saved to ml/models/
"""

import pandas as pd
import numpy as np
import os
import pickle
import json
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor, XGBClassifier
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# Feature columns used for price prediction
PRICE_FEATURES = [
    'sqft', 'bedrooms', 'bathrooms', 'balconies', 'parking',
    'age', 'floor', 'total_floors', 'amenities_count',
    'distance_metro', 'distance_school', 'distance_hospital', 'distance_cbd',
    'location_score', 'luxury_score', 'amenity_index', 'proximity_score',
    'age_bucket', 'furnish_numeric',
    'location_encoded', 'builder_name_encoded',
    'property_type_encoded', 'furnishing_encoded', 'listing_type_encoded'
]


def train_all_models(
    input_path='data/processed/feature_engineered.csv',
    models_dir='ml/models',
    test_size=0.2,
    random_state=42
):
    df = pd.read_csv(input_path)
    print(f"📂 Loaded {len(df)} rows for training")

    os.makedirs(models_dir, exist_ok=True)

    # Prepare features and target
    X = df[PRICE_FEATURES].copy()
    y = df['price'].copy()

    # Handle any remaining NaN in features
    X = X.fillna(0)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    train_indices = X_train.index
    test_indices = X_test.index

    print(f"   Train: {len(X_train)} | Test: {len(X_test)}")

    results = {}

    # ═══════════════════════════════════════════════════════
    # MODEL 1: Linear Regression
    # ═══════════════════════════════════════════════════════
    print("\n🔹 Training Linear Regression...")
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train)
    lr_pred = lr_model.predict(X_test)
    results['linear_regression'] = {
        'rmse': round(float(np.sqrt(mean_squared_error(y_test, lr_pred))), 2),
        'mae': round(float(mean_absolute_error(y_test, lr_pred)), 2),
        'r2': round(float(r2_score(y_test, lr_pred)), 4),
    }
    with open(os.path.join(models_dir, 'linear_regression.pkl'), 'wb') as f:
        pickle.dump(lr_model, f)
    print(f"   R²: {results['linear_regression']['r2']}")

    # ═══════════════════════════════════════════════════════
    # MODEL 2: Decision Tree
    # ═══════════════════════════════════════════════════════
    print("\n🔹 Training Decision Tree Regressor...")
    dt_model = DecisionTreeRegressor(max_depth=15, random_state=random_state)
    dt_model.fit(X_train, y_train)
    dt_pred = dt_model.predict(X_test)
    results['decision_tree'] = {
        'rmse': round(float(np.sqrt(mean_squared_error(y_test, dt_pred))), 2),
        'mae': round(float(mean_absolute_error(y_test, dt_pred)), 2),
        'r2': round(float(r2_score(y_test, dt_pred)), 4),
    }
    with open(os.path.join(models_dir, 'decision_tree.pkl'), 'wb') as f:
        pickle.dump(dt_model, f)
    print(f"   R²: {results['decision_tree']['r2']}")

    # ═══════════════════════════════════════════════════════
    # MODEL 3: Random Forest
    # ═══════════════════════════════════════════════════════
    print("\n🔹 Training Random Forest Regressor...")
    rf_model = RandomForestRegressor(
        n_estimators=300, max_depth=20, random_state=random_state, n_jobs=-1
    )
    rf_model.fit(X_train, y_train)
    rf_pred = rf_model.predict(X_test)
    results['random_forest'] = {
        'rmse': round(float(np.sqrt(mean_squared_error(y_test, rf_pred))), 2),
        'mae': round(float(mean_absolute_error(y_test, rf_pred)), 2),
        'r2': round(float(r2_score(y_test, rf_pred)), 4),
    }
    with open(os.path.join(models_dir, 'random_forest.pkl'), 'wb') as f:
        pickle.dump(rf_model, f)
    print(f"   R²: {results['random_forest']['r2']}")

    # ═══════════════════════════════════════════════════════
    # MODEL 4: XGBoost (Primary Production Model)
    # ═══════════════════════════════════════════════════════
    print("\n🔹 Training XGBoost Regressor (Primary)...")
    xgb_model = XGBRegressor(
        n_estimators=1000, learning_rate=0.05, max_depth=7,
        subsample=0.8, colsample_bytree=0.8,
        random_state=random_state, n_jobs=-1
    )
    xgb_model.fit(X_train, y_train)
    xgb_pred = xgb_model.predict(X_test)
    results['xgboost'] = {
        'rmse': round(float(np.sqrt(mean_squared_error(y_test, xgb_pred))), 2),
        'mae': round(float(mean_absolute_error(y_test, xgb_pred)), 2),
        'r2': round(float(r2_score(y_test, xgb_pred)), 4),
    }
    with open(os.path.join(models_dir, 'price_model.pkl'), 'wb') as f:
        pickle.dump(xgb_model, f)
    print(f"   R²: {results['xgboost']['r2']} ⭐ Primary Model")

    # ═══════════════════════════════════════════════════════
    # MODEL 5: ROI Regressor
    # ═══════════════════════════════════════════════════════
    print("\n🔹 Training ROI Regressor...")
    roi_model = XGBRegressor(
        n_estimators=500, learning_rate=0.1, max_depth=5,
        random_state=random_state, n_jobs=-1
    )
    y_roi_train = df.loc[train_indices, 'roi']
    y_roi_test = df.loc[test_indices, 'roi']
    roi_model.fit(X_train, y_roi_train)
    roi_pred = roi_model.predict(X_test)
    results['roi_model'] = {
        'rmse': round(float(np.sqrt(mean_squared_error(y_roi_test, roi_pred))), 2),
        'mae': round(float(mean_absolute_error(y_roi_test, roi_pred)), 2),
        'r2': round(float(r2_score(y_roi_test, roi_pred)), 4),
    }
    with open(os.path.join(models_dir, 'roi_model.pkl'), 'wb') as f:
        pickle.dump(roi_model, f)
    print(f"   R²: {results['roi_model']['r2']}")

    # ═══════════════════════════════════════════════════════
    # MODEL 6: Sell Signal Classifier
    # ═══════════════════════════════════════════════════════
    print("\n🔹 Training Sell Signal Classifier...")

    def classify_signal(trend):
        if trend > 0.14:
            return 0  # BUY — high growth
        elif trend > 0.10:
            return 1  # HOLD — steady
        elif trend > 0.07:
            return 2  # SELL — peak/slowing
        else:
            return 3  # WAIT — correction

    y_signal = df['market_trend'].apply(classify_signal)
    y_sig_train = y_signal.loc[train_indices]
    y_sig_test = y_signal.loc[test_indices]

    signal_model = XGBClassifier(
        n_estimators=300, random_state=random_state, n_jobs=-1,
        eval_metric='mlogloss'
    )
    signal_model.fit(X_train, y_sig_train)
    sig_pred = signal_model.predict(X_test)

    from sklearn.metrics import accuracy_score, classification_report
    results['signal_classifier'] = {
        'accuracy': round(float(accuracy_score(y_sig_test, sig_pred)), 4),
        'labels': {0: 'BUY', 1: 'HOLD', 2: 'SELL', 3: 'WAIT'}
    }
    with open(os.path.join(models_dir, 'signal_model.pkl'), 'wb') as f:
        pickle.dump(signal_model, f)
    print(f"   Accuracy: {results['signal_classifier']['accuracy']}")

    # ═══════════════════════════════════════════════════════
    # Save test predictions for evaluation
    # ═══════════════════════════════════════════════════════
    test_df = df.loc[test_indices].copy()
    test_df['predicted_price_lr'] = lr_pred
    test_df['predicted_price_dt'] = dt_pred
    test_df['predicted_price_rf'] = rf_pred
    test_df['predicted_price_xgb'] = xgb_pred
    test_df['predicted_roi'] = roi_pred
    test_df['predicted_signal'] = sig_pred

    test_df.to_csv('data/processed/test_predictions.csv', index=False)

    # Save full predictions for recommendation engine
    full_pred = xgb_model.predict(X.fillna(0))
    df['predicted_price'] = full_pred
    df['price_gap'] = df['price'] - df['predicted_price']
    df['price_gap_pct'] = ((df['price_gap'] / df['predicted_price']) * 100).round(2)
    df.to_csv('data/processed/production_final.csv', index=False)

    # Save training metadata
    meta = {
        'features': PRICE_FEATURES,
        'train_size': len(X_train),
        'test_size': len(X_test),
        'results': results,
        'best_model': 'xgboost',
        'best_r2': results['xgboost']['r2']
    }
    with open(os.path.join(models_dir, 'training_metadata.json'), 'w') as f:
        json.dump(meta, f, indent=2)

    print(f"\n{'='*50}")
    print(f"🏆 TRAINING SUMMARY")
    print(f"{'='*50}")
    for name, r in results.items():
        if name == 'signal_classifier':
            print(f"   {name}: Accuracy = {r['accuracy']}")
        else:
            print(f"   {name}: R² = {r['r2']} | RMSE = ₹{r.get('rmse', 'N/A'):,}")
    print(f"\n   Best: XGBoost (R² = {results['xgboost']['r2']})")
    print(f"   All models saved to: {models_dir}/")

    return results


if __name__ == '__main__':
    train_all_models()
