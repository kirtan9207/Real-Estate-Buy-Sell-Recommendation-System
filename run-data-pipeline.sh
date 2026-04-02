#!/bin/bash

echo "🚀 Starting Production Data Pipeline..."

# 1. Generate 20,000 realistic records
echo "📊 Generating synthetic market data..."
python data/generate_data.py

# 2. Clean data
echo "🧹 Cleaning raw datasets..."
python ml/scripts/cleaning_pipeline.py

# 3. Engineer features
echo "⚙️ Engineering intelligence features..."
python ml/scripts/feature_engineering.py

# 4. Train Models & Synchronize Database
echo "🤖 Training Price/ROI/Signal models..."
# Wait for DB to be ready before training
export DATABASE_URL="postgresql://user:password@localhost:5432/real_estate"
python ml/scripts/train_models.py

echo "✅ Pipeline Complete. Intelligence models and database are synchronized."
