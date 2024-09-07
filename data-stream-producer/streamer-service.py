class VehicleDataStreamerServicer(vehicle_data_pb2_grpc.VehicleDataStreamerServicer):
    def StreamVehicleData(self, request_iterator, context):
        for vehicle_data in request_iterator:
            # Serialize the Protobuf message to bytes
            serialized_data = vehicle_data.SerializeToString()

            # Produce the message to Kafka
            producer.produce('vehicle-data-topic', value=serialized_data, callback=delivery_report)
            producer.flush()

        return vehicle_data_pb2.StreamResponse(status="Data received")