GEN=python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=.

.PHONY: gen clean

gen:
	@echo "Generating gRPC Python stubs from echo.proto..."
	@$(GEN) echo.proto
	@echo "Done."

clean:
	@rm -f echo_pb2.py echo_pb2_grpc.py
	@echo "Cleaned generated files."
