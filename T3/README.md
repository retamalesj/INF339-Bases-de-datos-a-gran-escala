# INF 339: Tarea 3 - Bases de datos a gran escala 
## Integrantes
    - Pablo Retamales Jara      ROL: 202173650-6
    - Juan Alegría Vasquez      ROL: 202023510-4

## Instrucciones de ejecución

    (1) Primero, debe tener Docker encendido, y ubicarse en la raíz del proyecto.
    De esta manera, Visual Studio Code es capaz de reconocer su archivo devcontainer.json,
    con el que levantará los contenedores necesarios.

    (2) Ahora, ubicado en la raíz del proyecto puede clickear Dev Container: Reopen in Container (o al menos nosotros lo hacemos así con la extensión de Dev Containers), también si no sale esta opción puede clickear Fn + F1, donde puede escribir ">Dev Containers: Reopen in Container" (debe tener la extensión).

    (3) Luego de la interminable espera, se descargará todas las dependencias declaradas en requirements.txt, proceso que ocurre automático al usar Dev Containers.
    Cuando termine el proceso, se muestra un mensaje "Done. Press any key to close the terminal.", por lo que debes presionar cualquier tecla para salir.

    (4) Ahora, para ejecutar todo, debe ubicarse en la raíz del proyecto: vscode ➜ /workspaces/inf339t3
    Donde ejecutará:
        ./scripts/load-airflow.sh
    
    Recordarle que debe estar en la carpeta raíz, ya que si ejecuta './load-airflow.sh' no funcionará, pues dentro se define una carpeta .airflow, la cual debe coincidir con la ejecución a nivel raíz.

    (5) Cuando en la terminal salga 'standalone | Airflow is ready', significa que está listo, puede abrir la interfaz de Airflow en la web, escribiendo 'http://localhost:8080',
    Sus credenciales para ingresar son:
        Username: admin
        Password: admin

    Ahí puede ubicar el Dag de nombre 'fan_engagement_etl'.

## ¿Qué hace 'load-airflow.sh'?
    Este script crea una carpeta de Airflow con la configuración y anexa la carpeta de DAGs (/dags) del proyecto. También crea un usuario 'admin' de contraseña 'admin' y abre automáticamente Airflow. Luego, puede abrir la interfaz de Airflow en la web, escribiendo 'http://localhost:8080'

    (!) Puede que ejecutar el script pedirá permisos, CREO que usar 'bash ./scripts/load-airflow.sh' no los requerirá.
    
