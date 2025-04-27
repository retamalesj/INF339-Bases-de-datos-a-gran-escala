import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from decimal import Decimal
from .convert import Convert

class ConvertCsvToParquet(Convert):

    def convert(self, input_filename, output_folder, compression):
        # Get output filename
        output_path = self.get_output_filename(input_filename, output_folder, "parquet", compression)
        print(f"Converting {input_filename} to Parquet with compression {compression}")

        df = pd.read_csv(input_filename)
        
        df['UTC_Date'] = pd.to_datetime(df['UTC_Date'], format='%Y-%m-%d %H:%M:%S')
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        df['Hour'] = pd.to_datetime(df['Hour'], format='%H:%M:%S').dt.time

        columnas_decimal = ['Latitude', 'Longitude']
        for col in columnas_decimal:
            df[col] = df[col].apply(lambda x: Decimal(str(x)) if pd.notnull(x) else None)
    
        # Create schema
        schema = pa.schema([
            ('UTC_Date', pa.timestamp('s')),
            ('Profundity', pa.string()),
            ('Magnitude', pa.string()),
            ('Date', pa.date32()),
            ('Hour', pa.time32('s')),
            ('Location', pa.string()),
            ('Latitude', pa.decimal128(5,3)),
            ('Longitude', pa.decimal128(6,3))
        ])

        table = pa.Table.from_pandas(df, schema=schema, preserve_index=False)
        
        pq.write_table(table, output_path, compression=compression)


        """ # Reading CSV and converting to Parquet
        with open(input_filename, encoding='utf-8', newline='') as csvfile:
            datareader = csv.DictReader(csvfile, delimiter=',')
            #TODO: add your code here
        print(f"Parquet file created successfully at {output_path}") """

        return output_path
