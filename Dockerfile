# Stage 1: build frontend
FROM node:22-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: runtime
FROM python:3.12-slim
WORKDIR /app

# Install Python deps (no uv needed in prod — plain pip is fine)
COPY backend/pyproject.toml ./
RUN pip install --no-cache-dir fastapi "uvicorn[standard]" pydantic openai python-dotenv websockets aiofiles

COPY backend/ ./
COPY --from=frontend-build /app/frontend/dist ./frontend/dist
COPY data/ ./data/
COPY saves/ ./saves/

ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
