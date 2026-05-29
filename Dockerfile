FROM python:3.9-slim

WORKDIR /workspace

COPY . .
RUN pip install --no-cache-dir -r backend/requirements.txt

WORKDIR /workspace/backend

ENV PYTHONPATH=/workspace/backend
ENV PORT=8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
