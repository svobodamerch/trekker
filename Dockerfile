FROM python:3.9-slim

WORKDIR /app

# Copy everything first
COPY . .

# Install dependencies from backend
RUN pip install --no-cache-dir -r backend/requirements.txt

# Set working directory to backend
WORKDIR /app/backend

# Set environment
ENV PYTHONPATH=/app/backend
ENV PORT=8000

# Run migrations and start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
