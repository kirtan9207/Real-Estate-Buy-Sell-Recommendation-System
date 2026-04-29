"""
Market Clustering & Segmentation
==================================
- KMeans clustering on price, ROI, location_score, luxury_score, demand_score
- Elbow method + silhouette score validation
- Cluster visualization (scatter + summary)
"""

from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import pickle
import json
import matplotlib
matplotlib.use('Agg')


def run_clustering(
    input_path='data/processed/production_final.csv',
    models_dir='ml/models',
    assets_dir='ml/reports/assets',
    report_path='ml/reports/clustering_report.json',
    n_clusters=4
):
    df = pd.read_csv(input_path)
    os.makedirs(assets_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)
    print(f" Loaded {len(df)} rows for clustering")

    cluster_features = ['price', 'roi',
                        'location_score', 'luxury_score', 'demand_score']
    X = df[cluster_features].fillna(0)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # ═══════════════════════════════════════════════════════
    # Elbow Method
    # ═══════════════════════════════════════════════════════
    inertias = []
    sil_scores = []
    k_range = range(2, 9)
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init='auto')
        labels = km.fit_predict(X_scaled)
        inertias.append(km.inertia_)
        sil_scores.append(round(silhouette_score(X_scaled, labels), 4))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    ax1.plot(list(k_range), inertias, 'bo-', linewidth=2)
    ax1.set_xlabel('Number of Clusters (k)')
    ax1.set_ylabel('Inertia')
    ax1.set_title('Elbow Method', fontweight='bold')
    ax2.plot(list(k_range), sil_scores, 'go-', linewidth=2)
    ax2.set_xlabel('Number of Clusters (k)')
    ax2.set_ylabel('Silhouette Score')
    ax2.set_title('Silhouette Analysis', fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{assets_dir}/elbow_silhouette.png',
                dpi=150, bbox_inches='tight')
    plt.close()

    # ═══════════════════════════════════════════════════════
    # Final Clustering
    # ═══════════════════════════════════════════════════════
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
    df['cluster'] = kmeans.fit_predict(X_scaled)

    # Map clusters to meaningful labels
    cluster_means = df.groupby('cluster')['price'].mean().sort_values()
    label_map = {}
    segment_names = ['Budget', 'Mid-range', 'Premium', 'Emerging High-Growth']
    for i, (cluster_id, _) in enumerate(cluster_means.items()):
        if i < len(segment_names):
            label_map[cluster_id] = segment_names[i]
        else:
            label_map[cluster_id] = f'Segment-{i}'

    df['segment_label'] = df['cluster'].map(label_map)

    # ═══════════════════════════════════════════════════════
    # Cluster Visualization
    # ═══════════════════════════════════════════════════════
    colors_map = {'Budget': '#6366f1', 'Mid-range': '#2563eb',
                  'Premium': '#f59e0b', 'Emerging High-Growth': '#10b981'}

    fig, ax = plt.subplots(figsize=(12, 8))
    for seg in df['segment_label'].unique():
        subset = df[df['segment_label'] == seg]
    ax.scatter(subset['price'] / 1e7, subset['roi'],
               s=15, alpha=0.4, label=seg,
               color=colors_map.get(seg, '#888'))
    ax.set_xlabel('Price (Rs. Cr)', fontsize=12)
    ax.set_ylabel('ROI (%)', fontsize=12)
    ax.set_title('Market Segmentation — Price vs ROI',
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(f'{assets_dir}/cluster_scatter.png',
                dpi=150, bbox_inches='tight')
    plt.close()

    # Segment summary
    seg_summary = df.groupby('segment_label').agg({
        'price': ['mean', 'median', 'count'],
        'roi': 'mean',
        'location_score': 'mean',
        'luxury_score': 'mean',
        'demand_score': 'mean',
    }).round(2)
    seg_summary.columns = ['avg_price', 'median_price', 'count', 'avg_roi',
                           'avg_location_score', 'avg_luxury_score', 'avg_demand_score']

    # Location-cluster mapping
    loc_cluster = df.groupby(
        ['location', 'segment_label']).size().unstack(fill_value=0)

    # Save
    with open(os.path.join(models_dir, 'cluster_model.pkl'), 'wb') as f:
        pickle.dump({'kmeans': kmeans, 'scaler': scaler,
                'label_map': label_map}, f)

    df.to_csv(input_path, index=False)

    report = {
        'n_clusters': n_clusters,
        'silhouette_scores': {str(k): s for k, s in zip(k_range, sil_scores)},
        'final_silhouette': sil_scores[n_clusters - 2],
        'segment_summary': seg_summary.to_dict(),
        'label_map': label_map,
    }
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n{'='*50}")
    print(f" CLUSTERING SUMMARY")
    print(f"{'='*50}")
    for seg, row in seg_summary.iterrows():
        print(
        f" {seg}: {int(row['count'])} properties | Avg Rs.{row['avg_price']:,.0f} | ROI {row['avg_roi']:.1f}%")
    print(f" Silhouette Score: {sil_scores[n_clusters - 2]}")
    print(f" Saved to: {models_dir}/cluster_model.pkl")
    return report


if __name__ == '__main__':
    run_clustering()
