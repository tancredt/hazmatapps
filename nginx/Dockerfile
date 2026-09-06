# --- STAGE 1: Build Main Frontend ---
FROM node:26-alpine AS f1-builder
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# --- STAGE 2: Build District Cache Frontend ---
FROM node:26-alpine AS f2-builder
WORKDIR /app
COPY district-cache/package.json district-cache/package-lock.json ./
RUN npm ci
COPY district-cache/ ./
RUN npm run build

# --- STAGE 3: Backend Builder ---
FROM python:3.13-slim AS backend-builder
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
RUN python manage.py collectstatic --noinput

# --- STAGE 4: Final Nginx Image ---
FROM nginx:alpine
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=f1-builder /app/dist /usr/share/nginx/html/apps/inventory

COPY --from=f2-builder /app/dist /usr/share/nginx/html/apps/cache

COPY --from=backend-builder /app/staticfiles /usr/share/nginx/html/staticfiles

COPY --from=f1-builder /app/dist /usr/share/nginx/html/apps/inventory

COPY --from=f2-builder /app/dist /usr/share/nginx/html/apps/cache

# Copy backend static files
COPY --from=backend-builder /app/staticfiles /usr/share/nginx/html/staticfiles