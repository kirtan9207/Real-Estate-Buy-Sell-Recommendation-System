#!/bin/bash

echo "🚀 Starting Real Estate Intelligence Platform (Production Mode)..."

# 1. Start Docker Containers
echo "🐳 Spinning up Infrastructure (DB, Backend, Frontend)..."
docker compose up -d

# 2. Wait for Database to be ready
echo "⏳ Waiting for PostgreSQL to be healthy..."
until docker exec real-estate-system-db-1 pg_isready -U user -d real_estate; do
  sleep 2
done

# 3. Initialize Schema
echo "🗄️ Initializing Database Schema (init.sql)..."
# This usually happens automatically via docker-entrypoint-initdb.d
# But for safety:
docker exec -i real-estate-system-db-1 psql -U user -d real_estate < database/init/init.sql

# 4. Run Data Pipeline (Generate, Train, Populate DB)
echo "📈 Synchronizing Market Intelligence Data..."
bash run-data-pipeline.sh

# 5. Open Browser
echo "🌐 Launching Market Dashboard..."
# For Windows
explorer "http://localhost:5173"

echo "🎯 System is UP and RUNNING."
echo "Dashboard: http://localhost:5173"
echo "API Docs: http://localhost:8000/docs"
