#!/bin/bash
set -e

echo "🚀 Starting AI Video Generation Full-Stack App..."

# Print environment info
echo "📊 Environment Variables:"
echo "   PORT: ${PORT:-8000}"
echo "   ENVIRONMENT: ${ENVIRONMENT:-production}"
echo "   HF_TOKEN: ${HF_TOKEN:+***SET***}"

# Check if frontend build exists
if [ -d "frontend_build" ]; then
    echo "✅ Frontend build found"
    echo "📁 Frontend files:"
    ls -la frontend_build/ | head -5
else
    echo "⚠️  Frontend build not found - API-only mode"
fi

# Check if video generator model files exist
if [ -d "models" ]; then
    echo "✅ Backend models found"
else
    echo "❌ Backend models not found"
fi

# Start the FastAPI server
echo "🎬 Starting FastAPI server on port ${PORT:-8000}..."
exec python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1