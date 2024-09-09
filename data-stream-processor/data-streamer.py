import os
import json

from typing import Iterable
from pyflink.common import WatermarkStrategy, Encoder
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream import StreamExecutionEnvironment, SinkFunction
from pyflink.datastream.connectors import FileSink, RollingPolicy, OutputFileConfig
from pyflink.datastream.connectors.kafka import KafkaOffsetsInitializer, KafkaSource
from pyflink.datastream import ProcessWindowFunction

from pyflink.common.time import Time
from pyflink.datastream.window import TumblingEventTimeWindows
from pyflink.datastream import KeyedProcessFunction, OutputTag
from pyflink.datastream.functions import MapFunction, ProcessWindowFunction
from pyflink.datastream.state import ValueStateDescriptor
from pyflink.common import Duration
from datetime import datetime 

from google.cloud import bigquery

class JsonParser(MapFunction):
    def map(self, value):
        data = json.loads(value)
        vehicle_id = data.get("vehicleId")
        telemetry = data.get("telemetry", {})
        
        speed = telemetry.get("speed", 0.0)
        rpm = telemetry.get("rpm", 0.0)
        fuel_level = telemetry.get("fuelLevel", 0.0)
        engine_temp = telemetry.get("engineTemp", 0.0)
        battery_voltage = telemetry.get("batteryVoltage", 0.0)
        odometer = telemetry.get("odometer", 0.0)

        timestamp_str = data.get("timestamp", "")
        timestamp = datetime.fromisoformat(timestamp_str)  

        return (vehicle_id, (speed, rpm, fuel_level, engine_temp, battery_voltage, odometer), timestamp.timestamp())  


class BigQueryInsertMapFunction(MapFunction):
    def map(self, value):
       
        with bigquery.Client() as client:

            table_id = 'vehicle-data-processing.vehicle_data.TelemetryData'

            vehicle_id, avg_speed, avg_rpm, avg_fuel_level, avg_engine_temp, avg_battery_voltage, avg_odometer = value
            
            current_timestamp = datetime.utcnow().isoformat()

            rows_to_insert = [{
                "vehicleId": vehicle_id,
                "avg_speed": avg_speed,
                "avg_rpm": avg_rpm,
                "avg_fuel_level": avg_fuel_level,
                "avg_engine_temp": avg_engine_temp,
                "avg_battery_voltage": avg_battery_voltage,
                "avg_odometer": avg_odometer,
                "timestamp": current_timestamp
            }]

            errors = client.insert_rows_json(table_id, rows_to_insert)

            if errors:
                print(f"Encountered errors while inserting rows: {errors}")
            else:
                print(f"Inserted row into BigQuery: {rows_to_insert}")
            
            return value

class AverageAggregate(ProcessWindowFunction):
    def __init__(self):
        self.sum_speed_descriptor = ValueStateDescriptor("sum_speed", Types.FLOAT())
        self.sum_rpm_descriptor = ValueStateDescriptor("sum_rpm", Types.FLOAT())
        self.sum_fuel_level_descriptor = ValueStateDescriptor("sum_fuel_level", Types.FLOAT())
        self.sum_engine_temp_descriptor = ValueStateDescriptor("sum_engine_temp", Types.FLOAT())
        self.sum_battery_voltage_descriptor = ValueStateDescriptor("sum_battery_voltage", Types.FLOAT())
        self.sum_odometer_descriptor = ValueStateDescriptor("sum_odometer", Types.FLOAT())
        self.count_descriptor = ValueStateDescriptor("count", Types.INT())

    def open(self, runtime_context):
        self.sum_speed = runtime_context.get_state(self.sum_speed_descriptor)
        self.sum_rpm = runtime_context.get_state(self.sum_rpm_descriptor)
        self.sum_fuel_level = runtime_context.get_state(self.sum_fuel_level_descriptor)
        self.sum_engine_temp = runtime_context.get_state(self.sum_engine_temp_descriptor)
        self.sum_battery_voltage = runtime_context.get_state(self.sum_battery_voltage_descriptor)
        self.sum_odometer = runtime_context.get_state(self.sum_odometer_descriptor)
        self.count = runtime_context.get_state(self.count_descriptor)

    def process(
        self, 
        key, 
        context: 'ProcessWindowFunction.Context', 
        elements: Iterable[tuple]):

        sum_speed = 0.0
        sum_rpm = 0.0
        sum_fuel_level = 0.0
        sum_engine_temp = 0.0
        sum_battery_voltage = 0.0
        sum_odometer = 0.0
        count = 0
        
        for element in elements:
            vehicle_id, (speed, rpm, fuel_level, engine_temp, battery_voltage, odometer), timestamp = element
            sum_speed += speed
            sum_rpm += rpm
            sum_fuel_level += fuel_level
            sum_engine_temp += engine_temp
            sum_battery_voltage += battery_voltage
            sum_odometer += odometer
            count += 1

        if count > 0:
            avg_speed = sum_speed / count
            avg_rpm = sum_rpm / count
            avg_fuel_level = sum_fuel_level / count
            avg_engine_temp = sum_engine_temp / count
            avg_battery_voltage = sum_battery_voltage / count
            avg_odometer = sum_odometer / count
            result = (key, avg_speed, avg_rpm, avg_fuel_level, avg_engine_temp, avg_battery_voltage, avg_odometer)

            yield result

    def clear(self, context: 'ProcessWindowFunction.Context') -> None:
        self.sum_speed.clear()
        self.sum_rpm.clear()
        self.sum_fuel_level.clear()
        self.sum_engine_temp.clear()
        self.sum_battery_voltage.clear()
        self.sum_odometer.clear()
        self.count.clear()


def flink_consumer():
    # Create a StreamExecutionEnvironment
    env = StreamExecutionEnvironment.get_execution_environment()

    # the kafka/sql jar is used here as it's a fat jar and could avoid dependency issues
    env.add_jars("file:///jars/flink-sql-connector-kafka-3.0.1-1.18.jar")

    # Define the new kafka source with our docker brokers/topics
    # This creates a source which will listen to our kafka broker
    # on the topic we created. It will read from the earliest offset
    # and just use a simple string schema for serialization (no JSON/Proto/etc)
    kafka_source = (
        KafkaSource.builder()
        .set_bootstrap_servers(os.environ["KAFKA_BROKER"])
        .set_topics(os.environ["KAFKA_TOPIC"])
        .set_group_id("flink_group")
        .set_starting_offsets(KafkaOffsetsInitializer.earliest())
        .set_value_only_deserializer(SimpleStringSchema())
        .build()
    )

    # Adding our kafka source to our environment
    watermark_strategy = WatermarkStrategy.for_bounded_out_of_orderness(
        Duration.of_seconds(5))
    ds = env.from_source(
        kafka_source, watermark_strategy, "Kafka Source"
    )

    # Parse JSON and extract fields
    parsed_stream = ds.map(
        JsonParser(), 
        output_type=Types.TUPLE([
            Types.STRING(), 
            Types.TUPLE([
                Types.FLOAT(), 
                Types.FLOAT(), 
                Types.FLOAT(), 
                Types.FLOAT(), 
                Types.FLOAT(), 
                Types.FLOAT()
            ]), 
            Types.FLOAT()
        ])
    )

    # Key by vehicleId
    keyed_stream = parsed_stream.key_by(lambda x: x[0])

    # Apply a tumbling window of 15 seconds and aggregate
    windowed_stream   = keyed_stream.window(
        TumblingEventTimeWindows.of(Time.seconds(5)))

    aggregated_stream = windowed_stream.process(
        AverageAggregate(), 
        output_type=Types.TUPLE([
            Types.STRING(), 
            Types.FLOAT(), 
            Types.FLOAT(), 
            Types.FLOAT(), 
            Types.FLOAT(), 
            Types.FLOAT(), 
            Types.FLOAT()
        ])
    )

    # Insert into bigquery
    aggregated_stream.map(
        BigQueryInsertMapFunction(), 
        output_type=Types.TUPLE([
            Types.STRING(), 
            Types.FLOAT(), 
            Types.FLOAT(), 
            Types.FLOAT(), 
            Types.FLOAT(), 
            Types.FLOAT(), 
            Types.FLOAT()
        ])
    )

    # Print the results to stdout
    aggregated_stream.print()

    # Execute the job and submit the job
    env.execute("Flink Consumer - BigQuery Sink")

if __name__ == "__main__":
    flink_consumer()

