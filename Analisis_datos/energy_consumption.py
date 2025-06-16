import pandas as pd
import os
import numpy as np

# Este archivo simula el consumo de energía de un autobús eléctrico basado en el modelo de conducción de driving_model.py

# Datos de entrada del modelo
# Estos son datos relativos a las caracteristicas del bus y condiciones de la ruta
mass_bus = 14535    # Tara del bus en kg
Af = 8.68   # Superficie frontal del bus en m2
air_density = 1.2041  # Densidad aire en kg/m3
Cd = 0.65   # Coeficiente aerodinamico, es adimensional
Cr = 0.01   # Coeficiente de rozamiento, es adimensional
motor_eff = 0.95    # Eficiencia del motor
conv_eff = 0.97     # Eficiencia de conversion energia bateria-motor
reg_eff = 0.6     # Eficiencia de regeneracion de energia
Paux = 5000    # Potencia consumida por cargas auxiliares en W. Incluye aire acondicionado, luces, etc.

# Carpetas de datos
CARPETA_DATOS_PROCESADOS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Analisis_datos", "Processed_data"))
CARPETA_RESULTADOS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Analisis_datos", "results"))

ruta_csv = os.path.join(CARPETA_DATOS_PROCESADOS, "df_driving_model.csv")
ruta_csv_energy = os.path.join(CARPETA_RESULTADOS, "df_energy_consumption.csv")
ruta_csv_summary = os.path.join(CARPETA_RESULTADOS, "df_consumption_results.csv")

# Importar el DataFrame desde el archivo CSV df_driving_model
if os.path.exists(ruta_csv):
    df_energy_consumption = pd.read_csv(ruta_csv)
    print("DataFrame df_driving_model cargado correctamente:")
    print(df_energy_consumption.head())
else:
    print(f"No se encontró el archivo CSV en la ruta: {ruta_csv}")

# Calcular las fuerzas que actúan sobre el bus
def calcular_fuerzas(df):
    print("Calculando fuerzas que actúan sobre el bus...")

    # Verificar que las columnas necesarias existan
    if not all(col in df.columns for col in ['inst_vel', 'inst_acc', 'angle_deg']):
        raise ValueError("El DataFrame debe contener las columnas 'inst_vel', 'inst_acc' y 'angle_deg'.")

    # Convertir el ángulo de grados a radianes
    df['angle_rad'] = np.radians(df['angle_deg'])

    # Calcular las fuerzas
    df['F_aero'] = 0.5 * Cd * Af * air_density * df['inst_vel']**2  # Fuerza aerodinámica
    df['F_g'] = mass_bus * 9.81 * np.sin(df['angle_rad'])           # Fuerza gravitacional
    df['F_roll'] = Cr * mass_bus * 9.81 * np.cos(df['angle_rad'])   # Fuerza de rodadura
    df['F_acc'] = mass_bus * df['inst_acc']                         # Fuerza de aceleración

    # Calcular la fuerza de tracción
    df['F_trac'] = df['F_aero'] + df['F_g'] + df['F_roll'] + df['F_acc']

    # Eliminar la columna temporal 'angle_rad'
    df.drop(columns=['angle_rad'], inplace=True)

    print("Fuerzas calculadas y añadidas al DataFrame:")
    print(df[['F_aero', 'F_g', 'F_roll', 'F_acc', 'F_trac']].head())
    return df

if df_energy_consumption is not None and not df_energy_consumption.empty:
    df_energy_consumption = calcular_fuerzas(df_energy_consumption)
    print("DataFrame df_energy_consumption con fuerzas calculadas:")
    print(df_energy_consumption)
else:
    print("El DataFrame df_energy_consumption está vacío. No se pudieron calcular las fuerzas.")

# Calcular la potencia de traccion
def calcular_potencia(df):
    print("Calculando potencia de tracción (P_trac)...")

    # Verificar que las columnas necesarias existan
    if not all(col in df.columns for col in ['F_trac', 'inst_vel']):
        raise ValueError("El DataFrame debe contener las columnas 'F_trac' e 'inst_vel'.")

    # Calcular la potencia de tracción
    df['P_trac'] = df['F_trac'] * df['inst_vel']

    print("Potencia de tracción calculada y añadida al DataFrame:")
    print(df[['F_trac', 'inst_vel', 'P_trac']].head())
    return df

if df_energy_consumption is not None and not df_energy_consumption.empty:
    df_energy_consumption = calcular_potencia(df_energy_consumption)
    print("DataFrame df_energy_consumption con potencia calculada:")
    print(df_energy_consumption)
else:
    print("El DataFrame df_energy_consumption está vacío. No se pudo calcular la potencia.")

# Calcular la potencia consumida por el bus
def calcular_potencia_consumida(df):
    print("Calculando potencia consumida (P_cons)...")

    # Verificar que las columnas necesarias existan
    if not all(col in df.columns for col in ['P_trac']):
        raise ValueError("El DataFrame debe contener la columna 'P_trac'.")

    # Calcular la potencia consumida
    df['P_cons'] = np.where(
        df['P_trac'] > 0,
        (df['P_trac'] / (conv_eff * motor_eff)) + (Paux / conv_eff),  # Caso de consumo
        (df['P_trac'] * motor_eff * reg_eff) + (Paux / conv_eff)     # Caso de regeneración
    )

    print("Potencia consumida calculada y añadida al DataFrame:")
    print(df[['P_trac', 'P_cons']].head())
    return df

if df_energy_consumption is not None and not df_energy_consumption.empty:
    df_energy_consumption = calcular_potencia_consumida(df_energy_consumption)
    print("DataFrame df_energy_consumption con potencia consumida calculada:")
    print(df_energy_consumption)
else:
    print("El DataFrame df_energy_consumption está vacío. No se pudo calcular la potencia consumida.")

# Calcular la energía consumida por instante
def calcular_energia_instantanea(df):
    """
    Calcula la energía consumida por instante (E_cons) y la almacena en una nueva columna.

    """
    print("Calculando energía consumida por instante (E_cons)...")

    # Verificar que las columnas necesarias existan
    if not all(col in df.columns for col in ['P_cons', 'delta_time']):
        raise ValueError("El DataFrame debe contener las columnas 'P_cons' y 'delta_time'.")

    # Calcular la energía consumida por instante (W·s)
    df['E_cons'] = df['P_cons'] * df['delta_time'] / 3600 / 1000  # Convertir a kWh

    print("Energía consumida por instante calculada y añadida al DataFrame:")
    print(df[['P_cons', 'delta_time', 'E_cons']].head())
    return df


if df_energy_consumption is not None and not df_energy_consumption.empty:
    df_energy_consumption = calcular_energia_instantanea(df_energy_consumption)
    print("DataFrame df_energy_consumption con energía instantánea calculada:")
    print(df_energy_consumption)
else:
    print("El DataFrame df_energy_consumption está vacío. No se pudo calcular la energía instantánea.")

#Creacion de un dataframe con los resultados finales de consumo de energia
def calcular_resultados_resumen(df):
    print("Calculando resultados resumen por shape_id...")

    # Verificar que las columnas necesarias existan
    if not all(col in df.columns for col in ['shape_id', 'shape_dist_traveled', 'departure_time', 'arrival_time', 'P_cons', 'E_cons']):
        raise ValueError("El DataFrame debe contener las columnas 'shape_id', 'shape_dist_traveled', 'departure_time', 'arrival_time', 'P_cons' y 'E_cons'.")

    # Convertir departure_time y arrival_time a segundos
    def tiempo_a_segundos(tiempo):
        h, m, s = map(int, tiempo.split(":"))
        return h * 3600 + m * 60 + s

    df['departure_time_seg'] = df['departure_time'].apply(tiempo_a_segundos)
    df['arrival_time_seg'] = df['arrival_time'].apply(tiempo_a_segundos)

    # Calcular los resultados agregados por shape_id
    resumen = df.groupby('shape_id').agg(
        tot_dist_traveled=('shape_dist_traveled', 'max'),    # Distancia total recorrida
        tot_time_traveled=('arrival_time_seg', 'max'),       # Último arrival_time en segundos
        first_departure_time=('departure_time_seg', 'min'),  # Primer departure_time en segundos
        tot_P_cons=('P_cons', 'sum'),                        # Potencia total consumida
        tot_E_cons=('E_cons', 'sum')                         # Energía total consumida en kWh
    ).reset_index()

    # Calcular el tiempo total recorrido como la diferencia entre el último arrival_time y el primer departure_time
    resumen['tot_time_traveled'] = resumen['tot_time_traveled'] - resumen['first_departure_time']

    # Calcular los kWh consumidos por kilómetro
    resumen['E_cons_km'] = resumen['tot_E_cons'] / (resumen['tot_dist_traveled'] / 1000)  # Convertir metros a kilómetros

    # Eliminar la columna temporal 
    resumen.drop(columns=['first_departure_time'], inplace=True)

    print("Resultados resumen calculados:")
    print(resumen)
    return resumen

if df_energy_consumption is not None and not df_energy_consumption.empty:
    df_consumption_results = calcular_resultados_resumen(df_energy_consumption)
    print("DataFrame df_consumption_results creado con éxito:")
    print(df_consumption_results)
else:
    print("El DataFrame df_energy_consumption está vacío. No se pudo calcular el resumen de consumo.")

# Exportar los DataFrames a archivos CSV
if not os.path.exists(CARPETA_RESULTADOS):
    os.makedirs(CARPETA_RESULTADOS)

if df_energy_consumption is not None and not df_energy_consumption.empty:
    df_energy_consumption.to_csv(ruta_csv_energy, index=False)
    print(f"DataFrame df_energy_consumption exportado a {ruta_csv_energy}")
else:
    print("El DataFrame df_energy_consumption está vacío. No se pudo exportar.")

if df_consumption_results is not None and not df_consumption_results.empty:
    df_consumption_results.to_csv(ruta_csv_summary, index=False)
    print(f"DataFrame df_consumption_results exportado a {ruta_csv_summary}")
else:
    print("El DataFrame df_consumption_results está vacío. No se pudo exportar.")
