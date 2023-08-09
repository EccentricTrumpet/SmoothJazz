PYTHON := python3

all: clean proto

proto:
	$(PYTHON) -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. ./protos/shengji.proto

clean:
	rm -rf shengji_pb2*.py

game_state_test:
	$(PYTHON) game_state_test.py

server_test:
	$(PYTHON) server_test.py

test: proto game_state_test server_test

run: proto
	$(PYTHON) server.py

run_local_testing: proto
	$(PYTHON) server.py --delay_sec=0

version:
	$(PYTHON) --version
