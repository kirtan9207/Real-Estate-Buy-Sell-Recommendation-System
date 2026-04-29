"""
Executive Report Generator
============================
Auto-generates a comprehensive HTML report with project summary,
data overview, model comparison, key findings, and recommendations.
"""

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime


def generate_executive_report(
    data_path='data/processed/production_final.csv',
    eval_path='ml/reports/evaluation_report.json',
    baseline_path='ml/reports/baseline_results.json',
    cleaning_path='ml/reports/cleaning_report.json',
    cluster_path='ml/reports/clustering_report.json',
    rec_path='ml/reports/recommendation_report.json',
    output_path='ml/reports/executive_report.html',
    assets_dir='ml/reports/assets'
):
    df = pd.read_csv(data_path)

    # Load reports
    def load_json(path):
        try:
            with open(path) as f:
                return json.load(f)
        except:
            return {}

    eval_report = load_json(eval_path)
    baseline = load_json(baseline_path)
    cleaning = load_json(cleaning_path)
    cluster_report = load_json(cluster_path)
    rec_report = load_json(rec_path)

    # Compute KPIs
    total_props = len(df)
    avg_price = df['price'].mean()
    locations = df['location'].nunique()
    best_roi_loc = df.groupby('location')['roi'].mean().idxmax()
    best_roi_val = df.groupby('location')['roi'].mean().max()

    underpriced_count = len(df[df.get('valuation_label', pd.Series()) == 'Underpriced']) if 'valuation_label' in df.columns else 0
    best_model = eval_report.get('best_model', 'XGBoost')
    best_r2 = eval_report.get('best_r2', 'N/A')

    # Model metrics table
    metrics = eval_report.get('model_metrics', {})
    metrics_rows = ''
    for model, m in metrics.items():
        metrics_rows += f"""
        <tr>
            <td>{model}</td>
            <td>₹{m.get('rmse', 0):,.0f}</td>
            <td>₹{m.get('mae', 0):,.0f}</td>
            <td>{m.get('mape', 0):.1f}%</td>
            <td><strong>{m.get('r2', 0):.4f}</strong></td>
        </tr>"""

    # Baseline metrics
    baseline_rows = ''
    for bname in ['global_mean', 'global_median', 'location_mean']:
        b = baseline.get(bname, {})
        baseline_rows += f"""
        <tr>
            <td>{bname.replace('_', ' ').title()}</td>
            <td>₹{b.get('rmse', 0):,.0f}</td>
            <td>₹{b.get('mae', 0):,.0f}</td>
            <td>{b.get('r2', 0):.4f}</td>
        </tr>"""

    # Location summary
    loc_summary = df.groupby('location').agg({
        'price': 'mean', 'roi': 'mean', 'market_trend': 'mean', 'demand_score': 'mean'
    }).round(2).sort_values('roi', ascending=False)

    loc_rows = ''
    for loc, row in loc_summary.iterrows():
        trend_label = '🔥 Hot' if row['market_trend'] > 0.12 else '📈 Warm' if row['market_trend'] > 0.08 else '📉 Cool'
        loc_rows += f"""
        <tr>
            <td>{loc}</td>
            <td>₹{row['price']/1e7:.2f}Cr</td>
            <td>{row['roi']:.1f}%</td>
            <td>{trend_label}</td>
            <td>{row['demand_score']:.0f}</td>
        </tr>"""

    # Signal distribution
    signal_dist = rec_report.get('sell_signal_distribution', {})
    signal_html = ' | '.join([f"<span class='tag'>{k}: {v}</span>" for k, v in signal_dist.items()])

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Executive Report — Bangalore Real Estate Intelligence</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #0a0a0a; color: #e0e0e0; line-height: 1.6; }}
        .container {{ max-width: 1100px; margin: auto; padding: 40px 24px; }}
        h1 {{ font-size: 2.2rem; color: #fff; margin-bottom: 4px; }}
        h2 {{ font-size: 1.4rem; color: #2563eb; margin: 40px 0 16px; border-bottom: 1px solid #222; padding-bottom: 8px; }}
        h3 {{ font-size: 1.1rem; color: #a78bfa; margin: 24px 0 8px; }}
        .subtitle {{ color: #888; margin-bottom: 32px; }}
        .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 32px; }}
        .kpi {{ background: #141414; border: 1px solid #222; border-radius: 12px; padding: 20px; }}
        .kpi-label {{ font-size: 0.7rem; color: #888; text-transform: uppercase; letter-spacing: 1px; }}
        .kpi-value {{ font-size: 1.6rem; font-weight: 800; margin-top: 4px; }}
        .kpi-value.green {{ color: #10b981; }}
        .kpi-value.blue {{ color: #2563eb; }}
        table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
        th {{ background: #1a1a1a; color: #888; text-align: left; padding: 12px 16px; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; }}
        td {{ padding: 10px 16px; border-bottom: 1px solid #1a1a1a; font-size: 0.9rem; }}
        tr:hover {{ background: #141414; }}
        .card {{ background: #141414; border: 1px solid #222; border-radius: 12px; padding: 24px; margin-bottom: 24px; }}
        .tag {{ display: inline-block; background: rgba(37,99,235,0.1); color: #2563eb; padding: 4px 10px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; margin: 2px; }}
        .highlight {{ background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); border-radius: 8px; padding: 16px; margin: 16px 0; }}
        img {{ max-width: 100%; border-radius: 10px; border: 1px solid #222; margin: 12px 0; }}
        .plot-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
        .footer {{ text-align: center; color: #555; font-size: 0.8rem; margin-top: 60px; padding-top: 20px; border-top: 1px solid #222; }}
    </style>
</head>
<body>
<div class="container">

    <h1>🏗️ Executive Intelligence Report</h1>
    <p class="subtitle">Bangalore Real Estate Buy/Sell Recommendation System — Generated: {datetime.now().strftime('%B %d, %Y')}</p>

    <div class="kpi-grid">
        <div class="kpi"><div class="kpi-label">Total Properties</div><div class="kpi-value">{total_props:,}</div></div>
        <div class="kpi"><div class="kpi-label">Avg Market Price</div><div class="kpi-value blue">₹{avg_price/1e7:.2f}Cr</div></div>
        <div class="kpi"><div class="kpi-label">Best ROI Location</div><div class="kpi-value green">{best_roi_loc}</div></div>
        <div class="kpi"><div class="kpi-label">Model R² Score</div><div class="kpi-value green">{best_r2}</div></div>
    </div>

    <h2>1. Project Overview</h2>
    <div class="card">
        <p>This system analyzes <strong>{total_props:,}</strong> property listings across <strong>{locations}</strong> Bangalore localities. It uses machine learning to predict property prices, detect undervalued investment opportunities, match buyer preferences, and generate buy/sell/hold signals.</p>
        <h3>Pipeline Flow</h3>
        <p>Data Generation → Cleaning → Feature Engineering → Baseline Models → Primary Models → Evaluation → Recommendations → Clustering → Dashboard</p>
    </div>

    <h2>2. Data Cleaning Summary</h2>
    <div class="card">
        <p>Initial: <strong>{cleaning.get('initial_shape', {}).get('rows', 'N/A')}</strong> rows → Final: <strong>{cleaning.get('final_shape', {}).get('rows', 'N/A')}</strong> rows</p>
        <p>Retention Rate: <strong>{cleaning.get('summary', {}).get('retention_rate', 'N/A')}%</strong></p>
    </div>

    <h2>3. Baseline Model Results</h2>
    <table>
        <thead><tr><th>Baseline</th><th>RMSE</th><th>MAE</th><th>R²</th></tr></thead>
        <tbody>{baseline_rows}</tbody>
    </table>

    <h2>4. Model Comparison</h2>
    <table>
        <thead><tr><th>Model</th><th>RMSE</th><th>MAE</th><th>MAPE</th><th>R²</th></tr></thead>
        <tbody>{metrics_rows}</tbody>
    </table>
    <div class="highlight">
        <strong>🏆 Best Model:</strong> {best_model} with R² = {best_r2}
    </div>

    <h2>5. Diagnostic Plots</h2>
    <div class="plot-grid">
        <div><img src="assets/model_comparison.png" alt="Model Comparison"></div>
        <div><img src="assets/actual_vs_predicted.png" alt="Actual vs Predicted"></div>
        <div><img src="assets/residual_distribution.png" alt="Residual Distribution"></div>
        <div><img src="assets/feature_importance.png" alt="Feature Importance"></div>
        <div><img src="assets/location_error.png" alt="Location Error"></div>
        <div><img src="assets/cluster_scatter.png" alt="Market Segments"></div>
    </div>

    <h2>6. Location Intelligence</h2>
    <table>
        <thead><tr><th>Location</th><th>Avg Price</th><th>Avg ROI</th><th>Trend</th><th>Demand</th></tr></thead>
        <tbody>{loc_rows}</tbody>
    </table>

    <h2>7. Investment Signals</h2>
    <div class="card">
        <p><strong>Underpriced Properties Detected:</strong> {underpriced_count}</p>
        <p><strong>Signal Distribution:</strong> {signal_html}</p>
    </div>

    <h2>8. Key Recommendations</h2>
    <div class="card">
        <h3>🟢 Buy Recommendations</h3>
        <p>Focus on <strong>{best_roi_loc}</strong> and other emerging locations with ROI > 15%. Target underpriced properties with gap > 10% below predicted value.</p>
        <h3>🟡 Hold Recommendations</h3>
        <p>Properties in mid-range locations showing steady 8-12% growth trends. Continue holding for appreciation.</p>
        <h3>🔴 Sell Considerations</h3>
        <p>Premium locations with slowing growth (< 7%). Properties where actual price exceeds predicted by > 10% (overpriced).</p>
    </div>

    <div class="footer">
        <p>Bangalore Real Estate Buy/Sell Recommendation System — Data Science Project Report</p>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</div>
</body>
</html>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html)

    print(f"\n✅ Executive Report generated: {output_path}")
    return output_path


if __name__ == '__main__':
    generate_executive_report()
