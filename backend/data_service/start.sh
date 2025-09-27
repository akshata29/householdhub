#!/bin/bash

# WealthOps Data Service Startup Script
# This script sets up and starts the data service

echo "🚀 Starting WealthOps Data Service..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "📝 Please update .env with your database credentials"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating Python virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Load environment variables
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Start the service
echo "🌐 Starting FastAPI service on http://localhost:${SERVICE_PORT:-8000}..."
echo "📊 Health check available at: http://localhost:${SERVICE_PORT:-8000}/health"
echo "📖 API documentation: http://localhost:${SERVICE_PORT:-8000}/docs"
echo ""
echo "Press Ctrl+C to stop the service"

uvicorn main:app --host ${SERVICE_HOST:-0.0.0.0} --port ${SERVICE_PORT:-8000} --reload