"""
Streamlit Interactive Dashboard
================================
9-tab dashboard for the Bangalore Real Estate Intelligence Platform.
Run: streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import json
import os
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics.pairwise import cosine_similarity

# ─── Page Config ──────────────────────────────────────────
st.set_page_config(
    page_title="Bangalore Real Estate Intelligence",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ───────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0a0a0a; }
    .stApp { background-color: #0a0a0a; }
    [data-testid="stSidebar"] { background-color: #0f0f0f; }
    .metric-card {
        background: #141414;
        border: 1px solid #222;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .metric-value { font-size: 1.8rem; font-weight: 800; color: #2563eb; }
    .metric-label { font-size: 0.75rem; color: #888; text-transform: uppercase; }
    .stMetric { background: #141414; border-radius: 12px; padding: 16px; border: 1px solid #222; }
</style>
""", unsafe_allow_html=True)

# ─── Data Loading ─────────────────────────────────────────
@st.cache_data
def load_data():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base, 'data/processed/production_final.csv')
    if not os.path.exists(data_path):
        st.error("⚠️ Run the pipeline first: `python run_pipeline.py`")
        st.stop()
    return pd.read_csv(data_path)

@st.cache_data
def load_json_report(name):
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, f'ml/reports/{name}')
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return {}

@st.cache_resource
def load_model(name):
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, f'ml/models/{name}')
    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    except:
        return None

df = load_data()

# ─── Sidebar ──────────────────────────────────────────────
st.sidebar.markdown("## 🏗️ **INTELLIGENCE**")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Overview", "🔮 Price Prediction", "🗺️ Location Heatmap",
     "💎 Undervalued Properties", "📊 Model Performance",
     "🎯 Buyer Matching", "📈 ROI Comparison",
     "🟢 Buy/Sell Signal", "📋 Executive Report"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**{len(df):,}** properties loaded")
st.sidebar.markdown(f"**{df['location'].nunique()}** locations")

# ═══════════════════════════════════════════════════════════
# PAGE 1: OVERVIEW
# ═══════════════════════════════════════════════════════════
if page == "🏠 Overview":
    st.title("📊 Market Intelligence Dashboard")
    st.markdown("Real-time analytics for Bangalore real estate market")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Properties", f"{len(df):,}")
    c2.metric("Avg Price", f"₹{df['price'].mean()/1e7:.2f}Cr")
    c3.metric("Avg ROI", f"{df['roi'].mean():.1f}%")
    best_loc = df.groupby('location')['roi'].mean().idxmax()
    c4.metric("Best ROI Location", best_loc)

    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        loc_stats = df.groupby('location').agg(
            avg_price=('price', 'mean'),
            avg_roi=('roi', 'mean'),
            count=('property_id', 'count')
        ).reset_index().sort_values('avg_roi', ascending=False)

        fig = px.bar(loc_stats, x='location', y='avg_roi',
                     color='avg_roi', color_continuous_scale='Viridis',
                     title='Average ROI by Location',
                     labels={'avg_roi': 'Avg ROI (%)', 'location': 'Location'})
        fig.update_layout(template='plotly_dark', height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        if 'segment_label' in df.columns:
            seg_counts = df['segment_label'].value_counts()
            fig = px.pie(values=seg_counts.values, names=seg_counts.index,
                        title='Market Segmentation', hole=0.4,
                        color_discrete_sequence=['#6366f1', '#2563eb', '#f59e0b', '#10b981'])
            fig.update_layout(template='plotly_dark', height=400)
            st.plotly_chart(fig, use_container_width=True)

    # Price distribution
    fig = px.histogram(df, x='price', nbins=50, title='Price Distribution',
                       color_discrete_sequence=['#2563eb'])
    fig.update_layout(template='plotly_dark', height=350)
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════
# PAGE 2: PRICE PREDICTION
# ═══════════════════════════════════════════════════════════
elif page == "🔮 Price Prediction":
    st.title("🔮 Price Prediction Tool")

    model = load_model('price_model.pkl')
    encoders = load_model('encoders.pkl')

    if model is None:
        st.error("Model not found. Run the pipeline first.")
        st.stop()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Property Details")
        sqft = st.slider("Square Feet", 500, 5000, 1500)
        bedrooms = st.selectbox("Bedrooms", [1, 2, 3, 4, 5], index=1)
        bathrooms = st.selectbox("Bathrooms", [1, 2, 3, 4], index=1)
        balconies = st.selectbox("Balconies", [0, 1, 2, 3], index=1)
        parking = st.selectbox("Parking", [0, 1, 2], index=1)
        age = st.slider("Property Age (years)", 0, 25, 3)
        floor = st.slider("Floor", 1, 25, 5)
        total_floors = st.slider("Total Floors", floor, 30, max(floor, 15))

    with col2:
        st.subheader("Location & Features")
        locations = sorted(df['location'].unique())
        location = st.selectbox("Location", locations)
        property_type = st.selectbox("Property Type", ['Apartment', 'Villa', 'Penthouse', 'Builder Floor', 'Plot'])
        furnishing = st.selectbox("Furnishing", ['Unfurnished', 'Semi-furnished', 'Fully-furnished'])
        listing_type = st.selectbox("Listing Type", ['Resale', 'New Launch', 'Ready to Move'])
        amenities = st.slider("Amenities Count", 2, 20, 8)
        dist_metro = st.slider("Distance to Metro (km)", 0.1, 15.0, 2.0)
        dist_school = st.slider("Distance to School (km)", 0.2, 8.0, 1.5)
        dist_hospital = st.slider("Distance to Hospital (km)", 0.3, 10.0, 2.0)
        dist_cbd = st.slider("Distance to CBD (km)", 1.0, 30.0, 10.0)

    if st.button("🔮 Predict Price", type="primary", use_container_width=True):
        # Compute derived features
        connectivity = max(1.0, 10.0 - (dist_metro * 0.4 + dist_cbd * 0.15))
        safety = 7
        school_sc = 7
        loc_score = connectivity * 0.4 + safety * 0.3 + school_sc * 0.3
        amenity_idx = amenities / 20.0
        furnish_map = {'Unfurnished': 0, 'Semi-furnished': 1, 'Fully-furnished': 2}
        furnish_num = furnish_map[furnishing]
        luxury = (sqft / 5000) * 0.3 + (amenities / 20) * 0.25 + (furnish_num / 2) * 0.2 + (balconies / 3) * 0.15 + (parking / 2) * 0.1
        prox = max(0, (15 - (dist_metro * 0.35 + dist_school * 0.2 + dist_hospital * 0.2 + dist_cbd * 0.25)) / 15 * 10)
        age_bucket = 0 if age <= 2 else 1 if age <= 5 else 2 if age <= 10 else 3 if age <= 20 else 4

        # Encode categoricals
        loc_enc = encoders['location'].transform([location])[0] if encoders and 'location' in encoders else 0
        builder_enc = 0
        type_enc = encoders['property_type'].transform([property_type])[0] if encoders and 'property_type' in encoders else 0
        furnish_enc = encoders['furnishing'].transform([furnishing])[0] if encoders and 'furnishing' in encoders else 0
        listing_enc = encoders['listing_type'].transform([listing_type])[0] if encoders and 'listing_type' in encoders else 0

        features = [sqft, bedrooms, bathrooms, balconies, parking,
                   age, floor, total_floors, amenities,
                   dist_metro, dist_school, dist_hospital, dist_cbd,
                   loc_score, luxury, amenity_idx, prox,
                   age_bucket, furnish_num,
                   loc_enc, builder_enc, type_enc, furnish_enc, listing_enc]

        predicted_price = int(model.predict([features])[0])

        st.markdown("---")
        st.success(f"### 💰 Predicted Price: ₹{predicted_price:,}")

        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Price Range (Low)", f"₹{int(predicted_price * 0.92):,}")
        mc2.metric("Predicted", f"₹{predicted_price:,}")
        mc3.metric("Price Range (High)", f"₹{int(predicted_price * 1.08):,}")

        # Find similar properties
        loc_data = df[df['location'] == location]
        avg_loc = loc_data['price'].mean()
        st.info(f"📍 Average price in **{location}**: ₹{avg_loc:,.0f} | Your prediction: ₹{predicted_price:,}")

# ═══════════════════════════════════════════════════════════
# PAGE 3: LOCATION HEATMAP
# ═══════════════════════════════════════════════════════════
elif page == "🗺️ Location Heatmap":
    st.title("🗺️ Bangalore Market Heatmap")

    try:
        import folium
        from streamlit_folium import st_folium

        metric = st.selectbox("Color by", ['roi', 'price', 'demand_score', 'market_trend'])

        loc_agg = df.groupby('location').agg(
            lat=('latitude', 'mean'), lon=('longitude', 'mean'),
            avg_price=('price', 'mean'), avg_roi=('roi', 'mean'),
            count=('property_id', 'count'),
            demand=('demand_score', 'mean'),
            trend=('market_trend', 'mean')
        ).reset_index()

        m = folium.Map(location=[12.9716, 77.5946], zoom_start=11,
                       tiles='CartoDB dark_matter')

        for _, row in loc_agg.iterrows():
            val = row['avg_roi'] if metric == 'roi' else row['avg_price'] / 1e7 if metric == 'price' else row['demand'] if metric == 'demand_score' else row['trend'] * 100
            color = '#10b981' if (metric == 'roi' and val > 12) or (metric == 'market_trend' and val > 12) else '#2563eb' if val > 8 else '#f59e0b'

            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=max(8, row['count'] / 50),
                color=color, fill=True, fill_color=color, fill_opacity=0.6,
                popup=f"<b>{row['location']}</b><br>Avg: ₹{row['avg_price']/1e7:.2f}Cr<br>ROI: {row['avg_roi']:.1f}%<br>Properties: {row['count']}"
            ).add_to(m)

        st_folium(m, width=None, height=600)

    except ImportError:
        st.warning("Install folium and streamlit-folium: `pip install folium streamlit-folium`")

        # Fallback to plotly
        loc_agg = df.groupby('location').agg(lat=('latitude', 'mean'), lon=('longitude', 'mean'), avg_roi=('roi', 'mean')).reset_index()
        fig = px.scatter_mapbox(loc_agg, lat='lat', lon='lon', size='avg_roi', color='avg_roi',
                               hover_name='location', zoom=10, mapbox_style='carto-darkmatter')
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════
# PAGE 4: UNDERVALUED PROPERTIES
# ═══════════════════════════════════════════════════════════
elif page == "💎 Undervalued Properties":
    st.title("💎 Undervalued Property Deals")

    if 'valuation_label' in df.columns:
        underpriced = df[df['valuation_label'] == 'Underpriced'].sort_values('price_gap_pct')

        c1, c2, c3 = st.columns(3)
        c1.metric("Underpriced", f"{len(underpriced):,}")
        c2.metric("Avg Price Gap", f"{underpriced['price_gap_pct'].mean():.1f}%")
        c3.metric("Best Deal Gap", f"{underpriced['price_gap_pct'].min():.1f}%")

        # Filters
        col1, col2 = st.columns(2)
        loc_filter = col1.multiselect("Filter by Location", df['location'].unique())
        budget = col2.slider("Max Budget (₹ Cr)", 0.5, 10.0, 5.0)

        filtered = underpriced.copy()
        if loc_filter:
            filtered = filtered[filtered['location'].isin(loc_filter)]
        filtered = filtered[filtered['price'] <= budget * 1e7]

        st.dataframe(
            filtered[['property_id', 'location', 'property_type', 'sqft', 'bedrooms',
                      'price', 'predicted_price', 'price_gap_pct', 'roi', 'sell_signal']]
            .head(50)
            .style.format({'price': '₹{:,.0f}', 'predicted_price': '₹{:,.0f}', 'price_gap_pct': '{:.1f}%', 'roi': '{:.1f}%'}),
            use_container_width=True, height=500
        )
    else:
        st.warning("Run recommendation engine first.")

# ═══════════════════════════════════════════════════════════
# PAGE 5: MODEL PERFORMANCE
# ═══════════════════════════════════════════════════════════
elif page == "📊 Model Performance":
    st.title("📊 Model Performance & Diagnostics")

    eval_report = load_json_report('evaluation_report.json')
    baseline = load_json_report('baseline_results.json')

    # Baseline comparison
    if baseline:
        st.subheader("Baseline Results")
        bl_data = []
        for name in ['global_mean', 'global_median', 'location_mean']:
            b = baseline.get(name, {})
            bl_data.append({'Model': name.replace('_', ' ').title(), 'RMSE': b.get('rmse', 0), 'MAE': b.get('mae', 0), 'R²': b.get('r2', 0)})
        st.dataframe(pd.DataFrame(bl_data), use_container_width=True)

    # Model metrics
    if eval_report.get('model_metrics'):
        st.subheader("ML Model Comparison")
        metrics = eval_report['model_metrics']
        m_data = [{'Model': k, **v} for k, v in metrics.items()]
        st.dataframe(pd.DataFrame(m_data), use_container_width=True)

        # Bar chart
        m_df = pd.DataFrame(m_data)
        fig = px.bar(m_df, x='Model', y='r2', color='Model', title='R² Score Comparison',
                     color_discrete_sequence=['#6366f1', '#8b5cf6', '#a78bfa', '#2563eb'])
        fig.update_layout(template='plotly_dark')
        st.plotly_chart(fig, use_container_width=True)

    # Show diagnostic plots
    st.subheader("Diagnostic Plots")
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets = os.path.join(base, 'ml/reports/assets')

    plots = ['model_comparison.png', 'actual_vs_predicted.png', 'residual_distribution.png',
             'residual_vs_predicted.png', 'feature_importance.png', 'location_error.png']

    cols = st.columns(2)
    for i, plot in enumerate(plots):
        path = os.path.join(assets, plot)
        if os.path.exists(path):
            cols[i % 2].image(path, caption=plot.replace('_', ' ').replace('.png', '').title())

# ═══════════════════════════════════════════════════════════
# PAGE 6: BUYER MATCHING
# ═══════════════════════════════════════════════════════════
elif page == "🎯 Buyer Matching":
    st.title("🎯 Buyer Preference Matching")

    col1, col2 = st.columns(2)
    with col1:
        budget = st.slider("Budget (₹ Lakhs)", 20, 800, 150) * 1e5
        bedrooms = st.selectbox("Preferred Bedrooms", [1, 2, 3, 4, 5], index=1)
        min_sqft = st.slider("Minimum Sqft", 500, 4000, 1000)
    with col2:
        pref_location = st.selectbox("Preferred Location", ['Any'] + sorted(df['location'].unique().tolist()))
        min_amenities = st.slider("Min Amenities", 2, 20, 5)

    if st.button("🔍 Find Matching Properties", type="primary", use_container_width=True):
        artifacts = load_model('recommendation_artifacts.pkl')

        if artifacts is not None:
            buyer_pref = {
                'bedrooms': bedrooms,
                'sqft': min_sqft,
                'location_score': 8.0,
                'amenity_index': min_amenities / 20.0,
                'luxury_score': 0.5,
                'proximity_score': 7.0,
                'price': budget,
            }

            buyer_vec = artifacts['scaler'].transform(
                pd.DataFrame([buyer_pref])[artifacts['feature_columns']]
            )
            sims = cosine_similarity(buyer_vec, artifacts['match_matrix'])[0]
            df_copy = df.copy()
            df_copy['match_score'] = sims

            candidates = df_copy[df_copy['price'] <= budget * 1.15]
            if pref_location != 'Any':
                loc_cands = candidates[candidates['location'] == pref_location]
                if len(loc_cands) >= 5:
                    candidates = loc_cands

            top = candidates.nlargest(15, 'match_score')

            st.success(f"Found {len(top)} matching properties!")
            st.dataframe(
                top[['property_id', 'location', 'property_type', 'sqft', 'bedrooms',
                     'price', 'roi', 'match_score']]
                .style.format({'price': '₹{:,.0f}', 'roi': '{:.1f}%', 'match_score': '{:.3f}'}),
                use_container_width=True
            )
        else:
            st.warning("Run recommendation engine first.")

# ═══════════════════════════════════════════════════════════
# PAGE 7: ROI COMPARISON
# ═══════════════════════════════════════════════════════════
elif page == "📈 ROI Comparison":
    st.title("📈 ROI & Market Trend Analysis")

    loc_roi = df.groupby('location').agg(
        avg_roi=('roi', 'mean'),
        avg_trend=('market_trend', lambda x: x.mean() * 100),
        avg_price=('price', 'mean'),
        count=('property_id', 'count')
    ).reset_index().sort_values('avg_roi', ascending=False)

    fig = px.bar(loc_roi, x='location', y='avg_roi', color='avg_trend',
                 color_continuous_scale='RdYlGn', title='ROI by Location (colored by Market Trend)',
                 labels={'avg_roi': 'Avg ROI (%)', 'avg_trend': 'Trend (%)'})
    fig.update_layout(template='plotly_dark', height=450)
    st.plotly_chart(fig, use_container_width=True)

    # Scatter: ROI vs Price
    fig2 = px.scatter(loc_roi, x='avg_price', y='avg_roi', size='count',
                      color='avg_trend', text='location',
                      color_continuous_scale='Viridis',
                      title='ROI vs Average Price',
                      labels={'avg_price': 'Avg Price (₹)', 'avg_roi': 'Avg ROI (%)'})
    fig2.update_traces(textposition='top center', textfont_size=9)
    fig2.update_layout(template='plotly_dark', height=450)
    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(loc_roi.style.format({
        'avg_roi': '{:.1f}%', 'avg_trend': '{:.1f}%', 'avg_price': '₹{:,.0f}'
    }), use_container_width=True)

# ═══════════════════════════════════════════════════════════
# PAGE 8: BUY/SELL SIGNAL
# ═══════════════════════════════════════════════════════════
elif page == "🟢 Buy/Sell Signal":
    st.title("🟢 Buy/Sell Recommendation Signal")

    if 'sell_signal' in df.columns:
        signal_counts = df['sell_signal'].value_counts()
        fig = px.pie(values=signal_counts.values, names=signal_counts.index,
                     title='Signal Distribution',
                     color_discrete_sequence=['#10b981', '#22c55e', '#f59e0b', '#ef4444', '#dc2626'])
        fig.update_layout(template='plotly_dark')
        st.plotly_chart(fig, use_container_width=True)

        # Property lookup
        st.subheader("Property Signal Lookup")
        prop_id = st.text_input("Enter Property ID (e.g., BLR-10001)")
        if prop_id:
            prop = df[df['property_id'] == prop_id]
            if len(prop) > 0:
                p = prop.iloc[0]
                c1, c2, c3 = st.columns(3)
                c1.metric("Signal", p.get('sell_signal', 'N/A'))
                c2.metric("ROI", f"{p['roi']:.1f}%")
                c3.metric("Market Trend", f"{p['market_trend']*100:.1f}%")

                st.json({
                    'location': p['location'],
                    'price': f"₹{p['price']:,.0f}",
                    'predicted_price': f"₹{p.get('predicted_price', 0):,.0f}",
                    'gap': f"{p.get('price_gap_pct', 0):.1f}%",
                    'signal': p.get('sell_signal', 'N/A'),
                    'demand_score': int(p['demand_score']),
                })
            else:
                st.warning("Property not found.")
    else:
        st.warning("Run recommendation engine first.")

# ═══════════════════════════════════════════════════════════
# PAGE 9: EXECUTIVE REPORT
# ═══════════════════════════════════════════════════════════
elif page == "📋 Executive Report":
    st.title("📋 Executive Summary Report")

    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    report_path = os.path.join(base, 'ml/reports/executive_report.html')

    if os.path.exists(report_path):
        with open(report_path) as f:
            html = f.read()
        st.components.v1.html(html, height=2000, scrolling=True)

        with open(report_path, 'rb') as f:
            st.download_button("📥 Download Report", f.read(), "executive_report.html", "text/html")
    else:
        st.warning("Executive report not generated yet. Run the full pipeline.")

        # Show inline summary
        st.subheader("Quick Summary")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Properties", f"{len(df):,}")
        c2.metric("Locations", f"{df['location'].nunique()}")
        c3.metric("Avg Price", f"₹{df['price'].mean()/1e7:.2f}Cr")
        c4.metric("Avg ROI", f"{df['roi'].mean():.1f}%")
