# Segundo Parcial – Inteligencia Artificial (Grupo 05)

**Asignatura:** Inteligencia Artificial · Ingeniería de Sistemas (2026-02)  
**Docente:** Ing. Jhon James Cano Sánchez  
**Grupo:** 05  
**Integrantes:**
- **Andrés Felipe Mejía Suaza**
- **Miguel Ángel Ramírez Gutiérrez**

**Archivo Asignado:** `data/grupo_05.csv`  
**Tema (Anexo A):** Calidad del aire – mediciones en Cartago, Valle del Cauca  
**Variables de Entrada ($x_1, x_2$):** `pm25_ugm3` ($\mu\text{g/m}^3$), `viento_m_s` ($\text{m/s}$)  
**Variable Objetivo ($y$):** `alerta_calidad` (`1` = se emitió alerta de calidad del aire, `0` = no se emitió alerta)

---

## Tarea 1. Configuración del Entorno

El proyecto cuenta con una arquitectura reproducible basada en contenedores Docker con **Python 3.12**, **NumPy**, **Pandas**, **Matplotlib** y **Seaborn**, usando el contenedor `parcial2_ia` para no entrar en conflicto con el contenedor `python_ia` de las sesiones de clase.

### Estructura del Repositorio

```text
parcial2/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── data/
│   ├── grupo_05.csv
│   └── grupo_05_limpio.csv
└── src/
    └── parcial2.py
```

### Comandos para Reproducir el Entorno (WSL + Docker)

```bash
# 1. En WSL, ubicarse en la carpeta del proyecto
mkdir -p parcial2/src parcial2/data
cd parcial2

# 2. Verificar contenedores en ejecución (detener python_ia si está activo)
docker ps
# Si python_ia está encendido: docker stop python_ia

# 3. Construir y levantar el contenedor parcial2_ia en segundo plano
docker-compose up -d --build

# 4. Ingresar al contenedor interactivo
docker exec -it parcial2_ia bash

# 5. Dentro del contenedor, ejecutar el flujo completo del parcial
cd src
python parcial2.py
exit
```

---

## Tarea 2. Carga e Inspección de Datos (`grupo_05.csv`)

Al cargar el archivo original `data/grupo_05.csv` con Pandas desde `src/parcial2.py`, se obtienen los siguientes resultados de diagnóstico inicial:

### 2.1 Primeras 5 filas (`df.head()`)

| Índice | `medicion_id` | `estacion` | `pm25_ugm3` | `viento_m_s` | `alerta_calidad` |
| :---: | :---: | :--- | :---: | :---: | :---: |
| 0 | `M001` | Terminal | 52.9 | `2,0` | 1 |
| 1 | `M002` | Universidad | 79.4 | `0.6` | 1 |
| 2 | `M003` | Zona Industrial | 12.3 | `7.9` | 0 |
| 3 | `M004` | Terminal | 43.0 | `7.7` | 0 |
| 4 | `M005` | Centro | 34.7 | `5.2` | 0 |

### 2.2 Resumen de Inspección Inicial

- **Forma del DataFrame (`df.shape`):** `(84, 5)` $\rightarrow$ **84 filas** y **5 columnas**.
- **Tipos de datos (`df.dtypes` / `df.info()`):**
  - `medicion_id`: `object` / `str` (84 no nulos)
  - `estacion`: `object` / `str` (84 no nulos)
  - `pm25_ugm3`: `float64` (84 no nulos)
  - `viento_m_s`: `object` / `str` (81 no nulos) $\leftarrow$ **Tipo incorrecto para una variable numérica**
  - `alerta_calidad`: `int64` (84 no nulos)
- **Cantidad de valores nulos por columna (`df.isnull().sum()`):**
  - `medicion_id`: `0`
  - `estacion`: `0`
  - `pm25_ugm3`: `0`
  - `viento_m_s`: `3` (`M006`, `M010` y `M021`)
  - `alerta_calidad`: `0`
- **Cantidad de filas duplicadas exactas (`df.duplicated().sum()`):** **`4` filas duplicadas** (`M004`, `M059`, `M066` y `M067`).

### 2.3 Pregunta Clave – Tarea 2

> **¿Alguna columna numérica aparece con un tipo de dato que no debería tener? ¿Por qué ocurre?**
>
> **Respuesta:** Sí. La columna numérica **`viento_m_s`** (velocidad del viento en $\text{m/s}$, que es la segunda entrada numérica $x_2$ del perceptrón) aparece con tipo de dato **`object` (`str` / texto)** en lugar de **`float64`**.  
> Esto ocurre porque **3 registros del archivo fueron exportados utilizando coma (`,`) como separador decimal en lugar de punto (`.`)**:
> - `M001` (Terminal): `"2,0"`
> - `M032` (Universidad): `"7,0"`
> - `M044` (Universidad): `"5,6"`
>
> Al encontrar cadenas con comas entre comillas en el CSV, el analizador de Pandas no puede convertir automáticamente la columna a punto flotante y la clasifica como texto.

---

## Tarea 3. Calidad y Limpieza de Datos con Pandas

Durante la auditoría del archivo `data/grupo_05.csv` se identificaron y corrigieron **4 problemas de calidad de datos**:

### Problema 1: Filas duplicadas exactas (4 registros)
- **¿Cómo se detectó?**  
  Ejecutando `df.duplicated().sum()` y `df[df.duplicated(keep=False)].sort_values("medicion_id")`, lo cual evidenció **4 filas repetidas exactamente** en todas sus columnas:
  ```text
     medicion_id     estacion  pm25_ugm3 viento_m_s  alerta_calidad
  3         M004     Terminal       43.0        7.7               0
  26        M004     Terminal       43.0        7.7               0
  10        M059  Universidad       74.0        7.1               1
  60        M059  Universidad       74.0        7.1               1
  64        M066     Terminal       60.3        3.5               1
  69        M066     Terminal       60.3        3.5               1
  65        M067       Centro        5.9        2.3               0
  70        M067       Centro        5.9        2.3               0
  ```
- **¿Qué decisión se tomó?**  
  **Eliminar** las 4 filas duplicadas conservando únicamente la primera aparición mediante `df.drop_duplicates(keep="first")` (reduciendo el dataset de 84 a 80 filas).
- **¿Por qué se tomó esa decisión?**  
  Porque comparten exactamente el mismo identificador de medición (`medicion_id`) y los mismos valores, producto de una doble exportación en el sistema de información. Conservarlas sesgaría la media y desviación estándar en el escalado y duplicaría artificialmente su peso en el descenso del gradiente.

### Problema 2: Texto (coma decimal) dentro de la columna numérica `viento_m_s` (3 registros)
- **¿Cómo se detectó?**  
  Al revisar `df.dtypes` (`viento_m_s` aparece como `str`/`object`) y filtrar con `df[df["viento_m_s"].astype(str).str.contains(",", na=False)]`:
  ```text
     medicion_id     estacion  pm25_ugm3 viento_m_s  alerta_calidad
  0         M001     Terminal       52.9        2,0               1
  33        M032  Universidad       55.8        7,0               0
  45        M044  Universidad       69.5        5,6               1
  ```
- **¿Qué decisión se tomó?**  
  **Convertir** el separador decimal reemplazando `","` por `"."` (`df["viento_m_s"].astype(str).str.replace(",", ".", regex=False)`) y transformar la columna a tipo numérico `float64` con `pd.to_numeric(..., errors="coerce")`.
- **¿Por qué se tomó esa decisión?**  
  Porque las magnitudes (`2.0`, `7.0` y `5.6` $\text{m/s}$) son mediciones meteorológicas completamente válidas dentro del rango normal de velocidad del viento en Cartago (`0.6` a `8.0` $\text{m/s}$). Corregir el formato preserva 3 observaciones reales y habilita el cálculo vectorial en NumPy.

### Problema 3: Valores faltantes / nulos en `viento_m_s` (3 registros)
- **¿Cómo se detectó?**  
  Ejecutando `df.isnull().sum()` y `df[df["viento_m_s"].isnull()]`, identificando 3 registros sin dato de velocidad del viento (`NaN`):
  - `M006` (Centro, `pm25_ugm3 = 20.5`, `viento_m_s = NaN`, `alerta_calidad = 0`)
  - `M010` (Terminal, `pm25_ugm3 = 26.4`, `viento_m_s = NaN`, `alerta_calidad = 0`)
  - `M021` (Terminal, `pm25_ugm3 = 60.1`, `viento_m_s = NaN`, `alerta_calidad = 0`)
- **¿Qué decisión se tomó?**  
  **Eliminar** las 3 filas con valores faltantes usando `df.dropna(subset=["viento_m_s"])` (pasando de 80 a 77 filas).
- **¿Por qué se tomó esa decisión?**  
  Porque `viento_m_s` es una de las dos únicas variables de entrada ($x_2$) del modelo. Imputar la media ($\sim 4.35\text{ m/s}$) introduciría ruido físico severo: por ejemplo, el registro `M021` tiene una concentración alta de $\text{PM}_{2.5}$ (`60.1` $\mu\text{g/m}^3$) pero **no generó alerta (`0`)**, lo cual en el fenómeno real solo ocurre cuando hay vientos muy fuertes ($> 7.0\text{ m/s}$) que dispersan el material particulado. Imputarle un viento promedio crearía un dato falso contradictorio.

### Problema 4: Valor extremo con unidad equivocada en `pm25_ugm3` (1 registro: `M075`)
- **¿Cómo se detectó?**  
  Al inspeccionar las estadísticas descriptivas (`df["pm25_ugm3"].describe()`) y filtrar `df[df["pm25_ugm3"] > 1000]`:
  ```text
     medicion_id     estacion  pm25_ugm3  viento_m_s  alerta_calidad
  78        M075  Universidad    70100.0         6.4               1
  ```
- **¿Qué decisión se tomó?**  
  **Corregir** la unidad dividiendo el valor entre $1000$ (`70100.0 / 1000 = 70.1` $\mu\text{g/m}^3$).
- **¿Por qué se tomó esa decisión?**  
  Porque todas las demás mediciones de $\text{PM}_{2.5}$ en Cartago se encuentran entre `5.9` y `79.4` $\mu\text{g/m}^3$. Un valor de `70100.0` corresponde exactamente a **$70.1\ \mu\text{g/m}^3$ expresado en nanogramos por metro cúbico ($\text{ng/m}^3$)**, es decir, multiplicado por un factor de $1000$ ($1\ \mu\text{g/m}^3 = 1000\text{ ng/m}^3$). Al convertirlo a `70.1` $\mu\text{g/m}^3$, el registro guarda total coherencia física con su etiqueta `alerta_calidad = 1` y con registros similares de la estación Universidad (como `M059` con `74.0` $\mu\text{g/m}^3$, viento `7.1` $\text{m/s}$ y `alerta_calidad = 1`).

---

### Resumen del Dataset Antes y Después de la Limpieza

| Métrica | Antes (`grupo_05.csv`) | Después (`grupo_05_limpio.csv`) |
| :--- | :---: | :---: |
| **Total de filas (registros)** | **84** | **77** |
| **Filas duplicadas** | 4 | 0 |
| **Valores nulos en `viento_m_s`** | 3 | 0 |
| **Valores con coma decimal en `viento_m_s`** | 3 (`str`) | 0 (`float64`) |
| **Valores con unidad errónea en `pm25_ugm3`** | 1 (`70100.0`) | 0 (corregido a `70.1`) |
| **Registros Clase `0` (`alerta_calidad = 0`, sin alerta)** | 47 | **42** ($54.55\%$) |
| **Registros Clase `1` (`alerta_calidad = 1`, con alerta)** | 37 | **35** ($45.45\%$) |

---

### Pregunta Clave – Tarea 3

> **¿Qué valor le pareció más sospechoso? Calcular la media de esa columna antes y después de corregirlo y explicar cómo habría afectado el escalado del perceptrón si no se hubiera corregido.**
>
> - **Valor más sospechoso:** El valor **`pm25_ugm3 = 70100.0`** en el registro **`M075`** (estación Universidad), que es mil veces superior al comportamiento real de la variable (`5.9` a `79.4` $\mu\text{g/m}^3$).
> - **Media de `pm25_ugm3` ANTES de corregirlo:**
>   - Sobre el archivo crudo (84 filas): **`875.00` $\mu\text{g/m}^3$** (desviación estándar = `7644.09` $\mu\text{g/m}^3$).
>   - Sobre las 77 filas válidas antes de corregir `M075`: **`950.78` $\mu\text{g/m}^3$** (desviación estándar = `7983.79` $\mu\text{g/m}^3$).
> - **Media de `pm25_ugm3` DESPUÉS de corregirlo (`70100.0` $\rightarrow$ `70.1` $\mu\text{g/m}^3$):**
>   - Sobre el archivo limpio final (77 filas): **`41.30` $\mu\text{g/m}^3$** (`41.2974` $\mu\text{g/m}^3$, con desviación estándar = **`19.59` $\mu\text{g/m}^3$**). *(Nota: si se hubiera eliminado la fila quedando 76 registros, la media sería `40.92` $\mu\text{g/m}^3$).*
> - **Efecto sobre el escalado del perceptrón si NO se hubiera corregido:**  
>   La estandarización Z-score calcula $z_1 = \frac{x_1 - \mu_1}{\sigma_1}$. Sin corregir `70100.0`, la media se dispara a **`950.78`** y la desviación estándar a **`7983.79`**. Como consecuencia:
>   1. **Colapso de varianza en los datos reales:** Las 76 mediciones normales (entre `5.9` y `79.4` $\mu\text{g/m}^3$) quedarían comprimidas en un intervalo minúsculo de valores estandarizados entre $z_1 = -0.118$ y $z_1 = -0.109$ (una diferencia de apenas $0.009$ unidades entre el aire más limpio y el más contaminado), mientras que `M075` tendría $z_1 = +8.66$.
>   2. **Degradación del aprendizaje:** Durante el descenso del gradiente ($dw = \frac{1}{m} X^T (\hat{y} - y)$), el único punto extremo ($z_1 = +8.66$) dominaría la derivada parcial respecto a $w_1$, impidiendo que el perceptrón distinga el umbral real de $\text{PM}_{2.5}$ para las demás 76 mediciones y reduciendo drásticamente la exactitud del clasificador.
