import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Definir carpeta usando os.path.abspath
CARPETA_DATOS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Analisis_datos", "Raw_data"))

if not os.path.exists(CARPETA_DATOS):
    raise FileNotFoundError(f"La carpeta especificada no existe: {CARPETA_DATOS}")

print(f"Leyendo archivos GTFS desde la carpeta: {CARPETA_DATOS}")
archivos_en_carpeta = os.listdir(CARPETA_DATOS)
print(f"Archivos encontrados en la carpeta: {archivos_en_carpeta}")

#Se crea un diccionario con toda la informacion de los datos
datos_dict = {}

def cargar_datos():
    archivos_esperados = [
        "agency.txt", 
        "calendar.txt", 
        "calendar_dates.txt", 
        "frequencies.txt", 
        "routes.txt", 
        "shapes.txt", 
        "stop_times.txt", 
        "stops.txt", 
        "trips.txt"
    ]

    for archivo in archivos_esperados:
        ruta = os.path.join(CARPETA_DATOS, archivo)
        if os.path.exists(ruta):
            print(f"Intentando cargar: {archivo} desde {ruta}")
            try:
                datos_dict[archivo.replace(".txt", "")] = pd.read_csv(ruta, sep=",")  # Cambia sep si es necesario
                print(f"Archivo cargado: {archivo} con {datos_dict[archivo.replace('.txt', '')].shape[0]} filas")
            except pd.errors.EmptyDataError:
                print(f"Error: El archivo {archivo} está vacío.")
            except pd.errors.ParserError as e:
                print(f"Error de formato en {archivo}: {e}")
            except Exception as e:
                print(f"Error inesperado en {archivo}: {e}")
        else:
            print(f"Archivo no encontrado: {archivo}")

    if not datos_dict:
        print("El diccionario 'datos_dict' está vacío. Verifica los archivos en la carpeta especificada.")
    else:
        print(f"Archivos cargados exitosamente: {list(datos_dict.keys())}")

cargar_datos()

# Calcular la ruta con el shape_id de mayor distancia recorrida
shapes = datos_dict["shapes"]
if shapes.empty:
    print("El archivo shapes.txt está vacío o no se cargó correctamente.")
else:
    print("Calculando la ruta con el shape_id de mayor distancia recorrida...")
    shapes['distance'] = shapes.groupby('shape_id')['shape_dist_traveled'].transform('max')
    shape_max_distance = shapes.loc[shapes['distance'].idxmax()]
    print(f"Shape ID con mayor distancia recorrida: {shape_max_distance['shape_id']} con {shape_max_distance['distance']} unidades de distancia.")

# Calcular la ruta con el mayor número de trips (contando ambos sentidos)
trips = datos_dict["trips"]
if trips.empty:
    print("El archivo trips.txt está vacío o no se cargó correctamente.")
else:
    print("Calculando la ruta con el mayor número de trips...")
    trips_count = trips.groupby('route_id')['trip_id'].count().reset_index(name='num_trips')
    route_max_trips = trips_count.loc[trips_count['num_trips'].idxmax()]
    print(f"Route ID con mayor número de trips: {route_max_trips['route_id']} con {route_max_trips['num_trips']} trips.")

# Calcular la ruta con el mayor número de paradas
stop_times = datos_dict["stop_times"]
if stop_times.empty:
    print("El archivo stop_times.txt está vacío o no se cargó correctamente.")
else:
    print("Calculando la ruta con el mayor número de paradas...")
    stops_count = stop_times.merge(trips, on="trip_id").groupby('route_id')['stop_id'].nunique().reset_index(name='num_stops')
    route_max_stops = stops_count.loc[stops_count['num_stops'].idxmax()]
    print(f"Route ID con mayor número de paradas: {route_max_stops['route_id']} con {route_max_stops['num_stops']} paradas.")

# Mostrar todas las route_id disponibles
routes = datos_dict["routes"]
if routes.empty:
    print("El archivo routes.txt está vacío o no se cargó correctamente.")
else:
    print("Route IDs disponibles:")
    print(routes["route_id"].unique())

# Seleccionar las rutas a analizar
rutas_seleccionadas = input("Introduce las route_id seleccionadas separadas por comas: ")
rutas_seleccionadas = [int(ruta.strip()) for ruta in rutas_seleccionadas.split(",")]

# Filtrar las rutas seleccionadas
routes_filtradas = routes[routes["route_id"].isin(rutas_seleccionadas)]
if routes_filtradas.empty:
    print("No se encontraron rutas con los IDs seleccionados.")
else:
    print(f"Rutas seleccionadas: {routes_filtradas.shape[0]} filas.")
    print(routes_filtradas)

# Extraer los trips y shapes correspondientes a las rutas seleccionadas
trips = datos_dict["trips"]
stop_times = datos_dict["stop_times"]

trips_filtrados = trips[trips["route_id"].isin(rutas_seleccionadas)]
if trips_filtrados.empty:
    print("No se encontraron trips para las rutas seleccionadas.")
else:
    print(f"Trips encontrados: {trips_filtrados.shape[0]} filas.")

# Obtener la hora de inicio y final de cada trip desde stop_times
stop_times_filtrados = stop_times[stop_times["trip_id"].isin(trips_filtrados["trip_id"])]
horarios_trips = stop_times_filtrados.groupby("trip_id").agg(
    hora_inicio=("departure_time", "min"),
    hora_final=("arrival_time", "max")
).reset_index()

# Combinar la información de trips, shapes y horarios
df_gtfs_routes = trips_filtrados.merge(horarios_trips, on="trip_id", how="left")

if df_gtfs_routes.empty:
    print("El DataFrame df_gtfs_routes está vacío después del merge.")
else:
    print(f"DataFrame df_gtfs_routes creado con éxito: {df_gtfs_routes.shape[0]} filas.")
    print(df_gtfs_routes.head())

# Crear un DataFrame con información resumida por service_id y shape_id
def calcular_resumen_service_shape(df):
    """
    Calcula un resumen con el número total de trips por service_id y shape_id,
    la duración media de los trayectos por service_id, un trip_id de ejemplo,
    el trip_headsign, el número de paradas y la distancia total recorrida.

    Args:
        df (pd.DataFrame): DataFrame con las columnas necesarias para el cálculo.

    Returns:
        pd.DataFrame: DataFrame con las columnas 'service_id', 'shape_id', 'num_trips',
                      'avg_trip_duration', 'example_trip_id', 'trip_headsign',
                      'num_stops', y 'total_distance'.
    """
    print("Calculando resumen por service_id y shape_id...")

    # Verificar que las columnas necesarias existan
    required_columns = ['service_id', 'shape_id', 'hora_inicio', 'hora_final', 'trip_id', 'trip_headsign']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"El DataFrame debe contener las columnas {required_columns}.")

    # Convertir hora_inicio y hora_final a formato datetime si no lo están
    df['hora_inicio'] = pd.to_datetime(df['hora_inicio'], format="%H:%M:%S", errors="coerce")
    df['hora_final'] = pd.to_datetime(df['hora_final'], format="%H:%M:%S", errors="coerce")

    # Calcular la duración de cada trip en segundos
    df['trip_duration'] = (df['hora_final'] - df['hora_inicio']).dt.total_seconds()

    # Calcular el número de paradas por trip
    stop_times = datos_dict["stop_times"]
    stops_per_trip = stop_times.groupby('trip_id')['stop_id'].nunique().reset_index(name='num_stops')
    df = df.merge(stops_per_trip, on='trip_id', how='left')

    # Calcular la distancia total recorrida por trip
    shapes = datos_dict["shapes"]
    distances_per_trip = shapes.groupby('shape_id')['shape_dist_traveled'].max().reset_index(name='total_distance')
    df = df.merge(distances_per_trip, on='shape_id', how='left')

    # Agrupar por service_id y shape_id para calcular el resumen
    resumen = df.groupby(['service_id', 'shape_id']).agg(
        num_trips=('trip_id', 'count'),  # Número total de trips
        avg_trip_duration=('trip_duration', 'mean'),  # Duración media de los trayectos en segundos
        example_trip_id=('trip_id', 'first'),  # Un trip_id de ejemplo
        trip_headsign=('trip_headsign', 'first'),  # Un trip_headsign de ejemplo
        num_stops=('num_stops', 'mean'),  # Número promedio de paradas
        total_distance=('total_distance', 'mean')  # Distancia total promedio
    ).reset_index()

    # Convertir la duración media de segundos a minutos
    resumen['avg_trip_duration'] = resumen['avg_trip_duration'] / 60  # Convertir a minutos

    print("Resumen calculado:")
    print(resumen)
    return resumen

# Calcular el DataFrame resumen de service_id y shape_id
if df_gtfs_routes is not None and not df_gtfs_routes.empty:
    # Guardar el DataFrame df_gtfs_routes como un archivo CSV en la carpeta Raw_data
    ruta_csv_gtfs_routes = os.path.join(CARPETA_DATOS, "df_gtfs_routes.csv")
    df_gtfs_routes.to_csv(ruta_csv_gtfs_routes, index=False)
    print(f"DataFrame df_gtfs_routes guardado en: {ruta_csv_gtfs_routes}")

    # Calcular el DataFrame resumen de service_id y shape_id
    df_service_shape_summary = calcular_resumen_service_shape(df_gtfs_routes)
    print("DataFrame df_service_shape_summary creado con éxito:")
    print(df_service_shape_summary)
    
    # Guardar el DataFrame df_service_shape_summary como un archivo CSV en la carpeta Raw_data
    ruta_csv_service_shape_summary = os.path.join(CARPETA_DATOS, "df_service_shape_summary.csv")
    df_service_shape_summary.to_csv(ruta_csv_service_shape_summary, index=False)
    print(f"Resumen guardado en: {ruta_csv_service_shape_summary}")
else:
    print("El DataFrame df_gtfs_routes está vacío. No se pudo calcular el resumen.")












