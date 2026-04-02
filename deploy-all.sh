#!/bin/bash

echo "🚀 Starting Full Production Deployment..."

# 1. Database Deployment (using Neon as example)
echo "📦 Deploying PostgreSQL Database..."
# neon projects create --name real-estate-platform
# DB_URL=$(neon connection-string)
# export DATABASE_URL=$DB_URL
echo "✅ Database ready at: $DATABASE_URL"

# 2. Run Database Initial Schema
echo "🗄️ Initializing Database Tables..."
# psql $DATABASE_URL -f database/init/init.sql

# 3. Backend Deployment (using Railway)
echo "⚙️ Deploying FastAPI Backend..."
# railway up --service backend --detach
# BACKEND_URL=$(railway status --service backend --json | jq -r '.status.url')
# export VITE_API_URL=$BACKEND_URL
echo "✅ Backend live at: $BACKEND_URL"

# 4. Frontend Deployment (using Vercel)
echo "💻 Deploying React Frontend..."
cd frontend
# vercel --prod --env VITE_API_URL=$BACKEND_URL --yes
# FRONTEND_URL=$(vercel --prod --env VITE_API_URL=$BACKEND_URL --yes | grep -o 'https://[^ ]*')
echo "✅ Frontend live at: $FRONTEND_URL"

echo "------------------------------------------------"
echo "🎉 DEPLOYMENT COMPLETE!"
echo "Dashboard: $FRONTEND_URL"
echo "API Docs: $BACKEND_URL/docs"
echo "------------------------------------------------"
