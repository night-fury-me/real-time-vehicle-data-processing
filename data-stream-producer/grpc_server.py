from concurrent import futures
from confluent_kafka import Producer
from google.protobuf import json_format

import os
import grpc
import vehicle_data_pb2
import vehicle_data_pb2_grpc


# Kafka configuration
kafka_conf = {
    'bootstrap.servers': os.environ["KAFKA_BROKER"]
}

# Create a Kafka producer
producer = Producer(kafka_conf)

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

class VehicleDataStreamerServicer(vehicle_data_pb2_grpc.VehicleDataStreamerServicer):
    def StreamVehicleData(self, request_iterator, context):
        for idx, vehicle_data in enumerate(request_iterator):
            # Serialize the Protobuf message to bytes
            # serialized_data = vehicle_data.SerializeToString()
            serialized_data = json_format.MessageToJson(vehicle_data)
            print(f"{idx}:: {serialized_data}")
            # Produce the message to Kafka
            producer.produce(os.environ["KAFKA_TOPIC"], value=serialized_data, callback=delivery_report)
            producer.flush()

        return vehicle_data_pb2.StreamResponse(status="Data received")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    vehicle_data_pb2_grpc.add_VehicleDataStreamerServicer_to_server(VehicleDataStreamerServicer(), server)
    server.add_insecure_port(os.environ["GRPC_SERVER"])  # Port for the gRPC server
    server.start()
    print(f"gRPC server is running on port {os.environ['GRPC_SERVER']}")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
