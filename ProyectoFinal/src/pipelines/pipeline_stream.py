import os
import apache_beam as beam
import json
from datetime import datetime as dt

from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions

STREAMING_SCHEMA_PATH = 'resources/VehicleTelemetry.avsc' # Para data de streaming
INPUT_PATH = 'output.json'
STREAMING_OUTPUT_PATH = os.path.join('output/streaming', f"vehicletelemetry_{dt.now().strftime("%Y%m%dT%H%M%S")}.avro")

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
    return {
        "Implement_ID": record.get("Implement_ID"),
        "Section_Control_Status": record.get("Section_Control_Status"),
        "Flow_Rate": record.get("Flow_Rate"),
        "Application_Rate": record.get("Application_Rate"),
        "Seed_Rate": record.get("Seed_Rate"),
        "Yield_Moisture_Content": record.get("Yield_Moisture_Content"),
        "Yield_Mass_Flow": record.get("Yield_Mass_Flow"),
        "Yield_Rate_Per_Hectare": record.get("Yield_Rate_Per_Hectare"),
        "Soil_Moisture_Percentage": record.get("Soil_Moisture_Percentage"),
        "Soil_Temperature_Celsius": record.get("Soil_Temperature_Celsius"),
        "Soil_EC": record.get("Soil_EC"),
        "Soil_Nutrients": record.get("Soil_Nutrients")
    }

def run(argv=None):
    pipeline_options = PipelineOptions(argv)
    pipeline_options.view_as(StandardOptions).streaming = True
    
    streaming_schema = load_avro_schema(STREAMING_SCHEMA_PATH)

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
                codec='null'
            )
        )

        # batch = (
        #     records
        #     | 'Extract Batch Data' >> beam.Map(extract_batch_fields)
        #     | 'Write batch to JSON' >> beam.io.WriteToText('output/batch/sensor_data.json')
        # )

if __name__ == '__main__':
    run()