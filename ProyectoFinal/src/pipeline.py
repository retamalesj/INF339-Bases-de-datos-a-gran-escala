import os
import apache_beam as beam
import json
import pyarrow as pa
from datetime import datetime as dt, UTC

from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from confluent_kafka import Producer
from random_data_generator import send_json_to_kafka
from data_extraction import extract_batch_fields, extract_streaming_fields

INPUT_PATH = 'output.json'

STREAMING_SCHEMA_PATH = 'resources/VehicleTelemetry.avsc' # Para data de streaming
BATCH_SCHEMA_PATH = 'resources/Sensors.avsc' # Para data batch

STREAMING_OUTPUT_PATH = os.path.join('output/streaming', f"vehicletelemetry_{dt.now().strftime("%Y%m%dT%H%M%S")}")
BATCH_OUTPUT_PATH = os.path.join('output/batch', f"sensors_{dt.now().strftime("%Y%m%dT%H%M%S")}")

KAFKA_BROKERS = 'kafka:19092'
KAFKA_STREAMING_TOPIC = 'TerramEarthStreaming'
KAFKA_BATCH_TOPIC = 'TerramEarthBatch'

batch_schema = pa.schema([
    pa.field('Implement', pa.struct([
        pa.field('Implement_ID', pa.string()),
        pa.field('Section_Control_Status', pa.struct([
            pa.field('Section1', pa.string()),
            pa.field('Section2', pa.string()),
            pa.field('Section3', pa.string())
        ])),
        pa.field('Flow_Rate_L_min', pa.float64()),
        pa.field('Seed_Rate_seeds_per_sq_m', pa.float64()),
        pa.field('Yield_Monitor_Data', pa.struct([
            pa.field('Yield_Moisture_Content_Percentage', pa.float64()),
            pa.field('Yield_Mass_Flow_Rate_kg_s', pa.float64()),
            pa.field('Yield_Rate_Per_Hectare_kg_ha', pa.float64())
        ])),
        pa.field('Soil_Sensor_Data', pa.struct([
            pa.field('Soil_Moisture_Percentage', pa.float64()),
            pa.field('Soil_Temperature_C', pa.float64()),
            pa.field('Soil_Nutrient_Levels', pa.struct([
                pa.field('Nitrogen_ppm', pa.int64()),
                pa.field('Phosphorus_ppm', pa.int64()),
                pa.field('Potassium_ppm', pa.int64())
            ]))
        ]))
    ]), nullable=True)
])

def load_avro_schema(schema_path):
    with open(schema_path, 'r') as f:
        return json.load(f)

def run(argv=None):
    pipeline_options = PipelineOptions(argv)
    pipeline_options.view_as(StandardOptions).streaming = True
    
    streaming_schema = load_avro_schema(STREAMING_SCHEMA_PATH)
    
    producer = Producer({'bootstrap.servers': KAFKA_BROKERS})

    with beam.Pipeline(options=pipeline_options) as p:
        records = (
            p
            | 'Read JSON' >> beam.io.ReadFromText(INPUT_PATH)
            | 'Parse JSON' >> beam.Map(json.loads)
        )

        (
            records
            | 'Extract Streaming Data' >> beam.Map(extract_streaming_fields)
            | 'Write to Avro' >> beam.io.avroio.WriteToAvro(
                file_path_prefix=STREAMING_OUTPUT_PATH,
                schema=streaming_schema,
                file_name_suffix='.avro',
                codec='snappy'
            )
        )

        (
            records
            | 'Extract Batch Data' >> beam.Map(extract_batch_fields)
            | 'Filter Null Implement' >> beam.Filter(lambda x: x.get('Implement') is not None)
            | 'Write batch to Parquet' >> beam.io.WriteToParquet(
                file_path_prefix=BATCH_OUTPUT_PATH,
                schema=batch_schema,
                file_name_suffix=".parquet"
            )
        )

    # Notificaciones a Kafka
    streaming_filename = STREAMING_OUTPUT_PATH+ "-00000-of-00001.avro"
    if os.path.exists(streaming_filename):
        kafka_notification = {
            "event": "file_generated",
            "file_path": streaming_filename,
            "generated_at": dt.now(UTC).isoformat()
        }
        send_json_to_kafka(json.dumps(kafka_notification), topic=KAFKA_STREAMING_TOPIC, producer=producer)
        producer.flush()
    else:
        print(f"Archivo {streaming_filename} no encontrado, no se envió notificación a Kafka.")


    batch_filename = BATCH_OUTPUT_PATH + "-00000-of-00001.parquet"
    if os.path.exists(batch_filename):
        kafka_notification = {
            "event": "file_generated",
            "file_path": batch_filename,
            "generated_at": dt.now(UTC).isoformat()
        }
        send_json_to_kafka(json.dumps(kafka_notification), topic=KAFKA_BATCH_TOPIC, producer=producer)
        producer.flush()
    else:
        print(f"Archivo {batch_filename} no encontrado, no se envió notificación a Kafka.")


if __name__ == '__main__':
    run()