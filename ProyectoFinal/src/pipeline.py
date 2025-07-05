import os
import apache_beam as beam
import json
import pyarrow as pa
from datetime import datetime as dt, UTC

from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from confluent_kafka import Producer
from random_data_generator import send_json_to_kafka

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

def normalize_diagnostic_data(data):
    if not data:
        return None

    return {
        "Error_Code": data.get("Error_Code"),

        "Warning_Lights": {
            "CheckEngineLight": data.get("Warning_Lights", {}).get("CheckEngineLight", ""),
            "LowOilPressure": data.get("Warning_Lights", {}).get("LowOilPressure", "")
        },

        "Component Temperatures_C": {
            "Engine": int(data.get("Component Temperatures_C", {}).get("Engine", 0)),
            "Transmission": int(data.get("Component Temperatures_C", {}).get("Transmission", 0)),
            "HydraulicSystem": int(data.get("Component Temperatures_C", {}).get("HydraulicSystem", 0))
        },

        "Vibration": {
            "Vibration_Index_X": float(data.get("Vibration", {}).get("Vibration_Index_X", 0.0)),
            "Vibration_Index_Y": float(data.get("Vibration", {}).get("Vibration_Index_Y", 0.0)),
            "Vibration_Index_Z": float(data.get("Vibration", {}).get("Vibration_Index_Z", 0.0))
        },

        "Component_Wear_Indicators": {
            k: float(v) for k, v in data.get("Component_Wear_Indicators", {}).items()
        }
    }

def extract_streaming_fields(record):
    gps_data = record.get("GPS_Coordinates", {})
    
    return {
        "Vehicle_ID": record.get("Vehicle_ID"),
        "Timestamp": record.get("Timestamp"),
        "GPS_Coordinates": {
            "Latitude": gps_data.get("Latitude"),
            "Longitude": gps_data.get("Longitude")
        },
        "Engine_RPM": record.get("Engine_RPM"),
        "Engine_Load_Percentage": record.get("Engine_Load_Percentage"),
        "Fuel_Level_Percentage": record.get("Fuel_Level_Percentage"),
        "Fuel_Consumption_Rate_L_hr": record.get("Fuel_Consumption_Rate_L_hr"),
        "Speed_km_h": record.get("Speed_km_h"),
        "Odometer_km": record.get("Odometer_km"),
        "Operating_Hours": record.get("Operating_Hours"),
        "Hydraulic_Pressure_psi": record.get("Hydraulic_Pressure_psi"),
        "Hydraulic_Fluid_Temp_C": record.get("Hydraulic_Fluid_Temp_C"),
        "Engine_Coolant_Temp_C": record.get("Engine_Coolant_Temp_C"),
        "Battery_Voltage_V": record.get("Battery_Voltage_V"),
        "Gear_Engaged": record.get("Gear_Engaged"),
        "Accelerator_Pedal_Position_Percentage": record.get("Accelerator_Pedal_Position_Percentage"),
        "Brake_Pedal_Position_Percentage": record.get("Brake_Pedal_Position_Percentage"),
        "Diagnostic_Data": normalize_diagnostic_data(record.get("Diagnostic_Data"))
    }

def extract_batch_fields(record):
    implement = record.get("Implement")
    if implement is None:
        return {"Implement": None}
    
    yield_monitor = implement.get("Yield_Monitor_Data", {})
    soil_sensor = implement.get("Soil_Sensor_Data", {})

    return {
        "Implement": {
            "Implement_ID": implement.get("Implement_ID"),
            "Section_Control_Status": implement.get("Section_Control_Status"),
            "Flow_Rate_L_min": implement.get("Flow_Rate_L_min"),
            "Seed_Rate_seeds_per_sq_m": implement.get("Seed_Rate_seeds_per_sq_m"),
            "Yield_Monitor_Data": {
                "Yield_Moisture_Content_Percentage": yield_monitor.get("Yield_Moisture_Content_Percentage"),
                "Yield_Mass_Flow_Rate_kg_s": yield_monitor.get("Yield_Mass_Flow_Rate_kg_s"),
                "Yield_Rate_Per_Hectare_kg_ha": yield_monitor.get("Yield_Rate_Per_Hectare_kg_ha")
            },
            "Soil_Sensor_Data": {
                "Soil_Moisture_Percentage": soil_sensor.get("Soil_Moisture_Percentage"),
                "Soil_Temperature_C": soil_sensor.get("Soil_Temperature_C"),
                "Soil_Nutrient_Levels": soil_sensor.get("Soil_Nutrient_Levels")
            }
        }
    }

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
            | 'Write batch to Parquet' >> beam.io.WriteToParquet(
                file_path_prefix=BATCH_OUTPUT_PATH,
                schema=batch_schema,
                file_name_suffix=".parquet"
            )
        )

    filename = STREAMING_OUTPUT_PATH+ "-00000-of-00001.avro"
    if os.path.exists(filename):
        kafka_notification = {
            "event": "file_generated",
            "file_path": filename,
            "generated_at": dt.now(UTC).isoformat()
        }
        send_json_to_kafka(json.dumps(kafka_notification), topic=KAFKA_STREAMING_TOPIC, producer=producer)
        producer.flush()
    else:
        print(f"Archivo {STREAMING_OUTPUT_PATH} no encontrado, no se envió notificación a Kafka.")

if __name__ == '__main__':
    run()