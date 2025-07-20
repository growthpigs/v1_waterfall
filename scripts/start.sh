#!/bin/bash

# Brand BOS Backend Startup Script for Render
# This script ensures proper initialization on Render's infrastructure

echo "🚀 Starting Brand BOS Backend..."

# Set default PORT if not provided (Render provides this)
export PORT=${PORT:-8080}

# Ensure we're in the correct directory
cd /app

# Create necessary directories
mkdir -p /app/logs

# Log environment info (without secrets)
echo "📋 Environment Information:"
echo "  - Port: $PORT"
echo "  - Environment: ${ENVIRONMENT:-production}"
echo "  - Python Version: $(python --version)"
echo "  - Working Directory: $(pwd)"

# Health check function
health_check() {
    echo "🏥 Performing startup health check..."
    timeout 5 python -c "
import os
import sys

# Check critical environment variables
required_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY', 'ANTHROPIC_API_KEY']
missing = [var for var in required_vars if not os.getenv(var)]

if missing:
    print(f'❌ Missing required environment variables: {missing}')
    sys.exit(1)
else:
    print('✅ All required environment variables are set')
"
}

# Run health check
health_check

# Start the application
echo "🎯 Starting Uvicorn server on 0.0.0.0:$PORT"
exec uvicorn src.main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers 1 \
    --loop uvloop \
    --log-level ${LOG_LEVEL:-info} \
    --access-log \
    --use-colors