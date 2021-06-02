# Public URL

http://smoothjazz.ddns.net

# Backend
Installation:
pip3 install grpcio
pip3 install grpcio-tools

Local testing:
1. start the server: python3 backend/server.py
2. start a client that creates a game, then listens for game update: python3 streaming_client.py
3. start a client that updates the game: python3 backend/updating_client.py

## Using docker

1. `cd backend`
2. Build docker image: `docker build -t backend:v1 .`
3. Run docker image: `docker run -it --rm -p 50051:50051 backend:v1 pipenv run python server.py`
4. Exit: `{ctl-c}` twice

# Reverse Proxy
Set up reverse proxy (from https://github.com/improbable-eng/grpc-web):
1. `cd proxy`
2. Download file: `./getProxy.sh`
3. Start proxy: `./proxy  --backend_addr=localhost:50051 --backend_tls=False --server_tls_cert_file=./misc/localhost.crt --server_tls_key_file=./misc/localhost.key --allow_all_origins --server_http_max_read_timeout=1h --server_http_max_write_timeout=1h`

Alternative installation to build from binary:
1. Install golang
2. Follow instructions from https://github.com/improbable-eng/grpc-web/tree/master/go/grpcwebproxy

## Using docker

1. `cd proxy`
2. Build docker image: `docker build -t proxy:v1 .`
3. Run docker image: `docker run -it --rm -p 8080:8080 proxy:v1 ./proxy --backend_addr=host.docker.internal:50051 --backend_tls=False --server_tls_cert_file=./misc/localhost.crt --server_tls_key_file=./misc/localhost.key --allow_all_origins --server_http_max_read_timeout=1h --server_http_max_write_timeout=1h`
4. Exit: `{ctl-c}`

# Frontend
To start frontend ionic app locally:
1. `cd frontend`
2. sudo apt-get install -y npm
3. npm install -g @ionic/cli
4. `npm install`
5. `ionic serve`
NOTE: It deploys to localhost:8100 by default. To deploy it to 0.0.0.0:8936, run `ionic serve --external -p 8936`

To compile new versions of the generated .d.ts file for the protobuf definition:
protoc --plugin=protoc-gen-ts=./frontend/node_modules/.bin/protoc-gen-ts --js_out=import_style=commonjs,binary:frontend/proto-gen --ts_out=service=grpc-web:frontend/proto-gen -I ./backend/protos/ ./backend/protos/shengji.proto

## Using docker

1. `cd frontend`
2. `npm install`
3. `npm run build`
4. Build docker image: `docker build -t frontend:v1 .`
5. Run docker image: `docker run --rm -it -p 8100:80 frontend:v1`
6. Exit: `docker ps; docker stop {CONTAINER_ID}`

# To start all servers locally
1. Start: `./local_test.sh start`
2. navigate to http://localhost:8100
3. Stop: `./local_test.sh stop`

## Using docker compose

1. Start: `docker compose up`
2. navigate to http://localhost:8100
3. Stop: `{ctl-c}`
4. Cleanup: `docker compose down`

# Testing

## Backend

Requirements
1. Python dependencies

```console
$ cd backend
$ python *test.py
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
# Deployment

## Prerequisites

1. Azure CLI
2. Kubectl: `az aks install-cli`

## Tag and push docker images

1. `az login`
2. `az acr login -n smoothjazz`
3. `docker tag backend:v1 smoothjazz.azurecr.io/backend:v1`
4. `docker tag proxy:v1 smoothjazz.azurecr.io/proxy:v1`
5. `docker tag frontend:v1 smoothjazz.azurecr.io/frontend:v1`
6. `docker push smoothjazz.azurecr.io/backend:v1`
7. `docker push smoothjazz.azurecr.io/proxy:v1`
8. `docker push smoothjazz.azurecr.io/frontend:v1`

## Kubernetes deployment

1. `kubectl apply -f kubernetes.yml`

