"""
parcial2.py
Segundo Parcial - Inteligencia Artificial (2026-02)
Docente: Ing. Jhon James Cano Sánchez
Grupo 05: Andrés Felipe Mejía Suaza & Miguel Ángel Ramírez Gutiérrez
Archivo asignado: grupo_05.csv (Calidad del aire - mediciones en Cartago, Valle del Cauca)
"""

import os
import pandas as pd


def obtener_directorio_base():
    """Resuelve la raíz del proyecto tanto si se ejecuta desde /app como desde /app/src."""
    actual = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(actual) == "src":
        return os.path.dirname(actual)
    return actual


def tarea_2_carga_inspeccion(ruta_csv):
    """
    Tarea 2: Carga e inspección inicial del archivo grupo_05.csv con Pandas.
    Muestra primeras 5 filas, shape, tipos de datos (info y dtypes),
    cantidad de nulos por columna y cantidad de filas duplicadas.
    """
    print("=" * 78)
    print("  TAREA 2. CARGA E INSPECCIÓN DE DATOS (grupo_05.csv)")
    print("=" * 78)

    df = pd.read_csv(ruta_csv)

    print("\n[2.1] Primeras 5 filas del DataFrame (df.head()):")
    print(df.head())

    print(f"\n[2.2] Forma del DataFrame (df.shape): {df.shape[0]} filas x {df.shape[1]} columnas")

    print("\n[2.3] Tipos de datos (df.dtypes):")
    print(df.dtypes)

    print("\n[2.4] Información detallada del DataFrame (df.info()):")
    df.info()

    print("\n[2.5] Cantidad de valores nulos por columna (df.isnull().sum()):")
    print(df.isnull().sum())

    duplicados = int(df.duplicated().sum())
    print(f"\n[2.6] Cantidad de filas duplicadas exactas (df.duplicated().sum()): {duplicados}")
    if duplicados > 0:
        print("      Registros duplicados detectados:")
        print(df[df.duplicated(keep=False)].sort_values("medicion_id"))

    print("\n[2.7] Respuesta a la Pregunta Clave de la Tarea 2:")
    filas_con_coma = df[df["viento_m_s"].astype(str).str.contains(",", na=False)]
    print("      • ¿Alguna columna numérica aparece con un tipo de dato que no debería tener?")
    print("        Sí: la columna 'viento_m_s' (velocidad del viento en m/s) aparece con tipo")
    print("        de dato texto ('object' / 'str') en lugar de numérico ('float64').")
    print("      • ¿Por qué ocurre?")
    print("        Porque existen 3 registros ('M001' con '2,0', 'M032' con '7,0' y 'M044' con '5,6')")
    print("        que fueron exportados con coma decimal (',') en vez de punto decimal ('.').")
    print("        Al encontrar cadenas con coma, Pandas infiere toda la columna como texto:")
    print(filas_con_coma[["medicion_id", "estacion", "pm25_ugm3", "viento_m_s", "alerta_calidad"]])

    return df


def main():
    base_dir = obtener_directorio_base()
    ruta_csv = os.path.join(base_dir, "data", "grupo_05.csv")
    tarea_2_carga_inspeccion(ruta_csv)


if __name__ == "__main__":
    main()
