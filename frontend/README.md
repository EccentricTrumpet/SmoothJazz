To start frontend ionic app locally:
0- cd frontend/
1- sudo apt-get install -y npm
2- npm install -g @ionic/cli
3- In the frontend folder, run `npm install`
4- In the frontend folder, run `ionic serve`
NOTE: It deploys to localhost:8100 by default. To deploy it to 0.0.0.0:8936, run `ionic serve --external -p 8936`

To compile new versions of the generated .d.ts file for the protobuf definition:
cd frontend/
protoc --plugin=protoc-gen-ts=./node_modules/.bin/protoc-gen-ts --js_out=import_style=commonjs,binary:proto-gen --ts_out=service=grpc-web:proto-gen -I ../grpc_server/protos/ ../grpc_server/protos/shengji.proto
