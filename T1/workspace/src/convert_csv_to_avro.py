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
            #TODO: add your code here
        print(f"AVRO file created successfully at {output_path}")
        return output_path
            