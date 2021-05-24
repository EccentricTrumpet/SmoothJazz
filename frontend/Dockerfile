FROM node:15-alpine as builder

# Copy files
WORKDIR /app
COPY . /app

# Build app
RUN npm run build -- --configuration production,ci

# Build hosting image
FROM nginx:1.15.8-alpine

COPY --from=builder /app/www/ /usr/share/nginx/html
