#!/bin/bash

start() {
  python3 ./grpc_server/server.py > backend.log 2>&1 &
  grpcwebproxy  --backend_addr=localhost:50051 --backend_tls=False --server_tls_cert_file=./grpc_server/misc/localhost.crt --server_tls_key_file=./grpc_server/misc/localhost.key --allow_all_origins --server_http_max_write_timeout=1h --server_http_max_read_timeout=1h > proxy.log 2>&1 &
  cd ./frontend && ionic serve > frontend.log 2>&1 &
}

stop() {
  pkill grpcwebproxy
  pkill ionic
  pkill -f "server.py"
}

if [[ "$1" = "start" ]]; then
  start
elif [[ "$1" = "stop" ]]; then
  stop
else
  echo "UNKNOWN COMMAND: $1"
fi
