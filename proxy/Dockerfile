FROM alpine:3.7

WORKDIR /app
COPY . /app

RUN apk --no-cache add curl
RUN ./getProxy.sh