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
