# Real Estate Intelligence Platform (Buy/Sell Recommender)

A production-level property intelligence system that uses machine learning to predict property prices, identify undervalued assets, and recommend optimal buy/sell timings.

## Features
- **AI Price Prediction**: Multi-regressor ensemble (XGBoost, Random Forest, etc.) to estimate property market value.
- **Undervalued Asset Detection**: Real-time identification of properties listed below their intrinsic market value.
- **ROI Analytics**: Automated calculation of estimated Return on Investment based on location trends and luxury scores.
- **Market Segmentation**: KMeans clustering for segmenting properties into Budget, Mid-range, Premium, and Emerging areas.
- **Sell Strategy**: Logic-based signals (Sell/Hold/Wait) based on market momentum.
- **Premium Dashboard**: Dark-theme financial dashboard built with React, Recharts, and Lucide icons.

## System Architecture
`Data Pipeline -> Feature Engineering -> Model Hub -> FastAPI -> React Dashboard`

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 20+

### Option 1: Docker (Recommended)
```bash
docker-compose up --build
```
Access the dashboard at `http://localhost:5173` and API at `http://localhost:8000`.

### Option 2: Local Development
1. **Backend & ML**:
   ```bash
   pip install -r requirements.txt
   # Generate and train
   python data/generate_data.py
   python ml/scripts/cleaning_pipeline.py
   python ml/scripts/feature_engineering.py
   python ml/scripts/train_models.py
   # Run server
   uvicorn backend.app.main:app --reload
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## ML Components
- **Data Reports**: Located in `ml/reports/` (EDA and Evaluation).
- **Saved Models**: Located in `ml/models/`.
- **Database Schema**: Located in `database/init/init.sql`.

## License
MIT
