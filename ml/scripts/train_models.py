import pandas as pd
import numpy as np
import os
import pickle
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

def train_models(input_path='data/processed/feature_engineered_properties.csv'):
    df = pd.read_csv(input_path)
    
    # Features for price prediction
    features = [
        'sqft', 'bedrooms', 'bathrooms', 'balconies', 'parking', 'age', 
        'floor', 'total_floors', 'furnished', 'amenities_count', 
        'distance_metro', 'distance_school', 'distance_hospital',
        'location_encoded', 'age_bucket_encoded', 'luxury_score', 'roi'
    ]
    
    X = df[features]
    y = df['price']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    models = {
        'Linear Regression': LinearRegression(),
        'Ridge': Ridge(),
        'Lasso': Lasso(),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingRegressor(random_state=42),
        'XGBoost': XGBRegressor(random_state=42)
    }
    
    results = {}
    best_rmse = float('inf')
    best_model_name = ""
    best_model = None
    
    # Baseline models
    y_mean = np.full_like(y_test, y_train.mean())
    results['Baseline (Mean)'] = {
        'RMSE': np.sqrt(mean_squared_error(y_test, y_mean)),
        'MAE': mean_absolute_error(y_test, y_mean),
        'R2': r2_score(y_test, y_mean)
    }
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)
        
        results[name] = {'RMSE': rmse, 'MAE': mae, 'R2': r2}
        
        if rmse < best_rmse:
            best_rmse = rmse
            best_model_name = name
            best_model = model
            
    print(f"Best Model: {best_model_name} with RMSE: {best_rmse}")
    
    # Save best model
    os.makedirs('ml/models', exist_ok=True)
    with open('ml/models/price_model.pkl', 'wb') as f:
        pickle.dump(best_model, f)
        
    # 2. Market Segmentation using KMeans
    segment_features = ['price_per_sqft', 'location_score', 'roi', 'amenity_score', 'market_trend']
    kmeans = KMeans(n_clusters=4, random_state=42)
    df['cluster'] = kmeans.fit_transform(df[segment_features]).argmin(axis=1) # Simplified label assignment
    
    # Map clusters to labels
    # Logic: Sort clusters by median price
    cluster_prices = df.groupby('cluster')['price'].median().sort_values()
    cluster_mapping = {
        cluster_prices.index[0]: 'Budget',
        cluster_prices.index[1]: 'Mid Range',
        cluster_prices.index[2]: 'Premium',
        cluster_prices.index[3]: 'Emerging'
    }
    df['cluster_label'] = df['cluster'].map(cluster_mapping)
    
    with open('ml/models/cluster_model.pkl', 'wb') as f:
        pickle.dump(kmeans, f)
        
    # Save data with clusters
    df.to_csv('data/processed/final_dataset.csv', index=False)
    
    # 3. Model Evaluation Report
    generate_eval_report(best_model, X_test, y_test, results, best_model_name)
    
    print("Model training and evaluation complete.")

def generate_eval_report(model, X_test, y_test, results, best_name):
    preds = model.predict(X_test)
    residuals = y_test - preds
    
    os.makedirs('ml/reports/assets', exist_ok=True)
    
    # Feature Importance
    if hasattr(model, 'feature_importances_'):
        plt.figure(figsize=(10, 8))
        feat_importances = pd.Series(model.feature_importances_, index=X_test.columns)
        feat_importances.nlargest(10).plot(kind='barh')
        plt.title('Top 10 Feature Importances')
        plt.savefig('ml/reports/assets/feature_importance.png')
        plt.close()
    
    # Residual Plot
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=preds, y=residuals)
    plt.axhline(y=0, color='r', linestyle='--')
    plt.xlabel('Predicted')
    plt.ylabel('Residuals')
    plt.title('Residuals vs Predicted')
    plt.savefig('ml/reports/assets/residuals.png')
    plt.close()
    
    # Results Table HTML
    res_df = pd.DataFrame(results).T
    
    html_content = f"""
    <html>
    <head>
        <title>Model Evaluation Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 30px; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #007bff; color: white; }}
            .container {{ max-width: 1000px; margin: auto; }}
            .metric-box {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            img {{ max-width: 100%; margin-top: 20px; border: 1px solid #eee; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Model Evaluation Report</h1>
            <div class="metric-box">
                <h2>Best Performing Model: {best_name}</h2>
            </div>
            
            <h2>Model Comparison</h2>
            {res_df.to_html(classes='table')}
            
            <div class="plot">
                <h2>Feature Importance</h2>
                <img src="assets/feature_importance.png">
            </div>
            
            <div class="plot">
                <h2>Residual Analysis</h2>
                <img src="assets/residuals.png">
            </div>
        </div>
    </body>
    </html>
    """
    with open('ml/reports/evaluation_report.html', 'w') as f:
        f.write(html_content)

if __name__ == "__main__":
    train_models()
