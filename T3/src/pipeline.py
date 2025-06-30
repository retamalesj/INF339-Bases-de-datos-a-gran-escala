import apache_beam as beam
import json
import datetime

from apache_beam.options.pipeline_options import PipelineOptions

SCHEMA_PATH = 'schemas/fan_engagement.avsc'
INPUT_PATH = 'data/fan_engagement.json'
OUTPUT_PATH = 'output/fan_engagement.avro'

def load_avro_schema(schema_path):
    with open(schema_path, 'r') as f:
        return json.load(f)


def to_unix_millis(timestamp):
    # Transforma un timestamp en formato %Y-%m-%d %H:%M:%S a Unix timestamp
    dt = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    return int(dt.timestamp() * 1000)

def parse_json(line):
    try:
        record = json.loads(line)
        record['Timestamp_unix'] = to_unix_millis(record['Timestamp'])
        return record
    except Exception as e:
        print(f"Error al parsear la linea: {line}. Exception: {e}")
        return None

def run(argv=None):
    pipeline_options = PipelineOptions(argv)

    schema = load_avro_schema(SCHEMA_PATH)

    with beam.Pipeline(options=pipeline_options) as p:
        (
            p
            | 'ReadDataFromJSON' >> beam.io.ReadFromText(INPUT_PATH)
            | 'ParseJSON' >> beam.Map(parse_json)
            | 'FilterValid' >> beam.Filter(lambda x: x is not None)
            | 'WriteToAvro' >> beam.io.WriteToAvro(
                file_path_prefix=OUTPUT_PATH,
                schema=schema,
                file_name_suffix='.avro',
                codec='deflate'
            )
        )

if __name__ == '__main__':
    run()