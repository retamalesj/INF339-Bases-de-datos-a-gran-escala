import csv
import fastavro
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from .convert import Convert

class ConvertCsvToAvro(Convert):

    def convert(self, input_filename, output_folder, compression):
        # Get output filename
        output_path = self.get_output_filename(input_filename, output_folder, "avro", compression)
        print(f"Converting {input_filename} to AVRO with compression {compression}")
        
        # Load avro schema
        parsed_schema = fastavro.schema.load_schema('resources/Earthquake schema.avsc')

        # Reading CSV and converting to AVRO
        with open(input_filename, encoding='utf-8', newline='') as csvfile:
            datareader = csv.DictReader(csvfile, delimiter=',')

            records = []
            for row in datareader:
                record = {
                    "UTC_Date": self.convert_utc_date(row['UTC_Date']),
                    "Profundity": row['Profundity'],
                    "Magnitude": row['Magnitude'],
                    "Date": self.convert_date(row['Date']),
                    "Hour": self.convert_hour(row['Hour']),
                    "Location": row['Location'],
                    "Latitude": self.convert_latitude(row['Latitude']),
                    "Longitude": self.convert_longitude(row['Longitude']),
                }
                records.append(record)
            
            with open(output_path, 'wb') as out_file:
                fastavro.writer(out_file, parsed_schema, records)

        print(f"AVRO file created successfully at {output_path}")
        return output_path

    def convert_utc_date(self, utc_date_str):
        dt = datetime.strptime(utc_date_str, "%Y-%m-%d %H:%M:%S")
        
        # Se utiliza timestamp-millis por lo que se convierte a milisegundos
        return int(dt.timestamp() * 1000)
    
    def convert_date(self, date_str):
        dt = datetime.strptime(date_str, "%Y-%m-%d")

        unix_epoch = datetime(1970, 1, 1)

        # Avro almacena el número de días desde el 1 de enero de 1970
        # "A date logical type annotates an Avro int, where the int
        # stores the number of days from the unix epoch, 1 January 1970
        # (ISO calendar)."
        return (dt - unix_epoch).days
    
    def convert_hour(self, hour_str):
        time = datetime.strptime(hour_str, "%H:%M:%S").time()

        # "A time-millis logical type annotates an Avro int, where
        # the int stores the number of milliseconds after
        # midnight, 00:00:00.000."
        # Por lo tanto, se debe convertir el número a milisegundos
        return (time.hour * 3600 + time.minute * 60 + time.second) * 1000

    def convert_latitude(self, latitude_str):
        # La precisión tiene 5 dígitos, y según la escala, tiene 3 decimales
        # Por lo que máximo se tiene 99.999
        return Decimal(latitude_str).quantize(Decimal('0.001'))
    
    def convert_longitude(self, longitude_str):
        # La precisión tiene 6 dígitos, y según la escala, tiene 3 decimales
        # Por lo que máximo se tiene 99.999
        return Decimal(longitude_str).quantize(Decimal('0.001'))
    