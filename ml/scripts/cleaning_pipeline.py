"""
Data Cleaning Pipeline
=======================
Comprehensive cleaning with full diagnostics:
- Missing values analysis
- Duplicate detection
- Outlier detection (IQR on price_per_sqft)
- Leakage checks
- Before/after row counts at each step
- Cleaning report saved as JSON
"""

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime


def run_cleaning_pipeline(
    input_path='data/raw/bangalore_properties.csv',
    output_path='data/processed/cleaned_properties.csv',
    report_path='ml/reports/cleaning_report.json'
):
    report = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'input_file': input_path,
        'steps': []
    }

    # ── Load data ──
    df = pd.read_csv(input_path)
    initial_rows = len(df)
    initial_cols = len(df.columns)
    report['initial_shape'] = {'rows': initial_rows, 'columns': initial_cols}
    print(f" Loaded {initial_rows} rows × {initial_cols} columns")

    # ═══════════════════════════════════════════════════════
    # STEP 1: Missing Values Analysis
    # ═══════════════════════════════════════════════════════
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_report = {
        col: {'count': int(missing[col]),
              'percentage': float(missing_pct[col])}
        for col in df.columns if missing[col] > 0
    }

    # Impute missing values
    rows_before = len(df)
    for col in df.columns:
        if df[col].isnull().any():
            if df[col].dtype in [np.float64, np.int64]:
                df[col].fillna(df[col].median(), inplace=True)
            else:
                df[col].fillna(df[col].mode()[0], inplace=True)

    report['steps'].append({
        'step': 'Missing Values Analysis',
        'missing_columns': missing_report,
        'total_missing_cells': int(missing.sum()),
        'strategy': 'Median for numeric, Mode for categorical',
        'rows_before': rows_before,
        'rows_after': len(df),
        'rows_removed': 0
    })
    print(f" Step 1: Missing values — {int(missing.sum())} cells imputed")

    # ═══════════════════════════════════════════════════════
    # STEP 2: Duplicate Detection
    # ═══════════════════════════════════════════════════════
    rows_before = len(df)

    # Exact duplicates by property_id
    id_dupes = df.duplicated(subset=['property_id'], keep='first').sum()
    df.drop_duplicates(subset=['property_id'], keep='first', inplace=True)

    # Near-duplicates by key features
    feature_dupes = df.duplicated(
        subset=['location', 'sqft', 'bedrooms', 'price', 'builder_name'],
        keep='first'
    ).sum()
    df.drop_duplicates(
        subset=['location', 'sqft', 'bedrooms', 'price', 'builder_name'],
        keep='first', inplace=True
    )

    report['steps'].append({
        'step': 'Duplicate Detection',
        'id_duplicates': int(id_dupes),
        'feature_duplicates': int(feature_dupes),
        'rows_before': rows_before,
        'rows_after': len(df),
        'rows_removed': rows_before - len(df)
    })
    print(
        f" Step 2: Duplicates — {rows_before - len(df)} removed (ID: {id_dupes}, Feature: {feature_dupes})")

    # ═══════════════════════════════════════════════════════
    # STEP 3: Outlier Detection (IQR on price_per_sqft)
    # ═══════════════════════════════════════════════════════
    rows_before = len(df)
    df['price_per_sqft'] = df['price'] / df['sqft']

    outlier_details = {}

    def remove_location_outliers(group):
        loc_name = group['location'].iloc[0]
        q1 = group['price_per_sqft'].quantile(0.25)
        q3 = group['price_per_sqft'].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        before = len(group)
        filtered = group[(group['price_per_sqft'] >= lower) &
                         (group['price_per_sqft'] <= upper)]
        outlier_details[loc_name] = {
            'before': before,
            'after': len(filtered),
            'outliers_removed': before - len(filtered),
            'iqr_lower': round(lower, 2),
            'iqr_upper': round(upper, 2)
        }
        return filtered

    df = df.groupby('location', group_keys=False).apply(
        remove_location_outliers).reset_index(drop=True)

    total_outliers = rows_before - len(df)
    report['steps'].append({
        'step': 'Outlier Detection (IQR on price_per_sqft)',
        'method': 'IQR 1.5x per location group',
        'location_details': outlier_details,
        'total_outliers_removed': total_outliers,
        'rows_before': rows_before,
        'rows_after': len(df),
        'rows_removed': total_outliers
    })
    print(
        f" Step 3: Outliers — {total_outliers} removed across {len(outlier_details)} locations")

    # ═══════════════════════════════════════════════════════
    # STEP 4: Data Validation
    # ═══════════════════════════════════════════════════════
    rows_before = len(df)
    validations = []

    # Price must be positive
    invalid_price = (df['price'] <= 0).sum()
    df = df[df['price'] > 0]
    validations.append(f"Removed {invalid_price} rows with price <= 0")

    # Sqft must be positive
    invalid_sqft = (df['sqft'] <= 0).sum()
    df = df[df['sqft'] > 0]
    validations.append(f"Removed {invalid_sqft} rows with sqft <= 0")

    # Bedrooms must be non-negative
    invalid_bed = (df['bedrooms'] < 0).sum()
    df = df[df['bedrooms'] >= 0]
    validations.append(f"Removed {invalid_bed} rows with bedrooms < 0")

    # Floor <= total_floors (for non-plots)
    non_plot = df[df['property_type'] != 'Plot']
    invalid_floor = (non_plot['floor'] > non_plot['total_floors']).sum()
    df = df[~((df['property_type'] != 'Plot') &
              (df['floor'] > df['total_floors']))]
    validations.append(
        f"Removed {invalid_floor} rows with floor > total_floors")

    report['steps'].append({
        'step': 'Data Validation',
        'validations': validations,
        'rows_before': rows_before,
        'rows_after': len(df),
        'rows_removed': rows_before - len(df)
    })
    print(
        f" Step 4: Validation — {rows_before - len(df)} invalid rows removed")

    # ═══════════════════════════════════════════════════════
    # STEP 5: Leakage Check
    # ═══════════════════════════════════════════════════════
    # Check if any feature has suspiciously high correlation with target
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if 'price' in numeric_cols:
        correlations = df[numeric_cols].corr(
    )['price'].abs().sort_values(ascending=False)
    high_corr = correlations[(correlations > 0.95) &
                             (correlations.index != 'price')]
    leakage_cols = high_corr.index.tolist()

    # price_per_sqft is derived from price, so it's expected leakage
    leakage_cols = [c for c in leakage_cols if c != 'price_per_sqft']

    report['steps'].append({
        'step': 'Leakage Check',
        'method': 'Correlation > 0.95 with target (price)',
        'flagged_columns': leakage_cols,
        'note': 'price_per_sqft excluded (known derived feature)',
        'action': 'No leakage columns removed' if len(leakage_cols) == 0 else f'Flagged: {leakage_cols}',
        'rows_before': len(df),
        'rows_after': len(df),
        'rows_removed': 0
    })
    print(
        f" Step 5: Leakage check — {'No leakage detected' if not leakage_cols else f'Flagged: {leakage_cols}'}")

    # ═══════════════════════════════════════════════════════
    # STEP 6: Date Parsing & Final Cleanup
    # ═══════════════════════════════════════════════════════
    df['listing_date'] = pd.to_datetime(df['listing_date'])
    df['listing_year'] = df['listing_date'].dt.year
    df['listing_month'] = df['listing_date'].dt.month

    # Recalculate price_per_sqft after cleaning
    df['price_per_sqft'] = (df['price'] / df['sqft']).round(2)

    report['steps'].append({
        'step': 'Date Parsing & Final Cleanup',
        'new_columns': ['listing_year', 'listing_month', 'price_per_sqft (recalculated)'],
        'rows_before': len(df),
        'rows_after': len(df),
        'rows_removed': 0
    })

    # ═══════════════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════════════
    final_rows = len(df)
    report['final_shape'] = {'rows': final_rows, 'columns': len(df.columns)}
    report['summary'] = {
        'total_rows_removed': initial_rows - final_rows,
        'retention_rate': round(final_rows / initial_rows * 100, 2),
        'columns_added': len(df.columns) - initial_cols
    }

    # Save cleaned data
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    # Save report
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n{'='*50}")
    print(f" CLEANING SUMMARY")
    print(f"{'='*50}")
    print(f" Input: {initial_rows} rows")
    print(f" Output: {final_rows} rows")
    print(
        f" Removed: {initial_rows - final_rows} rows ({100 - report['summary']['retention_rate']:.2f}%)")
    print(f" Retention: {report['summary']['retention_rate']}%")
    print(f" Saved to: {output_path}")
    print(f" Report: {report_path}")

    return df


if __name__ == '__main__':
    run_cleaning_pipeline()
