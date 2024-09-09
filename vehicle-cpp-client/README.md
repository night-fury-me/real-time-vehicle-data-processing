# modern-vehicle-data-pipeline


### Generate Protobuf Code for C++ 

```bash
protoc --cpp_out=. --grpc_out=. --plugin=protoc-gen-grpc=`which grpc_cpp_plugin` vehicle_data.proto
```

### Vehicle Client Compilation command:

```bash
g++ -std=c++17 client.cpp vehicle_data.pb.cc vehicle_data.grpc.pb.cc -o client \
    `pkg-config --cflags protobuf grpc` \
    `pkg-config --libs protobuf grpc++ grpc` -lpthread
```

### Enter into Vehicle clients shell

```bash
docker-compose exec -it vehicle-cpp-client bash
```

### Start the sending vehicle data through gRPC

```bash
./client
```