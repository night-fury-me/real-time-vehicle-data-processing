> _This repository contains real-time data processing data pipeline using technologies like - `gRPC`, `Apache Kafka`, `Apache Flink`, `Google BigQuery`. The base framework for this project was adapted from the [flink-with-python](https://github.com/afoley587/flink-with-python) repository._


## Real-time vehicle data processing pipeline
The Real-Time Vehicle Data Processing Pipeline efficiently manages and analyzes vehicle data through a cohesive system. The Vehicle C++ Client collects real-time telemetry data and transmits it via gRPC. This data is then ingested by the Kafka Data Producer, which streams it into Kafka topics. Apache Flink processes the streaming data, performs aggregations and real-time analytics, and writes the results to Google BigQuery for comprehensive storage and analysis. This pipeline ensures seamless data flow and insightful analysis, optimizing vehicle management and performance. 

<img src="/images/vehicle-data-pipeline.png" alt="Image description" height="70%">

### Usage

To start all the containers - `Vehicle C++ Client`, `Kafka Data Producer (gRPC Server)`, `Flink Data Streamer (BigQuery Sink Client)`

```bash
docker-compose up -d  
```

### Enter into flink consumers shell

```bash
docker-compose exec -it data-streamer bash 
```

### Submit a flink job in the flink cluster

```bash
/flink/bin/flink run -py /taskscripts/data-streamer.py --jobmanager jobmanager:8081 --target local
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

### Enter into Vehicle clients shell

```bash
docker-compose exec -it vehicle-cpp-client bash
```

### Start the sending vehicle data through gRPC

```bash
./client
```

### Turn of all the processes
```bash
docker-compose down 
```

