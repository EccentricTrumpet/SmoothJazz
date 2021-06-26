#!/bin/bash

(cd frontend; npm run prebuild)
(cd backend; pipenv run python -m grpc_tools.protoc -I ./protos --python_out=. --grpc_python_out=. ./protos/shengji.proto)
