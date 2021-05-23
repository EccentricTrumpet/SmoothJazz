# syntax=docker/dockerfile:experimental
FROM node:15-alpine as builder

WORKDIR /app
COPY proto-gen /app/proto-gen
COPY resources /app/resources
COPY scripts /app/scripts
COPY src /app/src
COPY .browserslistrc *.json /app/

# Build app
RUN --mount=type=bind,source=node_modules,target=/app/node_modules npm run build -- --configuration production,ci

# Build hosting image
FROM nginx:1.15.8-alpine

COPY --from=builder /app/www/ /usr/share/nginx/html
