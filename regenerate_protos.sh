#!/bin/bash

protoc --js_out=import_style=commonjs,binary:proto-gen --grpc-web_out=import_style=typescript,mode=grpcwebtext:proto-gen -I ./backend/protos/ ./backend/protos/shengji.proto
cd backend
pipenv run python -m grpc_tools.protoc -I ./protos --python_out=. --grpc_python_out=. ./protos/shengji.proto