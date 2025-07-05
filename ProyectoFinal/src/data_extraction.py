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