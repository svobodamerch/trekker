FROM python:3.9-slim

WORKDIR /app

# Copy backend files
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# Set environment
ENV PYTHONPATH=/app
ENV PORT=8000

# Run migrations and start server
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
