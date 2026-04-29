"""
Enhanced EDA Report Generator
===============================
Generates 10+ visualizations for exploratory data analysis.
"""

from datetime import datetime
import os
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')


def generate_eda_report(
    input_path='data/processed/feature_engineered.csv',
    assets_dir='ml/reports/assets',
    output_report='ml/reports/eda_report.html'
):
    df = pd.read_csv(input_path)
    os.makedirs(assets_dir, exist_ok=True)
    print(f" Loaded {len(df)} rows for EDA")

    plt.style.use('seaborn-v0_8-darkgrid')

    # 1. Price Distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df['price'] / 1e7, bins=50, color='#2563eb',
            alpha=0.7, edgecolor='#1e40af')
    ax.set_xlabel('Price (Rs. Cr)')
    ax.set_ylabel('Count')
    ax.set_title('Property Price Distribution — Bangalore',
                 fontweight='bold', fontsize=14)
    plt.tight_layout()
    plt.savefig(f'{assets_dir}/price_dist.png', dpi=150, bbox_inches='tight')
    plt.close()

    # 2. Price vs Sqft by Location
    fig, ax = plt.subplots(figsize=(12, 7))
    for loc in df['location'].unique():
        subset = df[df['location'] == loc]
        ax.scatter(subset['sqft'], subset['price'] /
                   1e7, alpha=0.3, s=10, label=loc)
    ax.set_xlabel('Square Feet')
    ax.set_ylabel('Price (Rs. Cr)')
    ax.set_title('Price vs Square Footage by Location',
                 fontweight='bold', fontsize=14)
    ax.legend(bbox_to_anchor=(1.05, 1), fontsize=7, markerscale=2)
    plt.tight_layout()
    plt.savefig(f'{assets_dir}/price_vs_sqft.png',
                dpi=150, bbox_inches='tight')
    plt.close()

    # 3. Correlation Heatmap
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    corr_cols = [c for c in numeric_cols if '_encoded' not in c][:15]
    fig, ax = plt.subplots(figsize=(14, 11))
    sns.heatmap(df[corr_cols].corr(), annot=True, cmap='RdBu_r', fmt='.2f',
                center=0, ax=ax, square=True, linewidths=0.5)
    ax.set_title('Correlation Heatmap', fontweight='bold', fontsize=14)
    plt.tight_layout()
    plt.savefig(f'{assets_dir}/correlation.png', dpi=150, bbox_inches='tight')
    plt.close()

    # 4. Boxplot per Location
    fig, ax = plt.subplots(figsize=(14, 6))
    location_order = df.groupby(
        'location')['price'].median().sort_values(ascending=False).index
    sns.boxplot(data=df, x='location', y='price', order=location_order,
                palette='viridis', ax=ax, fliersize=2)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    ax.set_ylabel('Price (Rs.)')
    ax.set_title('Price Distribution by Location',
                 fontweight='bold', fontsize=14)
    plt.tight_layout()
    plt.savefig(f'{assets_dir}/location_box.png', dpi=150, bbox_inches='tight')
    plt.close()

    # 5. Bedroom Distribution
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    df['bedrooms'].value_counts().sort_index().plot(
        kind='bar', color='#8b5cf6', ax=ax1)
    ax1.set_title('Bedroom Count Distribution', fontweight='bold')
    ax1.set_xlabel('Bedrooms')
    df.groupby('bedrooms')['price'].mean().plot(
        kind='bar', color='#10b981', ax=ax2)
    ax2.set_title('Average Price by Bedrooms', fontweight='bold')
    ax2.set_xlabel('Bedrooms')
    ax2.set_ylabel('Avg Price (Rs.)')
    plt.tight_layout()
    plt.savefig(f'{assets_dir}/bedroom_analysis.png',
                dpi=150, bbox_inches='tight')
    plt.close()

    # 6. Age vs Price
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(df['age'], df['price'] / 1e7, alpha=0.2, s=8, c='#f59e0b')
    age_avg = df.groupby('age')['price'].mean() / 1e7
    ax.plot(age_avg.index, age_avg.values,
            color='#ef4444', linewidth=2, label='Mean')
    ax.set_xlabel('Property Age (years)')
    ax.set_ylabel('Price (Rs. Cr)')
    ax.set_title('Age vs Price', fontweight='bold', fontsize=14)
    ax.legend()
    plt.tight_layout()
    plt.savefig(f'{assets_dir}/age_vs_price.png', dpi=150, bbox_inches='tight')
    plt.close()

    # 7. Distance Metro vs Price
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(df['distance_metro'], df['price'] /
               1e7, alpha=0.2, s=8, c='#2563eb')
    ax.set_xlabel('Distance to Metro (km)')
    ax.set_ylabel('Price (Rs. Cr)')
    ax.set_title('Metro Distance vs Price', fontweight='bold', fontsize=14)
    plt.tight_layout()
    plt.savefig(f'{assets_dir}/distance_vs_price.png',
                dpi=150, bbox_inches='tight')
    plt.close()

    # 8. Market Trend by Location
    fig, ax = plt.subplots(figsize=(12, 6))
    trend_avg = df.groupby('location')[
        'market_trend'].mean().sort_values(ascending=False)
    colors = ['#10b981' if v > 0.12 else '#2563eb' if v >
              0.08 else '#f59e0b' for v in trend_avg.values]
    trend_avg.plot(kind='bar', color=colors, ax=ax)
    ax.set_ylabel('Avg Market Trend')
    ax.set_title('Market Growth Trend by Location',
                 fontweight='bold', fontsize=14)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f'{assets_dir}/market_trend.png', dpi=150, bbox_inches='tight')
    plt.close()

    # 9. ROI Distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df['roi'], bins=40, color='#10b981',
            alpha=0.7, edgecolor='#059669')
    ax.axvline(df['roi'].mean(), color='#ef4444', linestyle='--',
               linewidth=2, label=f"Mean: {df['roi'].mean():.1f}%")
    ax.set_xlabel('ROI (%)')
    ax.set_title('ROI Distribution', fontweight='bold', fontsize=14)
    ax.legend()
    plt.tight_layout()
    plt.savefig(f'{assets_dir}/roi_distribution.png',
                dpi=150, bbox_inches='tight')
    plt.close()

    # 10. Demand vs Liquidity
    fig, ax = plt.subplots(figsize=(10, 7))
    scatter = ax.scatter(df['demand_score'], df['liquidity_score'],
                         c=df['price'] / 1e7, cmap='viridis', alpha=0.4, s=10)
    plt.colorbar(scatter, label='Price (Rs. Cr)')
    ax.set_xlabel('Demand Score')
    ax.set_ylabel('Liquidity Score')
    ax.set_title('Demand vs Liquidity (colored by Price)',
                 fontweight='bold', fontsize=14)
    plt.tight_layout()
    plt.savefig(f'{assets_dir}/demand_liquidity.png',
                dpi=150, bbox_inches='tight')
    plt.close()

    # Generate HTML Report
    plots = [
        ('Price Distribution', 'price_dist.png'),
        ('Price vs Square Footage', 'price_vs_sqft.png'),
        ('Correlation Heatmap', 'correlation.png'),
        ('Price by Location', 'location_box.png'),
        ('Bedroom Analysis', 'bedroom_analysis.png'),
        ('Age vs Price', 'age_vs_price.png'),
        ('Metro Distance vs Price', 'distance_vs_price.png'),
        ('Market Trend by Location', 'market_trend.png'),
        ('ROI Distribution', 'roi_distribution.png'),
        ('Demand vs Liquidity', 'demand_liquidity.png'),
    ]

    plots_html = ''
    for i, (title, fname) in enumerate(plots, 1):
        plots_html += f'''
 <div class="plot">
 <h2>{i}. {title}</h2>
 <img src="assets/{fname}" alt="{title}">
 </div>'''

    html = f"""<!DOCTYPE html>
<html>
<head>
 <title>EDA Report — Bangalore Real Estate</title>
 <style>
 body {{ font-family: 'Segoe UI', sans-serif; margin: 0; background: #0a0a0a; color: #fff; }}
 .container {{ max-width: 1200px; margin: auto; padding: 40px 20px; }}
 h1 {{ font-size: 2.5rem; margin-bottom: 8px; }}
 .subtitle {{ color: #888; margin-bottom: 40px; }}
 .plot {{ margin-bottom: 48px; }}
 h2 {{ color: #2563eb; font-size: 1.3rem; margin-bottom: 16px; }}
 img {{ max-width: 100%; border-radius: 12px; border: 1px solid #222; }}
 .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 40px; }}
 .stat-card {{ background: #141414; padding: 20px; border-radius: 12px; border: 1px solid #222; }}
 .stat-value {{ font-size: 1.5rem; font-weight: 800; }}
 .stat-label {{ font-size: 0.75rem; color: #888; margin-bottom: 4px; }}
 </style>
</head>
<body>
 <div class="container">
 <h1> Exploratory Data Analysis Report</h1>
 <p class="subtitle">Bangalore Real Estate Dataset — {len(df):,} Properties | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>

 <div class="stats">
 <div class="stat-card"><div class="stat-label">TOTAL PROPERTIES</div><div class="stat-value">{len(df):,}</div></div>
 <div class="stat-card"><div class="stat-label">LOCATIONS</div><div class="stat-value">{df['location'].nunique()}</div></div>
 <div class="stat-card"><div class="stat-label">AVG PRICE</div><div class="stat-value">Rs.{df['price'].mean()/1e7:.2f}Cr</div></div>
 <div class="stat-card"><div class="stat-label">AVG ROI</div><div class="stat-value">{df['roi'].mean():.1f}%</div></div>
 </div>

 {plots_html}
 </div>
</body>
</html>"""

    os.makedirs(os.path.dirname(output_report), exist_ok=True)
    with open(output_report, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n EDA Report: 10 plots saved to {assets_dir}/")
    print(f" HTML Report: {output_report}")
    return True


if __name__ == '__main__':
    generate_eda_report()
