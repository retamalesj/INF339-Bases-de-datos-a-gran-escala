from src.pipeline import run as run_beam_pipeline

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import json

from kafka import KafkaProducer

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.combine(datetime.today() - timedelta(days=1), datetime.min.time()),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

DAG_NAME = 'fan_engagement_etl'
INPUT_PATH = 'data/fan_engagement.json'
OUTPUT_PATH = 'output/fan_engagement.avro'
KAFKA_TOPIC = 'data_notifications'
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']

def notify_kafka():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    message = {
        "event_type": "data_processing_completed",
        "data_entity": "FanEngagement",
        "status": "success",
        "location": OUTPUT_PATH,
        "processed_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "source_system": DAG_NAME
    }
    
    producer.send(KAFKA_TOPIC, message)
    producer.flush()

with DAG(
    DAG_NAME,
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
) as dag:

    etl_task = PythonOperator(
        task_id='run_beam_etl',
        python_callable=run_beam_pipeline
    )

    notify_task = PythonOperator(
        task_id='notify_kafka',
        python_callable=notify_kafka
    )

    etl_task >> notify_task