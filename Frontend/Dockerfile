# ---------- Build Stage ----------
FROM node:20-slim AS builder

# Install dependencies needed for building Angular apps
RUN apt-get update && apt-get install -y python3 make git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy package files
COPY package.json ./
COPY package-lock.json* ./

# Install Angular CLI and dependencies
RUN npm install -g @angular/cli
RUN npm install

# Copy the rest of the application source
COPY . .

# Build the Angular application for development
RUN npm run build:dev

# Debug: Show the dist folder structure
RUN ls -la dist/ && echo "=== Browser folder ===" && ls -la dist/audit-framework/browser/

# ---------- Runtime Stage ----------
FROM node:20-slim

# Install a minimal HTTP server
RUN npm install -g http-server

WORKDIR /app

# Copy the built application - Angular 17+ creates browser directory
COPY --from=builder /app/dist/audit-framework/browser ./dist

EXPOSE 4200

# Serve the application from the browser directory
CMD ["http-server", "dist", "-p", "4200", "-c-1"]