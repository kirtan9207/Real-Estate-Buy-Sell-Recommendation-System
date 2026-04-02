# Real Estate Intelligence Platform 🏡

This project is a complete property intelligence platform designed to help buyers and investors find undervalued properties using machine learning. It provides automated valuations, market segmentation, and investment signals (Buy/Sell/Hold).

## Why this exists?
Traditional real estate listing sites show you the price but don't tell you if it's a good deal. This system uses an ensemble of regressors (XGBoost, Random Forest, etc.) to predict the *fair market value* of properties and flags anything listed below its intrinsic value.

## 🚀 Tech Stack
- **Backend:** FastAPI (Python 3.11)
- **Frontend:** React + Vite (Dark Theme Dashboard)
- **Database:** PostgreSQL (with Dockerized Init scripts)
- **ML Engine:** Scikit-Learn, XGBoost, KMeans (Clustering)
- **Ops:** Docker, Docker Compose

## 🛠️ Getting Started

### Prerequisites
You'll need Docker installed on your machine.

### One-Command Setup
I've dockerized everything. Just run:
```bash
docker compose up --build
```
This will:
1. Spin up the Postgres database.
2. Build and start the FastAPI ML backend.
3. Start the React dashboard.

After it's running, you can access:
- **Dashboard:** [http://localhost:5173](http://localhost:5173)
- **Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

## 🏗️ System Architecture
1. **Data Pipeline:** Scripts in `ml/scripts/` handle cleaning and feature engineering (like Luxury Score and Location Ranking).
2. **ML Core:** We train a variety of models. Currently, XGBoost is our best performer for price prediction. We also use KMeans to cluster properties into *Budget, Mid-range, Premium,* and *Emerging* segments.
3. **API Service:** FastAPI connects to our stored models and gives real-time recommendations.
4. **The UI:** A financial-grade dark mode dashboard to visualize ROI and potential deals.

## 📊 Endpoints to Try
- `GET /undervalued`: List properties priced significantly below market value.
- `POST /predict`: Submit property details to get an AI valuation.
- `GET /clusters`: See how the market is currently segmented.
- `GET /trend?location=Riverside`: View historical price trends for a specific area.

## 📂 Project Structure
```text
├── backend/            # FastAPI app
├── frontend/           # React dashboard source
├── ml/                 # Machine Learning pipeline
│   ├── scripts/        # Training & cleaning scripts
│   ├── models/         # Saved .pkl models
│   └── reports/        # HTML EDA & Evaluation reports
├── data/               # Raw & Processed datasets
├── docker/             # Docker configuration
└── docker-compose.yml  # Orchestration
```

## Contributing
Feel free to open a PR for any fixes or enhancements!

*Built with ❤️ for real estate enthusiasts.*
