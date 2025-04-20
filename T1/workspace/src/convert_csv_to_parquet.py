import csv
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime
from decimal import Decimal
from .convert import Convert

class ConvertCsvToParquet(Convert):

    def convert(self, input_filename, output_folder, compression):
        # Get output filename
        output_path = self.get_output_filename(input_filename, output_folder, "parquet", compression)
        print(f"Converting {input_filename} to Parquet with compression {compression}")

        # Create schema
        pa.schema([
            #TODO: add your schema definition here
        ])

        # Reading CSV and converting to Parquet
        with open(input_filename, encoding='utf-8', newline='') as csvfile:
            datareader = csv.DictReader(csvfile, delimiter=',')
            #TODO: add your code here
        print(f"Parquet file created successfully at {output_path}")
        return output_path
