import pandas as pd
import os
import numpy as np

# Este archivo genera un modelo de conduccion basado en los datos de la ruta obtenidos en route_data.py


# Directorio donde se encuentran los datos procesados
CARPETA_DATOS_RUTA = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Analisis_datos", "Processed_data"))


# Cargar el DataFrame df_route_data desde el archivo CSV
ruta_csv = os.path.join(CARPETA_DATOS_RUTA, "df_route_data.csv")
if os.path.exists(ruta_csv):
    df_route_data = pd.read_csv(ruta_csv)
    print("DataFrame df_route_data cargado correctamente:")
    print(df_route_data.head())
else:
    print(f"No se encontró el archivo CSV en la ruta: {ruta_csv}")

# Calcular la columna delta_time. Esta columna es la diferencia de tiempo entre dos puntos consecutivos
def calcular_delta_time(df):

    print("Calculando delta_time para df_route_data...")

    # Convertir tiempo a segundos
    def tiempo_a_segundos(tiempo):
        if pd.isnull(tiempo):
            return 0
        h, m, s = map(int, tiempo.split(":"))
        return h * 3600 + m * 60 + s

    # Convertir arrival_time y departure_time a segundos 
    df['arrival_time_seg'] = df['arrival_time'].apply(tiempo_a_segundos)
    df['departure_time_seg'] = df['departure_time'].apply(tiempo_a_segundos)

    df['delta_time'] = df.groupby('shape_id')['arrival_time_seg'].diff().fillna(0)

    df.drop(columns=['arrival_time_seg', 'departure_time_seg'], inplace=True)

    print("Columna delta_time calculada:")
    print(df[['shape_id', 'shape_pt_sequence', 'delta_time']].head())
    return df

if df_route_data is not None and not df_route_data.empty:
    df_route_data = calcular_delta_time(df_route_data)
    print("DataFrame df_route_data con delta_time:")
    print(df_route_data)
else:
    print("El DataFrame df_route_data está vacío. No se pudo calcular delta_time.")

# Crear la columna inst_vel e inst_acc
def generate_instantaneous_velocity(df, max_speed_mps=13.8):
    """
    Genera la velocidad instantánea (inst_vel) y la aceleración instantánea (inst_acc)
    para un viaje de autobús basadose en las paradas y en los tiempos y distancias.

    """
    # Verificar que las columnas necesarias existan
    if not all(col in df.columns for col in ['shape_dist_traveled', 'is_stop', 'delta_time']):
        raise ValueError("El DataFrame debe contener las columnas 'shape_dist_traveled', 'is_stop' y 'delta_time'.")

    # Inicializar las columnas inst_vel e inst_acc
    df['inst_vel'] = 0.0
    df['inst_acc'] = 0.0

    # Identificar los índices de las paradas
    stop_indices = df.index[df['is_stop'] == 1].tolist()

    # Si hay menos de 2 paradas, no se puede calcular el perfil de velocidad
    if len(stop_indices) < 2:
        print("Advertencia: Menos de 2 paradas encontradas. No se puede generar perfiles de velocidad entre paradas.")
        return df

    # Iterar a través de segmentos definidos por paradas consecutivas
    for i in range(len(stop_indices) - 1):
        start_stop_idx = stop_indices[i]
        end_stop_idx = stop_indices[i + 1]

        # Segmento entre las paradas
        segment_start_idx = start_stop_idx + 1
        segment_end_idx = end_stop_idx

        if segment_start_idx > segment_end_idx:
            continue
        distance_between_stops = df.loc[end_stop_idx, 'shape_dist_traveled'] - df.loc[start_stop_idx, 'shape_dist_traveled']
        segment_df = df.loc[segment_start_idx:end_stop_idx].copy()
        total_segment_time = segment_df['delta_time'].sum()

        # Manejar casos con tiempo total <= 0
        if total_segment_time <= 0:
            df.loc[segment_start_idx:end_stop_idx, ['inst_vel', 'inst_acc']] = 0.0
            continue

        # Cálculo de las inst_vel basado en las tasas de aceleración y frenado

        a_rate = 0.4   # m/s^2 (aceleración)
        b_rate = 0.4   # m/s^2 (frenado)

        # Calcular v_peak_distance basado en la distancia disponible (asumiendo solo acelerar y luego frenar)
        v_peak_distance = np.sqrt((2 * distance_between_stops) / (1 / a_rate + 1 / b_rate))

        # Si v_peak_distance es menor o igual a la velocidad máxima permitida, no hay fase de crucero
        if v_peak_distance <= max_speed_mps:
            v_peak = v_peak_distance
            t_acc = v_peak / a_rate
            t_dec = v_peak / b_rate
            t_cruise = 0.0
        else:
            # Si v_peak_distance es mayor a la velocidad máxima, calcular la fase de crucero
            v_peak = max_speed_mps
            t_acc = v_peak / a_rate
            t_dec = v_peak / b_rate
            t_cruise = total_segment_time - (t_acc + t_dec)

        # Generar el perfil de velocidad y aceleración en el segmento:
        cumulative_segment_times = segment_df['delta_time'].cumsum()
        for current_idx in segment_df.index:
            t_current = cumulative_segment_times.loc[current_idx]
            
            if t_current <= t_acc:  # Fase de aceleración
                velocity = a_rate * t_current
                acceleration = a_rate
            elif t_current <= t_acc + t_cruise:  # Fase de velocidad constante (crucero)
                velocity = v_peak
                acceleration = 0.0
            else:  # Fase de frenado
                t_decel = t_current - (t_acc + t_cruise)
                velocity = v_peak - b_rate * t_decel
                acceleration = -b_rate

            # Asegurar que la velocidad no sea negativa y no supere el máximo permitido
            df.loc[current_idx, 'inst_vel'] = min(max(0.0, velocity), max_speed_mps)
            df.loc[current_idx, 'inst_acc'] = acceleration

    # Asegurar que las paradas tengan velocidad cero
    df.loc[df['is_stop'] == 1, ['inst_vel', 'inst_acc']] = 0.0

    return df

if df_route_data is not None and not df_route_data.empty:
    df_route_data = generate_instantaneous_velocity(df_route_data)
    print("DataFrame df_route_data con inst_vel e inst_acc calculados:")
    print(df_route_data)
else:
    print("El DataFrame df_route_data está vacío. No se pudo calcular inst_vel e inst_acc.")

# Calcular la columna angle_deg
def calcular_angulo(df):
    """
    Calcula el ángulo en grados entre dos puntos consecutivos basado en la diferencia de altitudes
    y la diferencia de shape_dist_traveled, de manera independiente para cada shape_id.
    Si el ángulo calculado es mayor a 10°, se limita a 10°.

    """
    print("Calculando ángulo entre puntos consecutivos por shape_id...")

    # Verificar que las columnas necesarias existan
    if not all(col in df.columns for col in ['altitude', 'shape_dist_traveled', 'shape_id']):
        raise ValueError("El DataFrame debe contener las columnas 'altitude', 'shape_dist_traveled' y 'shape_id'.")

    # Inicializar la columna angle_deg
    df['angle_deg'] = 0.0

    # Calcular el ángulo de manera independiente para cada shape_id
    for shape_id, group in df.groupby('shape_id'):
        group = group.copy()
        group['delta_altitude'] = group['altitude'].diff().fillna(0)
        group['delta_distance'] = group['shape_dist_traveled'].diff().fillna(0)
        group['angle_deg'] = np.degrees(np.arctan2(group['delta_altitude'], group['delta_distance']))

        # Limitar el ángulo máximo a 10°
        group['angle_deg'] = group['angle_deg'].clip(upper=10)

        # Actualizar el DataFrame original con los valores calculados
        df.loc[group.index, 'angle_deg'] = group['angle_deg']

    print("Columna angle_deg calculada por shape_id (con límite de 10°):")
    print(df[['shape_id', 'shape_pt_sequence', 'angle_deg']].head())
    return df

if df_route_data is not None and not df_route_data.empty:
    df_route_data = calcular_angulo(df_route_data)
    print("DataFrame df_route_data con angle_deg calculado:")
    print(df_route_data)
else:
    print("El DataFrame df_route_data está vacío. No se pudo calcular angle_deg.")

# Exportar el DataFrame df_route_data a un archivo CSV en la carpeta Processed_data
output_csv = os.path.join(CARPETA_DATOS_RUTA, "df_driving_model.csv")
if df_route_data is not None and not df_route_data.empty:
    df_route_data.to_csv(output_csv, index=False)
    print(f"DataFrame df_route_data exportado a {output_csv}")
else:
    print("El DataFrame df_route_data está vacío. No se pudo exportar.")











