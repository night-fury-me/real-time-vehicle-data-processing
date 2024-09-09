### Install relevant packages

```bash
pip install grpcio-tools protobuf confluent-kafka
```

### Generate gRPC and protobuf python code

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. vehicle_data.proto
```

### Start ZooKeeper:

Kafka uses ZooKeeper to manage distributed brokers. Start ZooKeeper before starting Kafka:

```bash
sudo systemctl start zookeeper
```

You can enable it at boot using:

```bash
sudo systemctl enable zookeeper
```
### Start Kafka:
Now you can start the Kafka broker:

```bash
sudo systemctl start kafka
```

Enable Kafka at boot:

```bash
sudo systemctl enable kafka
```

### Enter into Data Stream Producers shell

```bash
docker-compose exec -it data-producer bash 
```

### Run the gRPC Server
Run the Python gRPC server script:

```bash
python grpc_server.py
```

### Configure Kafka Topic
Ensure that the Kafka topic (vehicle-data-topic in the example) exists:

```bash
kafka-topics --create --topic vehicle-data-topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```


### Consume Kafka messages from a topic using console
Use kafka-console-consumer to read raw messages from the topic:

```bash
kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic vehicle-data-topic --from-beginning
```