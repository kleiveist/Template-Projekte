# syntax=docker/dockerfile:1.7
FROM node:24.19.0-alpine3.24 AS build

WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./

# VITE_API_BASE_URL is public build-time configuration. Never pass secrets as VITE_* values.
ARG VITE_API_BASE_URL=http://127.0.0.1:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

FROM nginxinc/nginx-unprivileged:1.31.3-alpine3.24 AS runtime

COPY deployment/docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /build/frontend/dist /usr/share/nginx/html

USER 101:101
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1:8080/healthz || exit 1
