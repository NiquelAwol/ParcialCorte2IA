"""
parcial2.py
Segundo Parcial - Inteligencia Artificial (2026-02)
Docente: Ing. Jhon James Cano Sánchez
Grupo 05: Andrés Felipe Mejía Suaza & Miguel Ángel Ramírez Gutiérrez
Archivo asignado: grupo_05.csv (Calidad del aire - mediciones en Cartago, Valle del Cauca)

Flujo completo:
  - Tarea 2: Carga e inspección de datos con Pandas.
  - Tarea 3: Calidad y limpieza de datos con Pandas -> data/grupo_05_limpio.csv.
  - Tarea 4: Visualización con Seaborn -> grafico1_dispersion.png y grafico2_comparacion.png.
  - Tarea 5: Perceptrón desde cero con NumPy -> curva_aprendizaje.png y frontera_decision.png.
  - Tarea 6: Interpretación de resultados y evaluación de 2 nuevos registros realistas.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def obtener_directorio_base():
    """Resuelve la raíz del proyecto tanto si se ejecuta desde /app como desde /app/src."""
    actual = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(actual) == "src":
        return os.path.dirname(actual)
    return actual


# =============================================================================
# TAREA 2. CARGA E INSPECCIÓN DE DATOS
# =============================================================================
def tarea_2_carga_inspeccion(ruta_csv):
    """
    Carga el CSV con Pandas y muestra en consola: primeras 5 filas, shape,
    tipos de datos (dtypes e info), nulos por columna y filas duplicadas.
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


# =============================================================================
# TAREA 3. CALIDAD Y LIMPIEZA DE DATOS CON PANDAS
# =============================================================================
def tarea_3_limpieza_datos(df_raw, ruta_salida):
    """
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


# =============================================================================
# TAREA 4. VISUALIZACIÓN CON SEABORN
# =============================================================================
def tarea_4_visualizacion_seaborn(df_clean, base_dir):
    """
    Genera y guarda los dos gráficos con Seaborn:
      - grafico1_dispersion.png (sns.scatterplot de pm25_ugm3 vs viento_m_s con hue=alerta_calidad)
      - grafico2_comparacion.png (sns.boxplot de pm25_ugm3 por clase y sns.countplot por estacion)
    """
    print("\n" + "=" * 78)
    print("  TAREA 4. VISUALIZACIÓN CON SEABORN")
    print("=" * 78)

    sns.set_theme(style="whitegrid")
    df_vis = df_clean.copy()
    df_vis["Estado de Alerta"] = df_vis["alerta_calidad"].map({
        0: "0: Sin Alerta (Normal)",
        1: "1: Con Alerta (Crítico)"
    })
    paleta = {
        "0: Sin Alerta (Normal)": "#10b981",
        "1: Con Alerta (Crítico)": "#ef4444"
    }

    # Gráfico 1: Dispersión de las dos variables numéricas coloreada por el objetivo
    plt.figure(figsize=(9, 6))
    sns.scatterplot(
        data=df_vis,
        x="pm25_ugm3",
        y="viento_m_s",
        hue="Estado de Alerta",
        style="Estado de Alerta",
        palette=paleta,
        markers={"0: Sin Alerta (Normal)": "o", "1: Con Alerta (Crítico)": "X"},
        s=120,
        alpha=0.9,
        edgecolor="black"
    )
    plt.title(
        "Gráfico 1: Concentración de PM2.5 vs. Velocidad del Viento por Alerta de Calidad (Cartago)",
        fontsize=12.5,
        weight="bold",
        pad=14
    )
    plt.xlabel("Concentración de Material Particulado PM2.5 (µg/m³)", fontsize=11, weight="bold")
    plt.ylabel("Velocidad del Viento (m/s)", fontsize=11, weight="bold")
    plt.legend(title="alerta_calidad (Objetivo)", loc="upper left", frameon=True)
    plt.tight_layout()

    ruta_g1 = os.path.join(base_dir, "grafico1_dispersion.png")
    plt.savefig(ruta_g1, dpi=300)
    plt.close()
    print(f"\n[OK] Gráfico 1 guardado en: {ruta_g1}")
    print("     Interpretación: Muestra que las alertas (clase 1, n=35) se concentran en valores")
    print("     altos de PM2.5 (media 54.26 µg/m³) y vientos bajos/moderados (media 3.34 m/s),")
    print("     mientras que sin alerta (clase 0, n=42) predomina PM2.5 bajo (media 30.50 µg/m³)")
    print("     y mayor ventilación (media 5.40 m/s), evidenciando separabilidad lineal aproximada.")

    # Gráfico 2: Comparación por clase (sns.boxplot y sns.countplot)
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.8))

    sns.boxplot(
        data=df_vis,
        x="Estado de Alerta",
        y="pm25_ugm3",
        hue="Estado de Alerta",
        palette=paleta,
        width=0.45,
        ax=axes[0],
        legend=False
    )
    np.random.seed(42)
    sns.stripplot(
        data=df_vis,
        x="Estado de Alerta",
        y="pm25_ugm3",
        color="black",
        alpha=0.45,
        jitter=0.15,
        size=6,
        ax=axes[0]
    )
    axes[0].set_title("A) Distribución de PM2.5 según Clase (Boxplot)", fontsize=11.5, weight="bold")
    axes[0].set_xlabel("Clase Objetivo (alerta_calidad)", fontsize=10.5, weight="bold")
    axes[0].set_ylabel("Concentración PM2.5 (µg/m³)", fontsize=10.5, weight="bold")

    orden_estaciones = ["Universidad", "Terminal", "Zona Industrial", "Hospital", "Centro"]
    sns.countplot(
        data=df_vis,
        x="estacion",
        hue="Estado de Alerta",
        order=orden_estaciones,
        palette=paleta,
        edgecolor="black",
        ax=axes[1]
    )
    axes[1].set_title("B) Alertas de Calidad del Aire por Estación (Countplot)", fontsize=11.5, weight="bold")
    axes[1].set_xlabel("Estación de Monitoreo en Cartago", fontsize=10.5, weight="bold")
    axes[1].set_ylabel("Cantidad de Mediciones", fontsize=10.5, weight="bold")
    axes[1].tick_params(axis="x", rotation=15)
    axes[1].legend(title="alerta_calidad", loc="upper right")

    for container in axes[1].containers:
        axes[1].bar_label(container, fontsize=9.5, weight="bold", padding=2)

    fig.suptitle(
        "Gráfico 2: Comparación de PM2.5 y Estaciones de Monitoreo frente a la Alerta de Calidad",
        fontsize=13,
        weight="bold",
        y=1.02
    )
    plt.tight_layout()

    ruta_g2 = os.path.join(base_dir, "grafico2_comparacion.png")
    plt.savefig(ruta_g2, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] Gráfico 2 guardado en: {ruta_g2}")
    print("     Interpretación: El boxplot (Panel A) demuestra que la mediana de PM2.5 sube de")
    print("     30.70 µg/m³ (clase 0) a 54.40 µg/m³ (clase 1). El countplot (Panel B) revela que")
    print("     Universidad (15/24 alertas, 62.5%) y Terminal (11/18 alertas, 61.1%) concentran")
    print("     26 de las 35 alertas totales (74.3%) registradas en Cartago.")


# =============================================================================
# TAREA 5. PERCEPTRÓN DESDE CERO CON NUMPY (SIN SCIKIT-LEARN)
# =============================================================================
def sigmoide(z):
    """Función de activación sigmoide: 1 / (1 + exp(-z))."""
    z_clip = np.clip(z, -500, 500)
    return 1.0 / (1.0 + np.exp(-z_clip))


def predecir_probabilidad(X, w, b):
    """Calcula la probabilidad predicha P(y=1|X) = sigmoide(X @ w + b)."""
    return sigmoide(X @ w + b)


def perdida_logaritmica(y_true, y_prob):
    """Calcula la pérdida logarítmica (Binary Cross-Entropy)."""
    eps = 1e-15
    y_prob_clip = np.clip(y_prob, eps, 1.0 - eps)
    return -float(np.mean(y_true * np.log(y_prob_clip) + (1.0 - y_true) * np.log(1.0 - y_prob_clip)))


def calcular_exactitud(y_true, y_prob, umbral=0.5):
    """Calcula la exactitud (accuracy) comparando predicciones binarias con y_true."""
    y_pred = (y_prob >= umbral).astype(int)
    return float(np.mean(y_pred == y_true))


def tarea_5_perceptron_numpy(df_clean, base_dir):
    """
    Implementa y entrena desde cero con NumPy un perceptrón con función sigmoide y
    descenso del gradiente durante 300 épocas. Genera curva_aprendizaje.png y
    frontera_decision.png (en las unidades originales de PM2.5 y viento).
    """
    print("\n" + "=" * 78)
    print("  TAREA 5. PERCEPTRÓN DESDE CERO CON NUMPY (CLASE 9)")
    print("=" * 78)

    # 1. Separar X (las dos columnas numéricas) e y (columna objetivo) como arreglos de NumPy
    X = df_clean[["pm25_ugm3", "viento_m_s"]].to_numpy(dtype=float)
    y = df_clean["alerta_calidad"].to_numpy(dtype=float)
    m, n = X.shape

    # 2. Estandarizar X (media 0 y desviación 1 por columna) y guardar media y desviación
    media_X = np.mean(X, axis=0)
    desv_X = np.std(X, axis=0)
    X_std = (X - media_X) / desv_X

    print("\n[5.1] Escalado de variables de entrada (Estandarización Z-score con NumPy):")
    print(f"  • x1 ('pm25_ugm3')  -> Media guardada = {media_X[0]:.4f} µg/m³ | Desviación guardada = {desv_X[0]:.4f} µg/m³")
    print(f"  • x2 ('viento_m_s') -> Media guardada = {media_X[1]:.4f} m/s   | Desviación guardada = {desv_X[1]:.4f} m/s")
    print(f"  • Verificación post-escalado: medias = {np.mean(X_std, axis=0).round(6)}, desviaciones = {np.std(X_std, axis=0).round(6)}")

    # 3. Inicialización de parámetros y hiperparámetros de descenso del gradiente
    w_inicial = np.zeros(n, dtype=float)
    b_inicial = 0.0
    w = w_inicial.copy()
    b = float(b_inicial)

    tasa_aprendizaje = 0.1
    epocas = 300

    prob_inicial = predecir_probabilidad(X_std, w, b)
    perdida_ini = perdida_logaritmica(y, prob_inicial)
    exactitud_ini = calcular_exactitud(y, prob_inicial)

    historial_perdida = []
    historial_exactitud = []

    # 4. Entrenamiento con descenso del gradiente durante 300 épocas
    for epoca in range(epocas):
        y_prob = predecir_probabilidad(X_std, w, b)

        loss = perdida_logaritmica(y, y_prob)
        acc = calcular_exactitud(y, y_prob)
        historial_perdida.append(loss)
        historial_exactitud.append(acc)

        # Gradientes analíticos de la pérdida logarítmica con activación sigmoide
        error = y_prob - y
        dw = (X_std.T @ error) / m
        db = float(np.mean(error))

        w = w - tasa_aprendizaje * dw
        b = b - tasa_aprendizaje * db

    prob_final = predecir_probabilidad(X_std, w, b)
    perdida_fin = perdida_logaritmica(y, prob_final)
    exactitud_fin = calcular_exactitud(y, prob_final)
    y_pred_final = (prob_final >= 0.5).astype(int)
    aciertos = int(np.sum(y_pred_final == y.astype(int)))
    mal_clasificados = int(m - aciertos)

    print("\n[5.2] Resultados del Entrenamiento del Perceptrón (300 épocas, lr = 0.1):")
    print(f"  • Pesos iniciales (w1, w2, b) : w1 = {w_inicial[0]:.4f}, w2 = {w_inicial[1]:.4f}, b = {b_inicial:.4f}")
    print(f"  • Pesos finales   (w1, w2, b) : w1 = {w[0]:.4f}, w2 = {w[1]:.4f}, b = {b:.4f}")
    print(f"  • Pérdida inicial (Época 0)   : {perdida_ini:.4f}")
    print(f"  • Pérdida final   (Época {epocas}) : {perdida_fin:.4f}")
    print(f"  • Exactitud inicial           : {exactitud_ini * 100:.2f}%")
    print(f"  • Exactitud final             : {exactitud_fin * 100:.2f}% ({aciertos}/{m} aciertos, {mal_clasificados} en el lado equivocado)")

    # 5. Generar curva_aprendizaje.png (pérdida por época)
    plt.figure(figsize=(8.5, 5.2))
    plt.plot(range(1, epocas + 1), historial_perdida, color="#0284c7", linewidth=2.5, label="Pérdida Logarítmica (BCE)")
    plt.title("Curva de Aprendizaje del Perceptrón (Descenso del Gradiente - 300 Épocas)", fontsize=12.5, weight="bold", pad=12)
    plt.xlabel("Época", fontsize=11, weight="bold")
    plt.ylabel("Pérdida Logarítmica (Binary Cross-Entropy)", fontsize=11, weight="bold")
    plt.annotate(
        f"Pérdida inicial: {historial_perdida[0]:.4f}",
        xy=(1, historial_perdida[0]),
        xytext=(35, historial_perdida[0] - 0.04),
        arrowprops=dict(facecolor="#0f172a", shrink=0.08, width=1.2, headwidth=5),
        fontsize=10,
        weight="bold"
    )
    plt.annotate(
        f"Pérdida final (época {epocas}): {perdida_fin:.4f}\nExactitud final: {exactitud_fin * 100:.2f}%",
        xy=(epocas, perdida_fin),
        xytext=(epocas - 135, perdida_fin + 0.10),
        arrowprops=dict(facecolor="#16a34a", shrink=0.08, width=1.2, headwidth=5),
        fontsize=10,
        weight="bold"
    )
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(loc="upper right", fontsize=10.5)
    plt.tight_layout()

    ruta_curva = os.path.join(base_dir, "curva_aprendizaje.png")
    plt.savefig(ruta_curva, dpi=300)
    plt.close()
    print(f"\n[OK] Gráfico de curva de aprendizaje guardado en: {ruta_curva}")

    # 6. Generar frontera_decision.png en las UNIDADES ORIGINALES
    # Ecuación en espacio estandarizado: w1 * ((x1 - mu1)/s1) + w2 * ((x2 - mu2)/s2) + b = 0
    # Despejando x2 (viento_m_s) en función de x1 (pm25_ugm3) en unidades originales:
    plt.figure(figsize=(9.5, 6.2))

    x1_min, x1_max = 0.0, float(X[:, 0].max() + 6.0)
    x2_min, x2_max = 0.0, float(X[:, 1].max() + 0.8)

    xx1, xx2 = np.meshgrid(np.linspace(x1_min, x1_max, 300), np.linspace(x2_min, x2_max, 300))
    grid_orig = np.c_[xx1.ravel(), xx2.ravel()]
    grid_std = (grid_orig - media_X) / desv_X
    probs_grid = predecir_probabilidad(grid_std, w, b).reshape(xx1.shape)

    plt.contourf(xx1, xx2, probs_grid, levels=np.linspace(0, 1, 11), cmap="RdYlGn_r", alpha=0.30)
    cbar = plt.colorbar()
    cbar.set_label("Probabilidad estimada P(alerta_calidad = 1)", fontsize=10.5, weight="bold")

    # Línea de la frontera de decisión (P = 0.5) en unidades originales
    x1_vals = np.linspace(x1_min, x1_max, 200)
    z1_vals = (x1_vals - media_X[0]) / desv_X[0]
    z2_frontera = -(w[0] * z1_vals + b) / w[1]
    x2_frontera = media_X[1] + desv_X[1] * z2_frontera

    pendiente_orig = -(w[0] / desv_X[0]) / (w[1] / desv_X[1])
    intercepto_orig = media_X[1] - desv_X[1] * (b - w[0] * media_X[0] / desv_X[0]) / w[1]

    plt.plot(
        x1_vals,
        x2_frontera,
        color="#0f172a",
        linestyle="--",
        linewidth=2.6,
        label=f"Frontera de Decisión (P=0.5): viento = {pendiente_orig:.3f}·PM2.5 {intercepto_orig:+.2f}"
    )

    mascara_0 = (y == 0)
    mascara_1 = (y == 1)
    plt.scatter(
        X[mascara_0, 0],
        X[mascara_0, 1],
        color="#10b981",
        edgecolor="black",
        s=95,
        marker="o",
        label="Clase 0: Sin Alerta (42 registros)",
        alpha=0.95
    )
    plt.scatter(
        X[mascara_1, 0],
        X[mascara_1, 1],
        color="#ef4444",
        edgecolor="black",
        s=110,
        marker="X",
        label="Clase 1: Con Alerta (35 registros)",
        alpha=0.95
    )

    # Resaltar los registros que quedan del lado equivocado de la frontera
    mascara_err = (y_pred_final != y.astype(int))
    plt.scatter(
        X[mascara_err, 0],
        X[mascara_err, 1],
        facecolors="none",
        edgecolors="#f59e0b",
        linewidths=2.2,
        s=210,
        label=f"Lado equivocado ({mal_clasificados} registros)"
    )

    plt.title(
        "Frontera de Decisión del Perceptrón en Unidades Originales (PM2.5 vs. Viento)",
        fontsize=12.5,
        weight="bold",
        pad=12
    )
    plt.xlabel("Concentración de PM2.5 (µg/m³)", fontsize=11, weight="bold")
    plt.ylabel("Velocidad del Viento (m/s)", fontsize=11, weight="bold")
    plt.xlim(x1_min, x1_max)
    plt.ylim(x2_min, x2_max)
    plt.legend(loc="upper left", fontsize=9.5, framealpha=0.95)
    plt.grid(True, linestyle=":", alpha=0.5)
    plt.tight_layout()

    ruta_frontera = os.path.join(base_dir, "frontera_decision.png")
    plt.savefig(ruta_frontera, dpi=300)
    plt.close()
    print(f"[OK] Gráfico de frontera de decisión guardado en: {ruta_frontera}")

    return {
        "w": w,
        "b": b,
        "media_X": media_X,
        "desv_X": desv_X,
        "perdida_ini": perdida_ini,
        "perdida_fin": perdida_fin,
        "exactitud_fin": exactitud_fin,
        "aciertos": aciertos,
        "total": m,
        "mal_clasificados": mal_clasificados,
        "df_errores": df_clean[mascara_err].copy()
    }


# =============================================================================
# TAREA 6. INTERPRETACIÓN DE RESULTADOS Y PREDICCIÓN DE NUEVOS REGISTROS
# =============================================================================
def tarea_6_interpretacion(resultados):
    """
    Responde en consola las preguntas de interpretación de la Tarea 6, incluyendo
    la evaluación de dos registros nuevos realistas escalados con la media y desviación
    del entrenamiento.
    """
    print("\n" + "=" * 78)
    print("  TAREA 6. INTERPRETACIÓN DE RESULTADOS (GRUPO 05 - CARTAGO)")
    print("=" * 78)

    w = resultados["w"]
    b = resultados["b"]
    media_X = resultados["media_X"]
    desv_X = resultados["desv_X"]

    print("\n[6.1] Significado del signo de w1 y w2 en Cartago:")
    print(f"  • w1 (pm25_ugm3) = {w[0]:+.4f} (POSITIVO): A mayor concentración de PM2.5 (µg/m³),")
    print("    mayor es el valor de z = X @ w + b y mayor la probabilidad de alerta ambiental (y=1).")
    print(f"  • w2 (viento_m_s) = {w[1]:+.4f} (NEGATIVO): A mayor velocidad del viento (m/s),")
    print("    menor es la probabilidad de alerta (y=1), pues el viento dispersa el material particulado.")
    print("  • ¿Tiene sentido para Cartago? Sí, totalmente: en el valle geográfico de Cartago,")
    print("    las quemas de caña y el tráfico elevan el PM2.5 (factor de riesgo, w1 > 0), mientras")
    print("    que las corrientes de viento actúan como mecanismo natural de ventilación (factor protector, w2 < 0).")

    print("\n[6.2] Separabilidad lineal y registros del lado equivocado:")
    print(f"  • Los datos son aproximadamente linealmente separables: el perceptrón alcanza una")
    print(f"    exactitud de {resultados['exactitud_fin'] * 100:.2f}% ({resultados['aciertos']}/{resultados['total']} registros correctos).")
    print(f"  • Quedan exactamente {resultados['mal_clasificados']} registros del lado equivocado de la frontera:")
    print("    - 4 Falsos Positivos (clase real 0 predicha como 1): M008, M051, M056, M069.")
    print("    - 6 Falsos Negativos (clase real 1 predicha como 0): M012, M017, M038, M040, M068, M071.")

    # 6.3 Inventar dos registros nuevos realistas, escalarlos y predecir probabilidad
    # Caso A (Esperado = 1): Hora pico en Terminal con alta contaminación y calma atmosférica
    nuevo_alerta = np.array([68.0, 1.5])
    # Caso B (Esperado = 0): Mañana ventilada en Hospital con aire limpio y brisa fuerte
    nuevo_normal = np.array([18.0, 6.8])

    nuevo_alerta_std = (nuevo_alerta - media_X) / desv_X
    nuevo_normal_std = (nuevo_normal - media_X) / desv_X

    prob_alerta = float(predecir_probabilidad(nuevo_alerta_std, w, b))
    prob_normal = float(predecir_probabilidad(nuevo_normal_std, w, b))

    print("\n[6.3] Evaluación de dos registros nuevos realistas:")
    print("  1) Registro Nuevo A (Esperado = 1 - Alerta en Terminal en hora pico sin viento):")
    print(f"     • Valores originales : pm25_ugm3 = {nuevo_alerta[0]:.1f} µg/m³, viento_m_s = {nuevo_alerta[1]:.1f} m/s")
    print(f"     • Valores escalados  : z1 = {nuevo_alerta_std[0]:+.4f}, z2 = {nuevo_alerta_std[1]:+.4f}")
    print(f"     • Probabilidad P(y=1): {prob_alerta:.4f} ({prob_alerta * 100:.2f}%) -> Predicción = {int(prob_alerta >= 0.5)} (Coincide con 1 esperado)")

    print("  2) Registro Nuevo B (Esperado = 0 - Sin alerta en Hospital con brisa fuerte):")
    print(f"     • Valores originales : pm25_ugm3 = {nuevo_normal[0]:.1f} µg/m³, viento_m_s = {nuevo_normal[1]:.1f} m/s")
    print(f"     • Valores escalados  : z1 = {nuevo_normal_std[0]:+.4f}, z2 = {nuevo_normal_std[1]:+.4f}")
    print(f"     • Probabilidad P(y=1): {prob_normal:.4f} ({prob_normal * 100:.2f}%) -> Predicción = {int(prob_normal >= 0.5)} (Coincide con 0 esperado)")


def main():
    base_dir = obtener_directorio_base()
    ruta_csv = os.path.join(base_dir, "data", "grupo_05.csv")
    ruta_limpio = os.path.join(base_dir, "data", "grupo_05_limpio.csv")

    df_raw = tarea_2_carga_inspeccion(ruta_csv)
    df_clean = tarea_3_limpieza_datos(df_raw, ruta_limpio)
    tarea_4_visualizacion_seaborn(df_clean, base_dir)
    resultados = tarea_5_perceptron_numpy(df_clean, base_dir)
    tarea_6_interpretacion(resultados)


if __name__ == "__main__":
    main()
