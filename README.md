# Backend
Installation:
pip3 install grpcio
pip3 install grpcio-tools

Local testing:
1- start the server: python3 grpc_server/server.py
2- start a client that creates a game, then listens for game update: python3 streaming_client.py
3- start a client that updates the game: python3 grpc_server/updating_client.py

# Reverse Proxy
Set up reverse proxy (from https://github.com/improbable-eng/grpc-web):
1 - Download grpcwebproxy binary from https://github.com/improbable-eng/grpc-web/releases
2- Ran `grpcwebproxy  --backend_addr=localhost:50051 --backend_tls=False --server_tls_cert_file=./misc/localhost.crt --server_tls_key_file=./misc/localhost.key --allow_all_origins --server_http_max_read_timeout=1h --server_http_max_write_timeout=1h` to start the proxy

Alternative installation to build from binary:
1- Install golang
2- Follow instructions from https://github.com/improbable-eng/grpc-web/tree/master/go/grpcwebproxy

# Frontend
To start frontend ionic app locally:
0- cd frontend/
1- sudo apt-get install -y npm
2- npm install -g @ionic/cli
3- In the frontend folder, run `npm install`
4- In the frontend folder, run `ionic serve`
NOTE: It deploys to localhost:8100 by default. To deploy it to 0.0.0.0:8936, run `ionic serve --external -p 8936`

To compile new versions of the generated .d.ts file for the protobuf definition:
protoc --plugin=protoc-gen-ts=./frontend/node_modules/.bin/protoc-gen-ts --js_out=import_style=commonjs,binary:frontend/proto-gen --ts_out=service=grpc-web:frontend/proto-gen -I ./grpc_server/protos/ ./grpc_server/protos/shengji.proto

# To start all servers locally
Run `./local_test.sh start` and navigate to http://localhost:8100 in browser

# To stop all servers
Run `./local_test.sh stop`

# Testing

## Backend

Requirements
1. Python dependencies

```console
$ cd backend
$ python test.py
```

## Frontend

Requirements
1. Angular CLI
2. NPM package dependencies
3. Chrome browser

```console
$ cd frontend
$ ng test
```
