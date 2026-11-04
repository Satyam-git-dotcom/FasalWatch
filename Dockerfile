# Multi-stage build: Frontend (React/Vite) + Backend (FastAPI/Python)
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and compiled frontend
COPY . ./
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

ENV PORT=8000
EXPOSE 8000

CMD ["python3", "server.py"]
