FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY index.html vite.config.js ./
COPY src ./src
RUN npm run build

FROM nginxinc/nginx-unprivileged:1.31.6-alpine3.24-slim
LABEL org.opencontainers.image.source="https://github.com/Godatcode/labpulse-devops-capstone" \
      org.opencontainers.image.title="LabPulse web" \
      org.opencontainers.image.description="LabPulse operations interface for shared campus labs"
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 8080
