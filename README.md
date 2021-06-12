# Public URL

http://smoothjazz.ddns.net

# Backend

---
**NOTE**

All commands run in the `./backend` directory

---

## Setup

1. Install dependencies: `pipenv install`

## Launch

1. Start server: `make run`

## Launch with docker

1. Build docker image: `docker build -t backend:v1 .`
2. Run docker image: `docker run -it --rm -p 50051:50051 backend:v1 pipenv run python server.py`
3. Exit: `{ctl-c}` twice

## Testing

1. Run tests: `make test`

# Reverse Proxy
Set up reverse proxy (from https://github.com/improbable-eng/grpc-web):
1. `cd proxy`
2. Download file: `./getProxy.sh`
3. Start proxy: `./proxy  --backend_addr=localhost:50051 --backend_tls=False --server_tls_cert_file=./misc/localhost.crt --server_tls_key_file=./misc/localhost.key --allow_all_origins --server_http_max_read_timeout=1h --server_http_max_write_timeout=1h`

## Launch with docker

1. `cd proxy`
2. Build docker image: `docker build -t proxy:v1 .`
3. Run docker image: `docker run -it --rm -p 8080:8080 proxy:v1 ./proxy --backend_addr=host.docker.internal:50051 --backend_tls=False --server_tls_cert_file=./misc/localhost.crt --server_tls_key_file=./misc/localhost.key --allow_all_origins --server_http_max_read_timeout=1h --server_http_max_write_timeout=1h`
4. Exit: `{ctl-c}`

# Frontend

---
**NOTE**

All commands run in the `./backend` directory

---

## Setup

1. Install NPM: `sudo apt-get install -y npm`
2. Install Ionic CLI: `npm install -g @ionic/cli`
3. Install NPM dependencies: `npm install`

## Launch

1. `ionic serve`

---
**NOTE**

It deploys to localhost:8100 by default. To deploy it to 0.0.0.0:8936, run `ionic serve --external -p 8936`

---

## Protobuf regeneration

1. `npm run prebuild`

## Launch with docker

1. Build app: `npm run build`
2. Build docker image: `docker build -t frontend:v1 .`
3. Run docker image: `docker run --rm -it -p 8100:80 frontend:v1`
4. Exit: `docker ps; docker stop {CONTAINER_ID}`

## Testing

1. Run tests: `ng test`

# To start all servers locally

1. Start: `./local_test.sh start`
2. navigate to http://localhost:8100
3. Stop: `./local_test.sh stop`

## Using docker compose

1. Start: `docker compose up`
2. navigate to http://localhost:8100
3. Stop: `{ctl-c}`
4. Cleanup: `docker compose down`

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

