all: clean proto

proto:
	python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. ./protos/shengji.proto

clean:
	rm -rf shengji_pb2*.py

game_state_test:
	python game_state_test.py

server_test:
	python server_test.py

test: proto game_state_test server_test

run: proto
	python server.py

run_local_testing: proto
	python server.py --delay_sec=0
