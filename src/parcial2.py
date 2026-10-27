"""
parcial2.py
Segundo Parcial - Inteligencia Artificial (2026-02)
Docente: Ing. Jhon James Cano Sánchez
Grupo 05: Andrés Felipe Mejía Suaza & Miguel Ángel Ramírez Gutiérrez
Archivo asignado: grupo_05.csv (Calidad del aire - mediciones en Cartago, Valle del Cauca)
"""

import os
import pandas as pd
import numpy as np


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


def tarea_3_limpieza_datos(df_raw, ruta_salida):
    """
    Tarea 3: Calidad y limpieza de datos con Pandas.
    Identifica y corrige todos los problemas de calidad en grupo_05.csv:
      1. Filas duplicadas exactas (4 filas: M004, M059, M066, M067).
      2. Formato numérico con coma decimal en 'viento_m_s' (3 filas: M001, M032, M044).
      3. Valores nulos en 'viento_m_s' (3 filas: M006, M010, M021).
      4. Valor extremo por unidad equivocada en 'pm25_ugm3' (M075 = 70100.0 ng/m3 -> 70.1 ug/m3).
    """
    print("\n" + "=" * 78)
    print("  TAREA 3. CALIDAD Y LIMPIEZA DE DATOS CON PANDAS")
    print("=" * 78)

    df = df_raw.copy()
    filas_antes = len(df)
    media_pm25_cruda = df["pm25_ugm3"].mean()
    std_pm25_cruda = df["pm25_ugm3"].std()

    # Problema 1: Filas duplicadas exactas
    num_duplicados = int(df.duplicated().sum())
    df = df.drop_duplicates(keep="first").copy()
    print(f"\n[Problema 1 - Filas duplicadas]: Detectadas {num_duplicados} filas duplicadas exactas (M004, M059, M066, M067).")
    print("  -> Decisión: Eliminar duplicados conservando la primera aparición (drop_duplicates).")
    print(f"  -> Filas tras eliminar duplicados: {len(df)}")

    # Problema 2: Texto / comas decimales en columna numérica 'viento_m_s'
    mascara_comas = df["viento_m_s"].astype(str).str.contains(",", na=False)
    num_comas = int(mascara_comas.sum())
    df["viento_m_s"] = df["viento_m_s"].astype(str).str.replace(",", ".", regex=False)
    df["viento_m_s"] = pd.to_numeric(df["viento_m_s"], errors="coerce")
    print(f"\n[Problema 2 - Comas decimales en 'viento_m_s']: Detectados {num_comas} valores con coma ('2,0', '7,0', '5,6').")
    print("  -> Decisión: Convertir ',' a '.' y transformar la columna a float64 con pd.to_numeric().")

    # Problema 3: Valores faltantes (NaN) en 'viento_m_s'
    num_nulos = int(df["viento_m_s"].isnull().sum())
    print(f"\n[Problema 3 - Valores faltantes en 'viento_m_s']: Detectados {num_nulos} registros con NaN (M006, M010, M021).")
    print("  -> Decisión: Eliminar las 3 filas incompletas (dropna) para no distorsionar la relación")
    print("     física entre PM2.5 y viento con imputaciones artificiales.")
    df = df.dropna(subset=["viento_m_s"]).copy()
    print(f"  -> Filas tras eliminar nulos: {len(df)}")

    # Problema 4: Valor sospechoso con unidad equivocada en 'pm25_ugm3' (M075 = 70100.0)
    media_pm25_antes_corr = df["pm25_ugm3"].mean()
    std_pm25_antes_corr = df["pm25_ugm3"].std()
    mascara_unidad = df["pm25_ugm3"] > 1000
    print(f"\n[Problema 4 - Unidad equivocada en 'pm25_ugm3']: Detectado {int(mascara_unidad.sum())} registro extremo:")
    print(df[mascara_unidad][["medicion_id", "estacion", "pm25_ugm3", "viento_m_s", "alerta_calidad"]])
    print("  -> Decisión: Corregir dividiendo entre 1000 (70100.0 ng/m³ -> 70.1 µg/m³), ya que fue")
    print("     registrado en nanogramos/m³ en vez de microgramos/m³.")
    df.loc[mascara_unidad, "pm25_ugm3"] = df.loc[mascara_unidad, "pm25_ugm3"] / 1000.0

    # Normalización preventiva de texto en columna categórica
    df["estacion"] = df["estacion"].astype(str).str.strip()
    df = df.reset_index(drop=True)

    media_pm25_despues = df["pm25_ugm3"].mean()
    std_pm25_despues = df["pm25_ugm3"].std()
    filas_despues = len(df)
    conteo_clases = df["alerta_calidad"].value_counts().sort_index()

    print("\n[Resumen de Limpieza]:")
    print(f"  • Número de filas ANTES de la limpieza  : {filas_antes}")
    print(f"  • Número de filas DESPUÉS de la limpieza: {filas_despues}")
    print(f"  • Registros de Clase 0 (Sin alerta)     : { int(conteo_clases.get(0, 0)) }")
    print(f"  • Registros de Clase 1 (Con alerta)     : { int(conteo_clases.get(1, 0)) }")

    print("\n[Respuesta a la Pregunta Clave de la Tarea 3]:")
    print("  • Valor más sospechoso: pm25_ugm3 = 70100.0 en el registro M075 (Universidad).")
    print(f"  • Media de 'pm25_ugm3' ANTES de corregirlo (dataset crudo, 84 filas) : {media_pm25_cruda:.2f} µg/m³ (Desv: {std_pm25_cruda:.2f})")
    print(f"  • Media de 'pm25_ugm3' ANTES de corregirlo (77 filas sin dup/nulos)  : {media_pm25_antes_corr:.2f} µg/m³ (Desv: {std_pm25_antes_corr:.2f})")
    print(f"  • Media de 'pm25_ugm3' DESPUÉS de corregirlo (70100.0 -> 70.1 µg/m³): {media_pm25_despues:.2f} µg/m³ (Desv: {std_pm25_despues:.2f})")
    print("  • ¿Cómo habría afectado el escalado del perceptrón si no se hubiera corregido?")
    print("    Al estandarizar X con z = (x - media) / desviación, el valor 70100.0 infla la media")
    print("    hasta ~950.78 µg/m³ y la desviación estándar hasta ~7983.79 µg/m³. Esto provocaría que")
    print("    las 76 mediciones normales (entre 5.9 y 79.4 µg/m³) quedaran aplastadas en un rango")
    print("    diminuto de z-score entre -0.118 y -0.109 (casi idénticas entre sí), mientras M075")
    print("    tendría z = +8.66, destruyendo la capacidad del perceptrón para separar por PM2.5.")

    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    df.to_csv(ruta_salida, index=False, encoding="utf-8")
    print(f"\n[OK] Archivo limpio guardado exitosamente en: {ruta_salida}")

    return df


def main():
    base_dir = obtener_directorio_base()
    ruta_csv = os.path.join(base_dir, "data", "grupo_05.csv")
    ruta_limpio = os.path.join(base_dir, "data", "grupo_05_limpio.csv")

    df_raw = tarea_2_carga_inspeccion(ruta_csv)
    tarea_3_limpieza_datos(df_raw, ruta_limpio)


if __name__ == "__main__":
    main()
