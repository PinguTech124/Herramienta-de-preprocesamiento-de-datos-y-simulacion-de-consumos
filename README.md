# Herramienta-de-preprocesamiento-de-datos-y-simulacion-de-consumos

📂 Estructura de Carpetas

├── Analisis_datos/
|
│   ├── Raw_data/         # <-- Coloca aquí tus archivos GTFS (.txt)
|
│   ├── Processed_data/   # <-- Los scripts guardarán aquí datos procesados
|
│   └── results/          # <-- Los scripts guardarán aquí resultados finales

🚀 Ejecución

Paso 1: Preparar los Datos GTFS
Copia todos los archivos .txt de tu conjunto de datos GTFS en la carpeta Analisis_datos/Raw_data/.

(Opcional): Puedes usar el script gtfs.py para hacer un análisis exploratorio de los datos, como ver las rutas con más viajes o más paradas. 

Paso 2: Configurar y Generar los Datos de Ruta
Este script construye el perfil detallado de las rutas seleccionadas, incluyendo coordenadas, paradas, tiempos y altitud.

Edita el archivo route_data.py:
Localiza las listas shape_ids_seleccionados y trip_ids_seleccionados.
Modifícalas para incluir los identificadores de las rutas y viajes que deseas analizar. Es importante que selecciones un trip_id representativo por cada shape_id.

Paso 3: Generar el Modelo de Conducción
Este script utiliza los datos de la ruta para simular un perfil de velocidad y aceleración del autobús entre paradas.

Ejecuta el script: python driving_model.py

El script leerá df_route_data.csv y creará df_driving_model.csv en Analisis_datos/Processed_data/.

Paso 4: Calcular el Consumo Energético
Basándose en el modelo de conducción y las características físicas del bus (masa, eficiencia, etc.), este script calcula las fuerzas que actúan sobre el vehículo y la energía que consume.

Ejecuta el script: python energy_consumption.py

El script leerá df_driving_model.csv y generará dos archivos en la carpeta Analisis_datos/results/: 
df_energy_consumption.csv: Datos de consumo a cada instante.
df_consumption_results.csv: Un resumen con el consumo total por ruta.

📊 Visualización de Resultados

Para generar un conjunto de gráficas estáticas (.jpg) que visualicen los perfiles de velocidad, aceleración, altitud y consumo de energía, ejecuta el siguiente script. Este paso debe realizarse después de haber completado la ejecución hasta el Paso 4.

Ejecuta el script: python plots_generator.py

Las gráficas se guardarán en varias subcarpetas (Graficas, Graficas_Rutas, etc.) dentro de Analisis_datos/Processed_data/.
