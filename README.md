# Real Estate Buy/Sell Recommendation System — Bangalore

A production-grade **Data Science project** that analyzes the Bangalore real estate market using machine learning. The system generates 20,000+ realistic property listings, trains multiple ML models, detects undervalued properties, matches buyer preferences, and provides buy/sell/hold investment signals through an interactive dashboard.

---

## Key Features

| Feature | Description |
|---|---|
| **Price Prediction** | XGBoost model with R2 > 0.85 on 24 engineered features |
| **Undervalued Detection** | Identifies properties priced 10%+ below predicted value |
| **Buyer Matching** | Cosine similarity-based preference matching engine |
| **Buy/Sell Signals** | Trend-based investment signals (Buy/Hold/Sell/Wait) |
| **Market Segmentation** | KMeans clustering into Budget/Mid-range/Premium/Emerging |
| **Location Heatmap** | Interactive Folium map with ROI-colored zones |
| **Model Diagnostics** | Residual analysis, feature importance, error segmentation |
| **Executive Report** | Auto-generated HTML report with charts and recommendations |

---

## Project Structure

```
├── data/
│   ├── generate_data.py          # 20K Bangalore property generator
│   ├── DATA_DICTIONARY.md        # Complete field documentation
│   ├── raw/                      # Raw generated data
│   └── processed/                # Cleaned & engineered data
├── ml/
│   ├── scripts/
│   │   ├── cleaning_pipeline.py  # 6-step cleaning with diagnostics
│   │   ├── feature_engineering.py # 9 engineered features
│   │   ├── baseline_model.py     # Mean/Median/Location baselines
│   │   ├── train_models.py       # LR, DT, RF, XGBoost, ROI, Signal
│   │   ├── evaluate_models.py    # Metrics + 7 diagnostic plots
│   │   ├── clustering.py         # KMeans market segmentation
│   │   ├── recommendation_engine.py # Under/overpriced + buyer match
│   │   ├── generate_eda.py       # 10 EDA visualizations
│   │   └── generate_report.py    # Executive HTML report
│   ├── models/                   # Saved model artifacts (.pkl)
│   └── reports/                  # JSON reports + plot assets
├── dashboard/
│   └── app.py                    # Streamlit dashboard (9 tabs)
├── backend/
│   └── app/main.py               # FastAPI REST API
├── run_pipeline.py               # One-command pipeline runner
└── requirements.txt
```

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Full Pipeline
```bash
python run_pipeline.py
```

This executes the entire pipeline:
```
Data Generation -> Cleaning -> Feature Engineering -> EDA ->
Baseline Models -> Training -> Evaluation -> Clustering ->
Recommendations -> Executive Report
```

### 3. Launch Dashboard
```bash
streamlit run dashboard/app.py
```

Access at: **http://localhost:8501**

### 4. Run API (Optional)
```bash
uvicorn backend.app.main:app --reload --port 8000
```

---

## Pipeline Stages

### Stage 1: Data Generation
- **20,000** property listings across **20 Bangalore localities**
- 30 fields including price, location, sqft, amenities, distances, market trends
- Realistic price computation with age/type/furnishing/proximity adjustments

### Stage 2: Data Cleaning
- Missing values analysis & imputation
- Duplicate detection (ID + feature-based)
- IQR outlier removal per location
- Leakage checks
- Full cleaning report (JSON) with before/after row counts

### Stage 3: Feature Engineering
- **price_per_sqft** — Price normalized by area
- **location_score** — Composite (connectivity + safety + schools)
- **amenity_index** — Normalized amenity count
- **age_bucket** — Categorical age grouping
- **luxury_score** — Composite (sqft + amenities + furnishing)
- **distance_composite** — Weighted proximity to metro/school/hospital/CBD
- **value_ratio** — Price vs location median
- Label encoding + StandardScaler saved as artifacts

### Stage 4: Modeling
| Model | Type | Purpose |
|---|---|---|
| Linear Regression | Regression | Baseline parametric |
| Decision Tree | Regression | Interpretable |
| Random Forest | Regression | Ensemble |
| **XGBoost** | **Regression** | **Primary price model** |
| XGBoost ROI | Regression | ROI prediction |
| XGBoost Signal | Classification | Buy/Hold/Sell/Wait |

### Stage 5: Evaluation
- RMSE, MAE, MAPE, R2 for all models
- 7 diagnostic plots (residuals, actual vs predicted, feature importance, etc.)
- High-error segment analysis (top 5%)
- Location-wise error comparison

### Stage 6: Intelligence
- **Undervalued detection**: Actual < Predicted - 10%
- **Buyer matching**: Cosine similarity on preferences
- **Sell signals**: Multi-factor trend/ROI/demand analysis
- **Market clusters**: Budget / Mid-range / Premium / Emerging

---

## Bangalore Locations (20)

Whitefield, Indiranagar, Electronic City, Koramangala, HSR Layout, Sarjapur Road, Hebbal, Bannerghatta Road, Marathahalli, JP Nagar, Jayanagar, BTM Layout, Yelahanka, KR Puram, Rajajinagar, Malleswaram, Basavanagudi, Devanahalli, Kanakapura Road, Hennur

---

## Technology Stack

- **ML**: Python, Pandas, Scikit-learn, XGBoost
- **Visualization**: Matplotlib, Seaborn, Plotly
- **Dashboard**: Streamlit, Folium
- **API**: FastAPI, Uvicorn, Pydantic

---

## Output Artifacts

| File | Description |
|---|---|
| `data/raw/bangalore_properties.csv` | Raw 20K dataset |
| `data/processed/production_final.csv` | Final dataset with predictions |
| `ml/models/*.pkl` | Trained model files |
| `ml/reports/cleaning_report.json` | Cleaning diagnostics |
| `ml/reports/baseline_results.json` | Baseline model metrics |
| `ml/reports/evaluation_report.json` | Full evaluation metrics |
| `ml/reports/eda_report.html` | EDA visualization report |
| `ml/reports/executive_report.html` | Executive summary report |
| `ml/reports/assets/*.png` | All diagnostic plots |

---

*Developed as a production-level Data Science project for Bangalore real estate market analysis.*
