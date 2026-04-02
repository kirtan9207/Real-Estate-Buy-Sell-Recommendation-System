# Real Estate Intelligence Platform

A complete production-grade property intelligence system designed for real estate investors and market analysts. The platform utilizes machine learning to identify undervalued properties, forecast ROI, and generate strategic buy/sell signals across emerging market clusters.

## Core Features

- **Strategic AI Valuer**: High-precision price prediction engine using XGBoost trained on 20,000+ realistic market listings.
- **Investment Signals**: Automated buy/hold/sell logic based on 5-year ROI forecasts and local market momentum.
- **Geographical Heatmaps**: Interactive Leaflet-based visualization of ROI distribution and regional demand scores.
- **Market Segmentation**: KMeans clustering to categorize the market into Budget, Mid-range, Premium, and Emerging High-Growth zones.
- **Advanced ROI Analytics**: Deep-dive analytics for rental yield estimation and appreciation trends.

## Technical Architecture

The platform is designed as a modular micro-services architecture for scalability:

1. **ML Pipeline**: Automated cleaning, feature engineering (Location & Luxury scores), and multi-model training/serialization. 
2. **Backend API**: Optimized FastAPI service providing structured JSON responses for complex financial reports.
3. **Frontend Dashboard**: Responsive React + Vite application with professional dashboard components, Recharts for data visualization, and Lucide-React for typography-driven iconography.
4. **Data Engine**: Synthetic yet realistic data generator producing high-fidelity datasets with 20,000 samples including builder reputation, connectivity scores, and historical trends.

## Technology Stack

- **ML**: Python, Pandas, Scikit-learn, XGBoost
- **API**: FastAPI, Uvicorn, Pydantic
- **Development**: Docker, Docker Compose
- **Frontend**: React, Recharts, Leaflet, Tailwind (Design Tokens)

## Getting Started

### Local Setup (Docker)

To run the full production stack:

```bash
docker compose up --build
```

Access the components at:
- Dashboard: http://localhost:5173
- API Documentation: http://localhost:8000/docs
- Database: Local PostgreSQL (exposed on port 5432)

### ML Training Pipeline

If updates to the model logic are required, individual scripts can be executed:

```bash
# Clean data
python ml/scripts/cleaning_pipeline.py

# Engineer features
python ml/scripts/feature_engineering.py

# Train Production Ensemble
python ml/scripts/train_models.py
```

## Future Improvements

- Implementation of user authentication (JWT) for private investment portfolios.
- Automated API deployment to Render/Railway using terraform or shell-based CI/CD scripts.
- Integration of live web-scraped data from major property listing platforms.

---
Project developed as a production-level data product.
