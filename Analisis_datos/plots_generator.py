import os
import pandas as pd
import matplotlib.pyplot as plt

# Definir carpetas usando os.path.abspath
CARPETA_DATOS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Analisis_datos", "Processed_data"))
CARPETA_RESULTADOS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Analisis_datos", "results"))

# Directorio donde se encuentra el archivo df_driving_model.csv
# CARPETA_DATOS = r"C:\Users\JaimeCartonPerea\Documents\Development\python\tfg\Analisis_datos\Processed_data"

# Cargar el DataFrame df_driving_model desde el archivo CSV
ruta_csv = os.path.join(CARPETA_DATOS, "df_driving_model.csv")
if os.path.exists(ruta_csv):
    df_driving_model = pd.read_csv(ruta_csv)
    print("DataFrame df_driving_model cargado correctamente:")
    print(df_driving_model.head())
else:
    print(f"No se encontró el archivo CSV en la ruta: {ruta_csv}")
    df_driving_model = None

# Generar gráficas agrupadas para cada shape_id
if df_driving_model is not None and not df_driving_model.empty:
    # Crear carpeta para guardar las gráficas
    CARPETA_GRAFICAS = os.path.join(CARPETA_DATOS, "Graficas")
    os.makedirs(CARPETA_GRAFICAS, exist_ok=True)

    # Iterar por cada shape_id único
    for shape_id, group in df_driving_model.groupby("shape_id"):
        # Crear una figura con dos subgráficas (una al lado de la otra)
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))

        # Gráfica de inst_vel vs. shape_dist_traveled
        axes[0].plot(group["shape_dist_traveled"], group["inst_vel"], color="blue")
        axes[0].set_xlabel("Distancia Recorrida (m)")
        axes[0].set_ylabel("Velocidad Instantánea (m/s)")
        axes[0].grid(True)

        # Gráfica de inst_acc vs. shape_dist_traveled
        axes[1].plot(group["shape_dist_traveled"], group["inst_acc"], color="green")
        axes[1].set_xlabel("Distancia Recorrida (m)")
        axes[1].set_ylabel("Aceleración Instantánea (m/s²)")
        axes[1].grid(True)

        # Guardar la figura como un archivo JPG
        ruta_grafica = os.path.join(CARPETA_GRAFICAS, f"shape_{shape_id}.jpg")
        plt.savefig(ruta_grafica, format="jpg", dpi=300)
        plt.close()
        print(f"Gráfica guardada: {ruta_grafica}")
else:
    print("El DataFrame df_driving_model está vacío. No se generaron gráficas.")

# Generar gráficas agrupadas por ruta
if df_driving_model is not None and not df_driving_model.empty:
    # Crear carpeta para guardar las gráficas agrupadas por ruta
    CARPETA_GRAFICAS_RUTAS = os.path.join(CARPETA_DATOS, "Graficas_Rutas")
    os.makedirs(CARPETA_GRAFICAS_RUTAS, exist_ok=True)

    # Extraer el identificador de ruta (sin la letra final A/B)
    df_driving_model["route_id"] = df_driving_model["shape_id"].str[:-1]

    # Iterar por cada route_id único
    for route_id, group in df_driving_model.groupby("route_id"):
        # Crear una figura con cuatro subgráficas (dos por cada sentido A y B)
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        for i, suffix in enumerate(["A", "B"]):
            shape_id = f"{route_id}{suffix}"
            shape_group = group[group["shape_id"] == shape_id]

            if not shape_group.empty:
                sentido = f"Sentido {suffix}"  # Determinar el sentido (A o B)

                # Gráfica de inst_vel vs. shape_dist_traveled
                axes[i, 0].plot(shape_group["shape_dist_traveled"], shape_group["inst_vel"], color="blue")
                axes[i, 0].set_xlabel("Distancia Recorrida (m)")
                axes[i, 0].set_ylabel("Velocidad Instantánea (m/s)")
                axes[i, 0].grid(True)
                axes[i, 0].set_title(f"Velocidad Instantánea ({sentido})")

                # Gráfica de inst_acc vs. shape_dist_traveled
                axes[i, 1].plot(shape_group["shape_dist_traveled"], shape_group["inst_acc"], color="green")
                axes[i, 1].set_xlabel("Distancia Recorrida (m)")
                axes[i, 1].set_ylabel("Aceleración Instantánea (m/s²)")
                axes[i, 1].grid(True)
                axes[i, 1].set_title(f"Aceleración Instantánea ({sentido})")
            else:
                # Si no hay datos para el shape_id, dejar las subgráficas vacías
                axes[i, 0].set_visible(False)
                axes[i, 1].set_visible(False)

        # Ajustar diseño y guardar la figura como un archivo JPG
        plt.tight_layout()
        ruta_grafica_ruta = os.path.join(CARPETA_GRAFICAS_RUTAS, f"route_{route_id}.jpg")
        plt.savefig(ruta_grafica_ruta, format="jpg", dpi=300)
        plt.close()
        print(f"Gráfica agrupada guardada: {ruta_grafica_ruta}")
else:
    print("El DataFrame df_driving_model está vacío. No se generaron gráficas agrupadas por ruta.")

# Generar gráficas agrupadas por ruta para el consumo de energía
# CARPETA_RESULTADOS = r"C:\Users\JaimeCartonPerea\Documents\Development\python\tfg\Analisis_datos\results"
ruta_csv_energy = os.path.join(CARPETA_RESULTADOS, "df_energy_consumption.csv")

if os.path.exists(ruta_csv_energy):
    df_energy = pd.read_csv(ruta_csv_energy)
    print("DataFrame df_energy_consumption cargado correctamente para gráficas de consumo.")
    # Extraer el identificador de ruta (sin la letra final A/B)
    df_energy["route_id"] = df_energy["shape_id"].str[:-1]

    # Crear carpeta para guardar las gráficas agrupadas por ruta de consumo de energía
    CARPETA_GRAFICAS_CONSUMO = os.path.join(CARPETA_DATOS, "Graficas_Consumo")
    os.makedirs(CARPETA_GRAFICAS_CONSUMO, exist_ok=True)

    # --- Gráficas de potencia consumida ---
    for route_id, group in df_energy.groupby("route_id"):
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        for i, suffix in enumerate(["A", "B"]):
            shape_id = f"{route_id}{suffix}"
            shape_group = group[group["shape_id"] == shape_id]
            if not shape_group.empty:
                sentido = f"Sentido {suffix}"
                axes[i].plot(shape_group["shape_dist_traveled"], shape_group["P_cons"] / 1000, color="red")
                axes[i].set_xlabel("Distancia Recorrida (m)")
                axes[i].set_ylabel("Potencia Consumida (kW)")
                axes[i].grid(True)
                axes[i].set_title(f"Potencia Consumida ({sentido})")
            else:
                axes[i].set_visible(False)
        plt.tight_layout()
        ruta_grafica_consumo = os.path.join(CARPETA_GRAFICAS_CONSUMO, f"potencia_route_{route_id}.jpg")
        plt.savefig(ruta_grafica_consumo, format="jpg", dpi=300)
        plt.close()
        print(f"Gráfica de potencia consumida guardada: {ruta_grafica_consumo}")

    # --- Gráficas de energía acumulada ---
    for route_id, group in df_energy.groupby("route_id"):
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        for i, suffix in enumerate(["A", "B"]):
            shape_id = f"{route_id}{suffix}"
            shape_group = group[group["shape_id"] == shape_id]
            if not shape_group.empty:
                sentido = f"Sentido {suffix}"
                # Energía acumululada en kWh
                energia_acumulada = shape_group["E_cons"].cumsum()
                axes[i].plot(shape_group["shape_dist_traveled"], energia_acumulada, color="purple")
                axes[i].set_xlabel("Distancia Recorrida (m)")
                axes[i].set_ylabel("Energía Acumulada (kWh)")
                axes[i].grid(True)
                axes[i].set_title(f"Energía Acumulada ({sentido})")
            else:
                axes[i].set_visible(False)
        plt.tight_layout()
        ruta_grafica_energia = os.path.join(CARPETA_GRAFICAS_CONSUMO, f"energia_acumulada_route_{route_id}.jpg")
        plt.savefig(ruta_grafica_energia, format="jpg", dpi=300)
        plt.close()
        print(f"Gráfica de energía acumulada guardada: {ruta_grafica_energia}")

    # --- Gráfico circular del peso de cada fuerza por ruta (ambos sentidos en una imagen) ---
    fuerzas = ['F_aero', 'F_g', 'F_roll', 'F_acc']
    etiquetas = ["Aerodinámica", "Gravedad", "Rodadura", "Aceleración"]
    colores = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

    if all(f in df_energy.columns for f in fuerzas):
        for route_id, group in df_energy.groupby("route_id"):
            fig, axes = plt.subplots(1, 2, figsize=(16, 8))
            for i, suffix in enumerate(["A", "B"]):
                shape_id = f"{route_id}{suffix}"
                shape_group = group[group["shape_id"] == shape_id]
                if not shape_group.empty:
                    pesos = [shape_group[f].abs().sum() for f in fuerzas]
                    wedges, texts, autotexts = axes[i].pie(
                        pesos, labels=None, autopct='%1.1f%%', colors=colores, startangle=90
                    )
                    axes[i].set_title(f"Peso relativo de cada fuerza\n{shape_id} (Sentido {suffix})")
                else:
                    axes[i].axis('off')
            # Leyenda común a la derecha
            fig.legend(etiquetas, title="Fuerzas", loc="center left", bbox_to_anchor=(1, 0.5))
            plt.tight_layout()
            ruta_grafico_quesito = os.path.join(
                CARPETA_GRAFICAS_CONSUMO, f"fuerzas_peso_relativo_pie_{route_id}.jpg"
            )
            plt.savefig(ruta_grafico_quesito, format="jpg", dpi=300, bbox_inches="tight")
            plt.close()
            print(f"Gráfico circular de fuerzas (ambos sentidos) guardado: {ruta_grafico_quesito}")
    else:
        print("No se encontraron todas las columnas de fuerzas necesarias para el gráfico circular.")

    # --- Diagrama de barras: porcentaje de energía recuperada por frenada regenerativa por ruta y sentido ---
    if "P_trac" in df_energy.columns and "E_cons" in df_energy.columns and "route_id" in df_energy.columns:
        porcentajes = []
        rutas = []
        sentidos = []
        for route_id, group in df_energy.groupby("route_id"):
            for suffix in ["A", "B"]:
                shape_id = f"{route_id}{suffix}"
                shape_group = group[group["shape_id"] == shape_id]
                if not shape_group.empty:
                    energia_recup = shape_group.loc[shape_group["P_trac"] < 0, "E_cons"].sum()
                    energia_total = shape_group["E_cons"].sum()
                    # Evitar división por cero
                    if energia_total != 0:
                        porcentaje = abs(energia_recup) / energia_total * 100
                    else:
                        porcentaje = 0
                    rutas.append(route_id)
                    sentidos.append(suffix)
                    porcentajes.append(porcentaje)

        # Crear el gráfico de barras agrupadas
        import numpy as np
        rutas_unicas = list(sorted(set(rutas)))
        x = np.arange(len(rutas_unicas))
        width = 0.35

        fig, ax = plt.subplots(figsize=(10, 6))
        # Obtener los porcentajes para cada sentido alineados por ruta
        porcentajes_A = [porcentajes[i] for i in range(len(porcentajes)) if sentidos[i] == "A"]
        porcentajes_B = [porcentajes[i] for i in range(len(porcentajes)) if sentidos[i] == "B"]

        bars_A = ax.bar(x - width/2, porcentajes_A, width, label='Sentido A', color="#4daf4a")
        bars_B = ax.bar(x + width/2, porcentajes_B, width, label='Sentido B', color="#377eb8")

        ax.set_xlabel("Ruta")
        ax.set_ylabel("Porcentaje de energía recuperada (%)")
        ax.set_title("Porcentaje de energía recuperada por frenada regenerativa\nrespecto al total consumido por ruta y sentido")
        ax.set_xticks(x)
        ax.set_xticklabels(rutas_unicas)
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        # Etiquetas encima de cada barra
        for bars in [bars_A, bars_B]:
            for bar in bars:
                yval = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, yval, f"{yval:.1f}%", ha='center', va='bottom')
        ruta_grafico_barras = os.path.join(CARPETA_GRAFICAS_CONSUMO, "porcentaje_energia_recuperada_regenerativa_rutas.jpg")
        plt.savefig(ruta_grafico_barras, format="jpg", dpi=300)
        plt.close()
        print(f"Gráfico de barras de porcentaje de energía recuperada guardado: {ruta_grafico_barras}")
    else:
        print("No se encontraron las columnas necesarias para el gráfico de energía recuperada por ruta.")
else:
    print("No se encontró el archivo df_energy_consumption.csv. No se generaron gráficas de consumo.")

# --- Gráficas de perfiles de altitud agrupados por ruta (ambos sentidos en una imagen) ---
if df_driving_model is not None and not df_driving_model.empty and "altitude" in df_driving_model.columns:
    CARPETA_GRAFICAS_ALTITUD = os.path.join(CARPETA_DATOS, "Graficas_Altitud")
    os.makedirs(CARPETA_GRAFICAS_ALTITUD, exist_ok=True)

    for route_id, group in df_driving_model.groupby("route_id"):
        fig, ax = plt.subplots(figsize=(16, 6))
        plotted = False
        for suffix, color in zip(["A", "B"], ["#1f77b4", "#ff7f0e"]):
            shape_id = f"{route_id}{suffix}"
            shape_group = group[group["shape_id"] == shape_id]
            # Filtrar NaN en altitude y shape_dist_traveled
            shape_group = shape_group.dropna(subset=["altitude", "shape_dist_traveled"])
            if not shape_group.empty:
                ax.plot(
                    shape_group["shape_dist_traveled"],
                    shape_group["altitude"],
                    label=f"Sentido {suffix}",
                    color=color
                )
                plotted = True
        if plotted:
            ax.set_xlabel("Distancia Recorrida (m)")
            ax.set_ylabel("Altitud (m)")
            ax.set_title(f"Perfil de Altitud - Ruta {route_id}")
            ax.grid(True)
            ax.legend()
            plt.tight_layout()
            ruta_grafica_altitud = os.path.join(CARPETA_GRAFICAS_ALTITUD, f"altitud_route_{route_id}.jpg")
            plt.savefig(ruta_grafica_altitud, format="jpg", dpi=300)
            plt.close()
            print(f"Gráfica de perfil de altitud guardada: {ruta_grafica_altitud}")
        else:
            plt.close()
else:
    print("No se generaron gráficas de altitud: el DataFrame está vacío o falta la columna 'altitude'.")
