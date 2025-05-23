# 📈 Proyecto Final: Análisis de Acciones del NYSE

---

## 🚀 Descripción General

Este proyecto implementa un pipeline ETL (Extracción, Transformación y Carga) completo para construir una base de datos actualizada diariamente con información sobre las 500 empresas de mayor capitalización bursátil del NYSE (S&P 500).

Permite:
- Descargar y limpiar datos de precios históricos y fundamentales.
- Calcular indicadores técnicos y fundamentales clave.
- Almacenar todo en PostgreSQL para su posterior análisis y modelado.
- Generar reportes y dashboards para apoyar decisiones de inversión.
- Realizar Análisis Exploratorio de Datos (EDA) detallado para obtener insights valiosos.
- Generar señales automáticas de compra, venta o mantener combinando análisis técnico y fundamental.
- Visualizar el ecosistema en dashboards interactivos con Power BI.

---

## 🎯 Objetivos

### Objetivos Mínimos:
- Extracción de datos históricos y fundamentales usando Yahoo Finance (`yfinance`).
- Transformación, limpieza y cálculo de indicadores técnicos (SMA, EMA, RSI, MACD, Bollinger Bands, ATR, OBV, Volatilidad, Fibonacci) y fundamentales (PER, ROE, EPS Growth, Deuda/Patrimonio, Market Cap, Dividend Yield).
- Almacenamiento en base de datos relacional PostgreSQL.
- Análisis Exploratorio de Datos (EDA).
- Desarrollo de dashboards de visualización en Power BI.

### Objetivos Plus:
- Automatización diaria de la actualización de datos.
- Democratizar el acceso a datos financieros de calidad para pequeños inversores.
- Generación automática de recomendaciones de inversión.
- Base para desarrollo futuro de modelos predictivos y aplicación web.

---

## 🧩 Estructura del Pipeline ETL

| Fase | Scripts | Descripción |
|:----|:--------|:------------|
| **Extracción** | `etl_01_ext.py`, `etl_02_ext_diario.py` | Descarga inicial y actualización diaria de datos desde Yahoo Finance y Wikipedia. |
| **Transformación** | `etl_03_transform.py` | Limpieza de datos y cálculo de indicadores técnicos y fundamentales. |
| **Carga** | `etl_04_load.py` | Inserción incremental en PostgreSQL, controlando duplicados y actualizaciones. |
| **Orquestación** | `main.py` | Automatización completa del proceso ETL. |

---

## 📊 Variables de Interés

- **Históricos**: Open, High, Low, Close, Volume.  
- **Fundamentales**: PER, ROE, EPS Growth, Deuda/Patrimonio, Market Cap, Dividend Yield, Sector, Industria.  
- **Técnicos**:  
  - Media Móvil Simple (SMA)  
  - Media Móvil Exponencial (EMA)  
  - Relative Strength Index (RSI)  
  - MACD  
  - Bollinger Bands  
  - Average True Range (ATR)  
  - On-Balance Volume (OBV)  
  - Volatilidad Histórica  
  - Niveles de Fibonacci  

---

## 📈 Análisis Exploratorio de Datos (EDA)

El análisis exploratorio permitió detectar:
- Columnas con alta proporción de nulos (`EPS Growth YoY`, `Dividend Yield`).
- Variables con sesgo como `PER` y `Market Cap`, ideales para transformaciones logarítmicas.
- Fuertes correlaciones entre variables como `Market Cap` y `Dividend Yield`.
- Outliers identificados con Z-score y boxplots.
- Comportamientos temporales y fechas clave (como marzo 2020).

### Recomendaciones:
- Usar mediana para imputaciones en lugar de la media.
- Realizar normalización y selección de features para modelado.
- Aprovechar patrones temporales en modelos predictivos o alertas.

---
## 📁 Estructura Propuesta del Repositorio
Proyecto_Final/
├── 📁 consultas_SQL/                       # Consultas SQL organizadas por tipo y propósito
│   ├── Carga_tablas.sql                   # Script para carga inicial de tablas
│   ├── consultas_APPL.sql                 # Consultas específicas para Apple
│   ├── consultas_APPL_AVANZADAS.sql       # Consultas más complejas sobre Apple
│   └── consultas_APPL_PRO.sql             # Consultas profesionales/personalizadas
│
├── 📁 dashboards/                         # Dashboards interactivos (Power BI)
│   └── dashboard.pbix                     # Dashboard principal
│
├── 📁 documentacion/                      # Documentación interna y técnica
│   ├── 01.Analisis_acciones_NYSE.md       # Visión general del análisis
│   ├── 02.Documentación_ETL.md            # Explicación técnica del proceso ETL
│   ├── 03.Documetacion_Informe_EDA.md     # Documento sobre análisis exploratorio
│   └── esquema_bbdd.png                   # Esquema visual de la base de datos
│
├── 📁 entregables/                        # Documentos formales para presentación
│   ├── 01.Definicion_Proyecto_Analisis_Acciones.md
│   ├── 02.Documentacion_ETL_Proyecto_Final.md
│   ├── 03.Informe_EDA_Completo_Resultados.md
│   └── Trabajo_Final_DataAnalyticsHackio.md
│
├── 📁 notebooks/                          # Jupyter notebooks
│   ├── 📁 clean/                          # Notebooks ordenados y definitivos
│   │   └── EDA.ipynb                      # Exploración de datos limpia
│   └── 📁 src/                            # Funciones auxiliares para notebooks
│       └── soporte_query.py
│
├── 📁 src/etl/                            # Scripts del pipeline ETL
│   ├── etl_01_ext.py                     # Extracción inicial
│   ├── etl_02_ext_diario.py              # Actualización diaria
│   ├── etl_03_transform.py               # Transformación de datos
│   ├── etl_04_load.py                    # Carga a PostgreSQL
│   └── main.py                           # Orquestador del proceso completo
│
├── .gitattributes
├── .gitignore                            # Archivos/carpetas ignorados por Git
└── README.md                             # Documentación principal del proyecto


## 🗃️ Datasets Finales

- **empresas_ready.csv**: Información básica (Ticker, Nombre, Sector, Industria).
- **precios_historicos_ready.csv**: Precios diarios (Open, High, Low, Close, Volume).
- **indicadores_fundamentales_ready.csv**: PER, ROE, Deuda/Patrimonio, Margen Neto, etc.
- **indicadores_tecnicos_ready.csv**: SMA, EMA, RSI, MACD, ATR, OBV, Volatilidad, Bollinger Bands y niveles de Fibonacci.
- **precios_variacion_ready.csv**: Calculo de variaciones diarias, semanal, mensual, anual y cada 5 años.
- **resumen_inversion.csv**: Decision Final de compra o venta para cada indicador técnico y fundamental.

---

## 📊 Dashboards

Se desarrollaron dos dashboards interactivos en Power BI:

### Dashboard General
- Ranking de empresas por capitalización.
- Distribución de señales de inversión.
- Análisis histórico y sectorial.
- Mapas interactivos por sector e industria.

### Dashboard Individual
- KPIs fundamentales por empresa.
- Indicadores técnicos (MACD, RSI, ATR, Fibonacci).
- Recomendaciones personalizadas (compra, venta, mantener).

---

## 🛠️ Tecnologías Utilizadas

| Herramienta | Propósito |
|:------------|:----------|
| Python 3.12 | Desarrollo del pipeline ETL. |
| PostgreSQL | Base de datos relacional. |
| DBeaver | Administración de la base de datos. |
| Power BI | Visualización de dashboards. |
| GitHub | Control de versiones. |
| Librerías | `pandas`, `numpy`, `yfinance`, `psycopg2`, `tqdm`, `python-dotenv` |

---

## 🌎 Fuente de Datos

- **Yahoo Finance** (`yfinance`)
- **Wikipedia** (Tickers S&P 500)

---

## 🏗️ Estado del Proyecto

✅ Extracción masiva inicial completada.  
✅ Actualización diaria implementada.  
✅ Base de datos PostgreSQL funcional.  
✅ Indicadores técnicos y fundamentales calculados.  
✅ EDA completo documentado y visualizado.  
✅ Generación de señales de inversión implementada.  
✅ Dashboards.

---

## 📌 Próximos Desarrollos

- Modelos de predicción con ML/DL.
- Alertas automáticas de señales.
- App web o móvil para usuarios finales.
- Backtesting de estrategias.
- Expansión a otras bolsas (BYMA, Bovespa, etc.).

---

## 🤝 Colaboración

Cualquier sugerencia o colaboración para expandir este proyecto es bienvenida. ¡A construir herramientas financieras accesibles para todos! 🚀