# Multi-stage build for React + FastAPI
FROM node:18-alpine AS frontend-build

# Set working directory for frontend build
WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install frontend dependencies
RUN npm ci --omit=dev || npm install --omit=dev

# Copy frontend source code
COPY frontend/ .

# Build React app (make sure this actually works)
RUN npm run build

# Debug: List what was actually built
RUN echo "=== BUILD CONTENTS ===" && ls -la build/ && \
    echo "=== STATIC CONTENTS ===" && ls -la build/static/ || echo "No static directory" && \
    echo "=== CSS CONTENTS ===" && ls -la build/static/css/ || echo "No CSS directory" && \
    echo "=== JS CONTENTS ===" && ls -la build/static/js/ || echo "No JS directory"

# Stage 2: Python backend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ .

# Copy built frontend from previous stage to the expected location
COPY --from=frontend-build /app/frontend/build ./frontend_build

# Debug: Verify the copy worked
RUN echo "=== COPIED FRONTEND BUILD ===" && ls -la frontend_build/ && \
    echo "=== COPIED STATIC FILES ===" && ls -la frontend_build/static/ || echo "No static in copied build" && \
    echo "=== INDEX.HTML CHECK ===" && head -20 frontend_build/index.html || echo "No index.html"

# Create directories for generated content
RUN mkdir -p static/generated_videos

# Copy startup script
COPY start.sh .
RUN chmod +x start.sh

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["./start.sh"]
