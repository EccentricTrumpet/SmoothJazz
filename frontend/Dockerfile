FROM smoothjazz.azurecr.io/frontend-builder:node15-alpine as builder

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci --production

# Build app
COPY . /app
RUN npm run build -- --configuration production,ci

# Build hosting image
FROM nginx:1.15.8-alpine

COPY --from=builder /app/www/ /usr/share/nginx/html
