all:	shengji

shengji:
	python3 -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. ./protos/shengji.proto

clean:
	rm -rf shengji_pb2*.py
