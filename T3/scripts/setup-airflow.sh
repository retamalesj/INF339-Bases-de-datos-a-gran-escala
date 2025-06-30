#!/bin/bash

export AIRFLOW_HOME=$(pwd)/.airflow
mkdir -p $AIRFLOW_HOME

airflow db init

# Ruta dinámica de los DAGs basada en la carpeta actual
REAL_DAGS_FOLDER=$(pwd)/dags

# Cambiar la config para que apunte a tus DAGs reales
sed -i "s|^dags_folder = .*|dags_folder = $REAL_DAGS_FOLDER|" $AIRFLOW_HOME/airflow.cfg

airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@admin.com \
    --password admin

airflow scheduler &

airflow webserver