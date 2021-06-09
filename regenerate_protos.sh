#!/bin/bash

protoc --plugin=protoc-gen-ts=./frontend/node_modules/.bin/protoc-gen-ts --js_out=import_style=commonjs,binary:frontend/proto-gen --ts_out=service=grpc-web:frontend/proto-gen -I ./backend/protos/ ./backend/protos/shengji.proto
cd backend
pipenv run python -m grpc_tools.protoc -I ./protos --python_out=. --grpc_python_out=. ./protos/shengji.proto