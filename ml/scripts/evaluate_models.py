"""
Model Evaluation Pipeline
==========================
Generates metrics + diagnostic plots for all trained models.
"""

import pandas as pd
import numpy as np
import os
import json
import pickle
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


def evaluate_models(
 predictions_path='data/processed/test_predictions.csv',
 report_path='ml/reports/evaluation_report.json',
 assets_dir='ml/reports/assets'
):
 df = pd.read_csv(predictions_path)
 os.makedirs(assets_dir, exist_ok=True)
 y_true = df['price'].values

 models = {
 'Linear Regression': df['predicted_price_lr'].values,
 'Decision Tree': df['predicted_price_dt'].values,
 'Random Forest': df['predicted_price_rf'].values,
 'XGBoost': df['predicted_price_xgb'].values,
 }

 results = {}
 for name, y_pred in models.items():
 mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
 results[name] = {
 'rmse': round(float(np.sqrt(mean_squared_error(y_true, y_pred))), 2),
 'mae': round(float(mean_absolute_error(y_true, y_pred)), 2),
 'mape': round(float(mape), 2),
 'r2': round(float(r2_score(y_true, y_pred)), 4),
 }

 # PLOT 1: Model Comparison
 fig, axes = plt.subplots(1, 3, figsize=(18, 5))
 model_names = list(results.keys())
 colors = ['#6366f1', '#8b5cf6', '#a78bfa', '#2563eb']
 for idx, metric in enumerate(['rmse', 'mae', 'r2']):
 values = [results[m][metric] for m in model_names]
 axes[idx].bar(model_names, values, color=colors)
 axes[idx].set_title(metric.upper(), fontweight='bold', fontsize=14)
 axes[idx].tick_params(axis='x', rotation=25)
 for i, v in enumerate(values):
 axes[idx].text(i, v, f'{v:,.0f}' if metric != 'r2' else f'{v:.4f}', ha='center', va='bottom', fontsize=9)
 plt.suptitle('Model Comparison', fontsize=16, fontweight='bold')
 plt.tight_layout()
 plt.savefig(f'{assets_dir}/model_comparison.png', dpi=150, bbox_inches='tight')
 plt.close()

 xgb_pred = models['XGBoost']
 residuals = y_true - xgb_pred

 # PLOT 2: Residual Distribution
 fig, ax = plt.subplots(figsize=(10, 6))
 ax.hist(residuals, bins=50, color='#2563eb', alpha=0.7, edgecolor='#1e40af')
 ax.axvline(0, color='#ef4444', linestyle='--', linewidth=2)
 ax.axvline(np.mean(residuals), color='#f59e0b', linestyle='--', linewidth=2)
 ax.set_xlabel('Residual (Actual - Predicted)')
 ax.set_title('Residual Distribution — XGBoost', fontweight='bold')
 plt.tight_layout()
 plt.savefig(f'{assets_dir}/residual_distribution.png', dpi=150, bbox_inches='tight')
 plt.close()

 # PLOT 3: Residual vs Predicted
 fig, ax = plt.subplots(figsize=(10, 6))
 ax.scatter(xgb_pred, residuals, alpha=0.3, s=8, c='#2563eb')
 ax.axhline(0, color='#ef4444', linestyle='--')
 ax.set_xlabel('Predicted Price')
 ax.set_ylabel('Residual')
 ax.set_title('Residuals vs Predicted — XGBoost', fontweight='bold')
 plt.tight_layout()
 plt.savefig(f'{assets_dir}/residual_vs_predicted.png', dpi=150, bbox_inches='tight')
 plt.close()

 # PLOT 4: Actual vs Predicted
 fig, ax = plt.subplots(figsize=(10, 8))
 ax.scatter(y_true, xgb_pred, alpha=0.3, s=8, c='#2563eb')
 lims = [min(y_true.min(), xgb_pred.min()), max(y_true.max(), xgb_pred.max())]
 ax.plot(lims, lims, '--', color='#ef4444', linewidth=2)
 ax.set_xlabel('Actual Price')
 ax.set_ylabel('Predicted Price')
 ax.set_title('Actual vs Predicted — XGBoost', fontweight='bold')
 plt.tight_layout()
 plt.savefig(f'{assets_dir}/actual_vs_predicted.png', dpi=150, bbox_inches='tight')
 plt.close()

 # PLOT 5: Location-wise Error
 df['abs_error'] = np.abs(residuals)
 loc_error = df.groupby('location')['abs_error'].mean().sort_values(ascending=False)
 fig, ax = plt.subplots(figsize=(12, 6))
 ax.barh(loc_error.index, loc_error.values, color='#8b5cf6')
 ax.set_xlabel('Mean Absolute Error')
 ax.set_title('Location-wise MAE — XGBoost', fontweight='bold')
 plt.tight_layout()
 plt.savefig(f'{assets_dir}/location_error.png', dpi=150, bbox_inches='tight')
 plt.close()

 # PLOT 6: High-Error Segment Analysis
 threshold = df['abs_error'].quantile(0.95)
 high_error = df[df['abs_error'] >= threshold]
 high_error_analysis = {
 'count': len(high_error),
 'threshold': round(float(threshold), 2),
 'by_location': high_error['location'].value_counts().head(10).to_dict(),
 'by_property_type': high_error['property_type'].value_counts().to_dict(),
 }
 fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
 lc = high_error['location'].value_counts().head(10)
 ax1.bar(range(len(lc)), lc.values, color='#ef4444')
 ax1.set_xticks(range(len(lc)))
 ax1.set_xticklabels(lc.index, rotation=45, ha='right', fontsize=8)
 ax1.set_title('High-Error by Location', fontweight='bold')
 tc = high_error['property_type'].value_counts()
 ax2.bar(range(len(tc)), tc.values, color='#f59e0b')
 ax2.set_xticks(range(len(tc)))
 ax2.set_xticklabels(tc.index, rotation=30, ha='right')
 ax2.set_title('High-Error by Type', fontweight='bold')
 plt.tight_layout()
 plt.savefig(f'{assets_dir}/high_error_analysis.png', dpi=150, bbox_inches='tight')
 plt.close()

 # PLOT 7: Feature Importance
 try:
 with open('ml/models/price_model.pkl', 'rb') as f:
 xgb_model = pickle.load(f)
 feat_names = [
 'sqft', 'bedrooms', 'bathrooms', 'balconies', 'parking',
 'age', 'floor', 'total_floors', 'amenities_count',
 'dist_metro', 'dist_school', 'dist_hospital', 'dist_cbd',
 'loc_score', 'luxury_score', 'amenity_idx', 'prox_score',
 'age_bucket', 'furnish', 'loc_enc', 'builder_enc',
 'type_enc', 'furnish_enc', 'listing_enc'
 ]
 imp = pd.Series(xgb_model.feature_importances_, index=feat_names).sort_values().tail(15)
 fig, ax = plt.subplots(figsize=(10, 8))
 imp.plot(kind='barh', color='#10b981', ax=ax)
 ax.set_title('Top 15 Feature Importances — XGBoost', fontweight='bold')
 plt.tight_layout()
 plt.savefig(f'{assets_dir}/feature_importance.png', dpi=150, bbox_inches='tight')
 plt.close()
 except Exception as e:
 print(f" Feature importance skipped: {e}")

 # Save report
 report = {
 'model_metrics': results,
 'best_model': max(results, key=lambda k: results[k]['r2']),
 'best_r2': max(r['r2'] for r in results.values()),
 'high_error_analysis': high_error_analysis,
 'residual_stats': {
 'mean': round(float(np.mean(residuals)), 2),
 'std': round(float(np.std(residuals)), 2),
 },
 }
 os.makedirs(os.path.dirname(report_path), exist_ok=True)
 with open(report_path, 'w') as f:
 json.dump(report, f, indent=2)

 print(f"\n{'='*50}")
 print(f" EVALUATION SUMMARY")
 print(f"{'='*50}")
 for name, r in results.items():
 print(f" {name}: R²={r['r2']} | RMSE=₹{r['rmse']:,} | MAPE={r['mape']}%")
 print(f" Best: {report['best_model']} (R²={report['best_r2']})")
 print(f" 7 plots saved to: {assets_dir}/")
 return report


if __name__ == '__main__':
 evaluate_models()
