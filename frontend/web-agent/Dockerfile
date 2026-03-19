# ============================================================
# INSIGHT-311 Frontend — React + Vite Operator Dashboard
# ============================================================

# --- Stage 1: Build the production bundle ---
FROM node:18-alpine AS build

WORKDIR /app

# Copy package files first (Docker layer caching)
COPY package.json package-lock.json* ./
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build

# --- Stage 2: Serve with lightweight Nginx ---
FROM nginx:stable-alpine

# Copy the production build to Nginx's serve directory
COPY --from=build /app/dist /usr/share/nginx/html

# Custom Nginx config (SPA routing — all paths → index.html)
RUN echo 'server { \
    listen 80; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
