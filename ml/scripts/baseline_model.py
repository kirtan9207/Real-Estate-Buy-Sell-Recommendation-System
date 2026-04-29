"""
Baseline Model Evaluation
==========================
Establishes naive baselines for price prediction:
1. Global Mean baseline
2. Global Median baseline
3. Location-wise Mean baseline
Reports RMSE, MAE, R² for each.
"""

import pandas as pd
import numpy as np
import os
import json
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


def run_baselines(
    input_path='data/processed/feature_engineered.csv',
    report_path='ml/reports/baseline_results.json'
):
    df = pd.read_csv(input_path)
    y_true = df['price'].values

    results = {}

    # ═══════════════════════════════════════════════════════
    # 1. Global Mean Baseline
    # ═══════════════════════════════════════════════════════
    mean_pred = np.full_like(y_true, y_true.mean(), dtype=float)
    results['global_mean'] = {
        'strategy': 'Predict mean price for all properties',
        'predicted_value': round(float(y_true.mean()), 2),
        'rmse': round(float(np.sqrt(mean_squared_error(y_true, mean_pred))), 2),
        'mae': round(float(mean_absolute_error(y_true, mean_pred)), 2),
        'r2': round(float(r2_score(y_true, mean_pred)), 4),
    }

    # ═══════════════════════════════════════════════════════
    # 2. Global Median Baseline
    # ═══════════════════════════════════════════════════════
    median_val = np.median(y_true)
    median_pred = np.full_like(y_true, median_val, dtype=float)
    results['global_median'] = {
        'strategy': 'Predict median price for all properties',
        'predicted_value': round(float(median_val), 2),
        'rmse': round(float(np.sqrt(mean_squared_error(y_true, median_pred))), 2),
        'mae': round(float(mean_absolute_error(y_true, median_pred)), 2),
        'r2': round(float(r2_score(y_true, median_pred)), 4),
    }

    # ═══════════════════════════════════════════════════════
    # 3. Location-wise Mean Baseline
    # ═══════════════════════════════════════════════════════
    location_means = df.groupby('location')['price'].mean()
    loc_pred = df['location'].map(location_means).values
    results['location_mean'] = {
        'strategy': 'Predict location-specific mean price',
        'location_means': {k: round(v, 2) for k, v in location_means.items()},
        'rmse': round(float(np.sqrt(mean_squared_error(y_true, loc_pred))), 2),
        'mae': round(float(mean_absolute_error(y_true, loc_pred)), 2),
        'r2': round(float(r2_score(y_true, loc_pred)), 4),
    }

    # ═══════════════════════════════════════════════════════
    # Summary
    # ═══════════════════════════════════════════════════════
    results['comparison'] = {
        'best_baseline': min(results, key=lambda k: results[k]['rmse'] if k != 'comparison' else float('inf')),
        'note': 'Any ML model must beat the best baseline to be useful.'
    }

    # Save report
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*50}")
    print(f" BASELINE RESULTS")
    print(f"{'='*50}")
    for name in ['global_mean', 'global_median', 'location_mean']:
        r = results[name]
        print(f"\n {name.upper()}")
        print(f" RMSE: Rs.{r['rmse']:,.0f}")
        print(f" MAE: Rs.{r['mae']:,.0f}")
        print(f" R²: {r['r2']}")

    print(f"\n Best baseline: {results['comparison']['best_baseline']}")
    print(f" Saved to: {report_path}")

    return results


if __name__ == '__main__':
    run_baselines()
