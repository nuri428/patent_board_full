# ============================================================
# Stage 1: Build
# ============================================================
FROM node:22-alpine AS builder

WORKDIR /app

# Install dependencies (cache layer)
COPY front_end/package.json front_end/package-lock.json* ./
RUN npm ci --legacy-peer-deps

# Copy source and build
COPY front_end/ .

# VITE_API_URL 미설정 시 상대경로 /api/v1 사용 (nginx proxy)
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# ============================================================
# Stage 2: Serve (nginx static)
# ============================================================
FROM nginx:alpine

# Built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# nginx 설정 (SPA routing + API proxy)
COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
