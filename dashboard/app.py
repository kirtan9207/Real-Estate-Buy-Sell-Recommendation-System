"""
Streamlit Interactive Dashboard
================================
Real Estate Intelligence Platform — Bangalore
Run: python -m streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import json
import os
import plotly.express as px
import plotly.graph_objects as go

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bangalore Real Estate Intelligence",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0a0a0a; }
    .stApp { background-color: #0a0a0a; }
    [data-testid="stSidebar"] { background-color: #0f0f0f; border-right: 1px solid #1a1a1a; }

    div[role="radiogroup"] > label {
        padding: 12px 16px;
        background: #141414;
        border: 1px solid #222;
        border-radius: 8px;
        margin-bottom: 8px;
        transition: all 0.3s ease;
        cursor: pointer;
        display: block;
    }
    div[role="radiogroup"] > label:hover {
        background: #1f1f1f;
        border-color: #333;
        transform: translateY(-1px);
    }

    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #161616, #121212);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #252525;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    [data-testid="stMetricValue"] { color: #f8fafc; font-weight: 700; }
    [data-testid="stMetricLabel"] { color: #94a3b8; font-weight: 600; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

# ─── Helpers ──────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_pkl(name):
    """Direct pickle load — no Streamlit cache (avoids stale-cache bug)."""
    path = os.path.join(BASE, f'ml/models/{name}')
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return None
    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    except Exception:
        return None


def load_json_report(name):
    path = os.path.join(BASE, f'ml/reports/{name}')
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


@st.cache_data(ttl=300)
def load_data():
    path = os.path.join(BASE, 'data/processed/production_final.csv')
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    return df


# ─── Load Data ────────────────────────────────────────────────────────────────
df = load_data()

if df is None:
    st.error("Data not found. Run: `python run_pipeline.py` first.")
    st.stop()

# ─── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.markdown("## **INTELLIGENCE**")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    [
        "Market Overview",
        "Price Prediction Engine",
        "Geographic Heatmap",
        "Undervalued Opportunities",
        "Buyer Preference Matching",
        "Investment ROI Analysis",
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.caption(f"Dataset: {len(df):,} properties | 20 locations")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — MARKET OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
if page == "Market Overview":
    st.title("Market Intelligence Dashboard")
    st.markdown("Real-time analytics for Bangalore real estate market")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Properties", f"{len(df):,}")
    c2.metric("Avg Price", f"Rs.{df['price'].mean()/1e7:.2f} Cr")
    c3.metric("Avg ROI", f"{df['roi'].mean():.1f}%")
    best_loc = df.groupby('location')['roi'].mean().idxmax()
    c4.metric("Best ROI Location", best_loc)

    st.markdown("---")
    col1, col2 = st.columns([2, 1])

    with col1:
        loc_stats = df.groupby('location').agg(
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
            fig = px.pie(
                values=seg_counts.values, names=seg_counts.index,
                title='Market Segmentation', hole=0.4,
                color_discrete_sequence=['#6366f1', '#2563eb', '#f59e0b', '#10b981']
            )
            fig.update_layout(template='plotly_dark', height=400)
            st.plotly_chart(fig, use_container_width=True)

    # Signal distribution pie (only if sell_signal exists)
    col3, col4 = st.columns(2)
    with col3:
        if 'sell_signal' in df.columns:
            sc = df['sell_signal'].value_counts()
            fig = px.pie(
                values=sc.values, names=sc.index,
                title='Buy / Hold / Sell Signal Distribution', hole=0.35,
                color_discrete_sequence=['#10b981', '#2563eb', '#f59e0b', '#ef4444']
            )
            fig.update_layout(template='plotly_dark', height=360)
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        fig = px.histogram(df, x='price', nbins=50,
                           title='Price Distribution',
                           color_discrete_sequence=['#2563eb'])
        fig.update_layout(template='plotly_dark', height=360)
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — PRICE PREDICTION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Price Prediction Engine":
    st.title("AI Price Prediction Engine")
    st.markdown("Enter property details below and get an ML-powered price estimate.")

    model = load_pkl('price_model.pkl')
    encoders = load_pkl('encoders.pkl')

    if model is None:
        st.error("XGBoost price model not found. Make sure `python run_pipeline.py` completed successfully.")
        st.stop()

    st.success(f"Model loaded: XGBoost Regressor (R² = 0.9803)")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Property Details")
        sqft = st.slider("Square Feet", 500, 5000, 1500)
        bedrooms = st.selectbox("Bedrooms", [1, 2, 3, 4, 5], index=1)
        bathrooms = st.selectbox("Bathrooms", [1, 2, 3, 4], index=1)
        balconies = st.selectbox("Balconies", [0, 1, 2, 3], index=1)
        parking = st.selectbox("Parking Spots", [0, 1, 2], index=1)
        age = st.slider("Property Age (years)", 0, 25, 3)
        floor = st.slider("Floor Number", 1, 25, 5)
        total_floors = st.slider("Total Floors in Building", floor, 30, max(floor, 15))

    with col2:
        st.subheader("Location & Features")
        locations = sorted(df['location'].unique())
        location = st.selectbox("Location", locations)
        property_type = st.selectbox(
            "Property Type", ['Apartment', 'Villa', 'Penthouse', 'Builder Floor', 'Plot'])
        furnishing = st.selectbox(
            "Furnishing Status", ['Unfurnished', 'Semi-furnished', 'Fully-furnished'])
        listing_type = st.selectbox(
            "Listing Type", ['Resale', 'New Launch', 'Ready to Move'])
        amenities = st.slider("Amenities Count (gym, pool, etc.)", 2, 20, 8)
        dist_metro = st.slider("Distance to Metro (km)", 0.1, 15.0, 2.0)
        dist_school = st.slider("Distance to School (km)", 0.2, 8.0, 1.5)
        dist_hospital = st.slider("Distance to Hospital (km)", 0.3, 10.0, 2.0)
        dist_cbd = st.slider("Distance to CBD (km)", 1.0, 30.0, 10.0)

    if st.button("Predict Price", type="primary", use_container_width=True):
        # Derived features
        connectivity = max(1.0, 10.0 - (dist_metro * 0.4 + dist_cbd * 0.15))
        loc_score = connectivity * 0.4 + 7 * 0.3 + 7 * 0.3
        amenity_idx = amenities / 20.0
        furnish_map = {'Unfurnished': 0, 'Semi-furnished': 1, 'Fully-furnished': 2}
        furnish_num = furnish_map[furnishing]
        luxury = (sqft / 5000) * 0.3 + (amenities / 20) * 0.25 + \
            (furnish_num / 2) * 0.2 + (balconies / 3) * 0.15 + (parking / 2) * 0.1
        prox = max(0, (15 - (dist_metro * 0.35 + dist_school * 0.2 +
                   dist_hospital * 0.2 + dist_cbd * 0.25)) / 15 * 10)
        age_bucket = 0 if age <= 2 else 1 if age <= 5 else 2 if age <= 10 else 3 if age <= 20 else 4

        # Encoders
        def enc(key, val, fallback=0):
            if encoders and key in encoders:
                try:
                    return int(encoders[key].transform([val])[0])
                except Exception:
                    pass
            return fallback

        loc_enc = enc('location', location)
        type_enc = enc('property_type', property_type)
        furnish_enc = enc('furnishing', furnishing)
        listing_enc = enc('listing_type', listing_type)

        features = [sqft, bedrooms, bathrooms, balconies, parking,
                    age, floor, total_floors, amenities,
                    dist_metro, dist_school, dist_hospital, dist_cbd,
                    loc_score, luxury, amenity_idx, prox,
                    age_bucket, furnish_num,
                    loc_enc, 0, type_enc, furnish_enc, listing_enc]

        predicted_price = int(model.predict([features])[0])

        st.markdown("---")
        st.success(f"### Predicted Price: Rs.{predicted_price:,}")

        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Conservative Estimate", f"Rs.{int(predicted_price * 0.92):,}")
        mc2.metric("ML Predicted Price", f"Rs.{predicted_price:,}")
        mc3.metric("Optimistic Estimate", f"Rs.{int(predicted_price * 1.08):,}")

        avg_loc = df[df['location'] == location]['price'].mean()
        st.info(f"Avg market price in **{location}**: Rs.{avg_loc:,.0f} | Your prediction: Rs.{predicted_price:,}")

        # Gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=predicted_price / 1e7,
            title={'text': "Predicted Price (Rs. Cr)"},
            gauge={
                'axis': {'range': [0, df['price'].max() / 1e7]},
                'bar': {'color': '#2563eb'},
                'steps': [
                    {'range': [0, df['price'].quantile(0.33) / 1e7], 'color': '#10b981'},
                    {'range': [df['price'].quantile(0.33) / 1e7, df['price'].quantile(0.66) / 1e7], 'color': '#f59e0b'},
                    {'range': [df['price'].quantile(0.66) / 1e7, df['price'].max() / 1e7], 'color': '#ef4444'},
                ],
            }
        ))
        fig.update_layout(template='plotly_dark', height=300)
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — GEOGRAPHIC HEATMAP
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Geographic Heatmap":
    st.title("Bangalore Market Heatmap")
    st.markdown("Interactive location-based market analysis across Bangalore.")

    metric = st.selectbox("Metric to Visualize", ['roi', 'avg_price', 'demand_score', 'market_trend'])

    loc_agg = df.groupby('location').agg(
        lat=('latitude', 'mean'),
        lon=('longitude', 'mean'),
        avg_price=('price', 'mean'),
        avg_roi=('roi', 'mean'),
        count=('property_id', 'count'),
        demand=('demand_score', 'mean'),
        trend=('market_trend', 'mean')
    ).reset_index()

    color_col = {
        'roi': 'avg_roi',
        'avg_price': 'avg_price',
        'demand_score': 'demand',
        'market_trend': 'trend',
    }[metric]

    fig = px.scatter_mapbox(
        loc_agg, lat='lat', lon='lon',
        size='count',
        color=color_col,
        hover_name='location',
        hover_data={
            'avg_price': ':,.0f',
            'avg_roi': ':.1f',
            'count': True,
        },
        color_continuous_scale='Viridis',
        size_max=40,
        zoom=10,
        mapbox_style='carto-darkmatter',
        title=f'Bangalore — {metric.replace("_", " ").title()} by Location'
    )
    fig.update_layout(template='plotly_dark', height=600, margin={"r": 0, "l": 0, "b": 0, "t": 40})
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        loc_agg[['location', 'avg_price', 'avg_roi', 'count', 'demand', 'trend']]
        .sort_values('avg_roi', ascending=False)
        .rename(columns={'avg_price': 'Avg Price (Rs.)', 'avg_roi': 'Avg ROI (%)', 'count': 'Properties', 'demand': 'Demand Score', 'trend': 'Market Trend'})
        .style.format({'Avg Price (Rs.)': 'Rs.{:,.0f}', 'Avg ROI (%)': '{:.1f}%', 'Market Trend': '{:.3f}'}),
        use_container_width=True
    )

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — UNDERVALUED OPPORTUNITIES
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Undervalued Opportunities":
    st.title("Undervalued Property Deals")
    st.markdown("Properties where builder price is **below** the ML-predicted market value — best investment opportunities.")

    if 'valuation_label' not in df.columns:
        st.error("valuation_label column missing. Re-run the pipeline.")
        st.stop()

    underpriced = df[df['valuation_label'] == 'Underpriced'].copy()

    c1, c2, c3 = st.columns(3)
    c1.metric("Underpriced Deals", f"{len(underpriced):,}")
    c2.metric("Avg Price Gap", f"{underpriced['price_gap_pct'].mean():.1f}%")
    c3.metric("Best Deal Gap", f"{underpriced['price_gap_pct'].max():.1f}%")

    st.markdown("---")
    col1, col2 = st.columns(2)
    loc_filter = col1.multiselect("Filter by Location", sorted(df['location'].unique()))
    budget = col2.slider("Max Budget (Rs. Cr)", 0.5, 20.0, 10.0)

    filtered = underpriced.copy()
    if loc_filter:
        filtered = filtered[filtered['location'].isin(loc_filter)]
    filtered = filtered[filtered['price'] <= budget * 1e7]
    filtered = filtered.sort_values('price_gap_pct', ascending=False)

    st.markdown(f"**Showing {len(filtered)} deals**")

    # Bar chart of opportunities by location
    opp_by_loc = filtered.groupby('location').size().reset_index(name='deals')
    if len(opp_by_loc) > 0:
        fig = px.bar(opp_by_loc, x='location', y='deals',
                     color='deals', color_continuous_scale='Greens',
                     title='Undervalued Deals by Location')
        fig.update_layout(template='plotly_dark', height=350)
        st.plotly_chart(fig, use_container_width=True)

    show_cols = ['property_id', 'location', 'property_type', 'sqft', 'bedrooms',
                 'price', 'predicted_price', 'price_gap_pct', 'roi']
    available = [c for c in show_cols if c in filtered.columns]

    st.dataframe(
        filtered[available].head(50)
        .style.format({
            'price': 'Rs.{:,.0f}',
            'predicted_price': 'Rs.{:,.0f}',
            'price_gap_pct': '{:.1f}%',
            'roi': '{:.1f}%'
        }),
        use_container_width=True, height=450
    )

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — BUYER PREFERENCE MATCHING
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Buyer Preference Matching":
    st.title("Buyer Preference Matching")
    st.markdown("Tell us your requirements and our AI will find the best matched properties.")

    col1, col2 = st.columns(2)
    with col1:
        budget = st.slider("Budget (Rs. Lakhs)", 20, 1000, 200) * 1e5
        bedrooms = st.selectbox("Preferred Bedrooms", [1, 2, 3, 4, 5], index=1)
        min_sqft = st.slider("Minimum Square Feet", 500, 4000, 1000)
        min_roi = st.slider("Minimum ROI (%)", 5, 25, 10)
    with col2:
        pref_location = st.selectbox("Preferred Location", ['Any'] + sorted(df['location'].unique().tolist()))
        prop_type = st.selectbox("Property Type", ['Any', 'Apartment', 'Villa', 'Penthouse', 'Builder Floor'])
        max_metro = st.slider("Max Distance to Metro (km)", 0.5, 10.0, 3.0)

    if st.button("Find Matching Properties", type="primary", use_container_width=True):
        candidates = df.copy()
        candidates = candidates[candidates['price'] <= budget * 1.15]
        candidates = candidates[candidates['sqft'] >= min_sqft]
        candidates = candidates[candidates['bedrooms'] == bedrooms]
        candidates = candidates[candidates['roi'] >= min_roi]
        candidates = candidates[candidates['distance_metro'] <= max_metro]

        if pref_location != 'Any':
            loc_cands = candidates[candidates['location'] == pref_location]
            if len(loc_cands) >= 3:
                candidates = loc_cands

        if prop_type != 'Any':
            type_cands = candidates[candidates['property_type'] == prop_type]
            if len(type_cands) >= 3:
                candidates = type_cands

        # Score by ROI + value gap
        candidates['match_score'] = (
            candidates['roi'] / candidates['roi'].max() * 0.5 +
            candidates['price_gap_pct'].clip(0, 30) / 30 * 0.5
        )

        top = candidates.nlargest(15, 'match_score')

        if len(top) == 0:
            st.warning("No exact matches. Try relaxing filters (increase budget or reduce ROI requirement).")
        else:
            st.success(f"Found {len(top)} matching properties!")

            fig = px.scatter(
                top, x='price', y='roi',
                color='location', size='sqft',
                hover_name='property_id',
                hover_data={'price': ':,.0f', 'roi': ':.1f', 'sqft': True},
                title='Matched Properties — ROI vs Price',
                labels={'price': 'Price (Rs.)', 'roi': 'ROI (%)'}
            )
            fig.update_layout(template='plotly_dark', height=400)
            st.plotly_chart(fig, use_container_width=True)

            show_cols = ['property_id', 'location', 'property_type', 'sqft', 'bedrooms',
                         'price', 'roi', 'match_score']
            avail = [c for c in show_cols if c in top.columns]
            st.dataframe(
                top[avail].style.format({
                    'price': 'Rs.{:,.0f}',
                    'roi': '{:.1f}%',
                    'match_score': '{:.3f}'
                }),
                use_container_width=True
            )

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — INVESTMENT ROI ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Investment ROI Analysis":
    st.title("Investment ROI & Market Trend Analysis")
    st.markdown("Compare return on investment across all 20 Bangalore localities.")

    loc_roi = df.groupby('location').agg(
        avg_roi=('roi', 'mean'),
        avg_trend=('market_trend', lambda x: x.mean() * 100),
        avg_price=('price', 'mean'),
        count=('property_id', 'count')
    ).reset_index().sort_values('avg_roi', ascending=False)

    # ROI Bar
    fig = px.bar(
        loc_roi, x='location', y='avg_roi', color='avg_trend',
        color_continuous_scale='RdYlGn',
        title='ROI by Location (colored by Market Trend)',
        labels={'avg_roi': 'Avg ROI (%)', 'avg_trend': 'Trend (%)'}
    )
    fig.update_layout(template='plotly_dark', height=450)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        # ROI vs Price scatter
        fig2 = px.scatter(
            loc_roi, x='avg_price', y='avg_roi',
            size='count', color='avg_trend',
            text='location',
            color_continuous_scale='Viridis',
            title='ROI vs Average Price',
            labels={'avg_price': 'Avg Price (Rs.)', 'avg_roi': 'Avg ROI (%)'}
        )
        fig2.update_traces(textposition='top center', textfont_size=9)
        fig2.update_layout(template='plotly_dark', height=400)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        # Top 5 locations pie
        top5 = loc_roi.head(5)
        fig3 = px.pie(
            top5, values='avg_roi', names='location',
            title='Top 5 Locations by ROI',
            color_discrete_sequence=['#10b981', '#2563eb', '#6366f1', '#f59e0b', '#8b5cf6']
        )
        fig3.update_layout(template='plotly_dark', height=400)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("### Full Location Comparison Table")
    st.dataframe(
        loc_roi.style.format({
            'avg_roi': '{:.1f}%',
            'avg_trend': '{:.1f}%',
            'avg_price': 'Rs.{:,.0f}'
        }),
        use_container_width=True
    )
