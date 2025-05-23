# Resumen Ejecutivo

El mercado bursátil es, por naturaleza, volátil y sensible a múltiples factores externos, como eventos económicos, políticos y financieros. En este contexto, la toma de decisiones basadas en datos se vuelve esencial para mitigar riesgos y maximizar oportunidades. Sin embargo, la falta de herramientas asequibles y usables limita a muchos actores del mercado a operar de forma intuitiva o con información incompleta.

El presente proyecto tiene como objetivo desarrollar una solución integral y accesible para el análisis del mercado accionario del NYSE, enfocándose especialmente en pequeños inversionistas y fondos independientes que no cuentan con acceso a plataformas profesionales de alto costo o con requerimientos técnicos complejos.

Como respuesta a esta problemática, el proyecto propone una arquitectura de análisis basada en datos que permite:

- Recolectar información histórica y fundamental de empresas mediante la API de Yahoo Finance.
- Procesar esta información mediante un pipeline ETL automatizado.
- Calcular indicadores técnicos como RSI, MACD, Bandas de Bollinger, ATR, OBV y niveles de Fibonacci.
- Calcular métricas fundamentales como PER, ROE, crecimiento de EPS, deuda/patrimonio y margen neto.
- Integrar los datos en una base PostgreSQL estructurada y optimizada para consultas analíticas.
- Generar señales automáticas de inversión (compra, venta o mantener) basadas en una lógica combinada.
- Visualizar todo el ecosistema de datos en dashboards interactivos en Power BI, con enfoque por empresa.

## Fases del Proyecto

1. Fase inicial: desarrollo del pipeline ETL, diseño de base de datos y carga masiva de datos históricos.
2. Fase continua: automatización de las actualizaciones diarias y cálculo de señales de inversión en tiempo real.

### Logros Alcanzados

- Creación de la tabla `resumen_inversion`.
- Dashboards accesibles con KPIs clave y análisis técnico/fundamental.
- Estandarización y normalización de datos financieros.

El sistema fue desarrollado en Python (Pandas, NumPy, yfinance), PostgreSQL y visualizado con Power BI. Todo el código está versionado en GitHub.

### Futuro

- Modelos predictivos, alertas automáticas e interfaz web/móvil.

# Metodología

## 2.1 Pipeline ETL

### Extracción

- Tickers desde Wikipedia.
- Datos históricos y fundamentales con `yfinance`.
- Estrategia doble: carga inicial masiva y actualización incremental.

### Transformación

- Limpieza y normalización.
- Indicadores técnicos (SMA, EMA, RSI, MACD, Bollinger, ATR, OBV, Volatilidad).
- Categorización automática con Fibonacci.
- Tabla `resumen_inversion`.

### Carga

- Datos a PostgreSQL.
- Tablas: empresas, precios históricos, indicadores técnicos/fundamentales, resumen de inversión.
- Scripts con `psycopg2` y lógica `UPSERT`.

### Orquestación

- Script maestro `main.py`.
- Sistema reproducible de punta a punta.

## 2.2 Herramientas

| Fase | Herramienta |
|------|-------------|
| Extracción de Datos | `yfinance` |
| Transformación y Análisis | Python (Pandas, NumPy) |
| Almacenamiento | PostgreSQL |
| Visualización | Power BI |
| Control de Versiones | GitHub |

# Resultados

## 3.1 Exploración de Datos

- Valores nulos en EPS Growth YoY y Dividend Yield.
- Outliers en PER, ROE y Market Cap.
- Correlaciones fuertes entre variables clave.
- Comportamientos sectoriales diferenciados.

## 3.2 Sistema de Recomendación

- Clasificación: COMPRAR (210), VENDER (171), MANTENER (119).

## 3.3 Dashboards Interactivos

### Dashboard General

- Ranking de empresas.
- Distribución de decisiones.
- Visualización histórica y sectorial.
- Paneles por señales.

### Dashboard Individual por Empresa

- KPIs fundamentales.
- Evolución de precios con niveles técnicos.
- Indicadores técnicos.
- Recomendación textual.

# Impacto de Negocio

## 4.1 Democratización del Análisis Financiero

Uso de herramientas open source para inversionistas individuales y PYMEs.

## 4.2 Soporte a la Toma de Decisiones

Sistema objetivo, reduce subjetividad y riesgo.

## 4.3 Visibilidad Estratégica

Top-down desde el panorama global y bottom-up para análisis detallado.

## 4.4 Escalabilidad y Mantenimiento

Pipeline automatizable, modular y adaptable.

## 4.5 Aplicabilidad Comercial

Potencial para SaaS, herramienta de asesoría o app de inversión.

# Conclusiones y Próximos Pasos

## Principales Aprendizajes

- Limpieza de datos, análisis técnico + fundamental, automatización, visualización efectiva.

## Próximos Pasos

- Modelos predictivos.
- Nuevas APIs (Alpaca, Polygon.io, etc.).
- App web/móvil.
- Backtesting.
- Internacionalización (BYMA, Bovespa, etc.).

# Anexo A – Glosario de Indicadores

## Indicadores Técnicos

| Indicador | Descripción | Interpretación |
|----------|-------------|----------------|
| SMA | Promedio del precio de cierre | Cruce de medias indica tendencia |
| EMA | Promedio ponderado | Reacciona más rápido |
| RSI | Índice de fuerza relativa | RSI > 70 = sobrecompra |
| MACD | Diferencia entre EMAs | Cruce = cambio de tendencia |
| ATR | Volatilidad del precio | Mayor ATR = mayor riesgo |
| OBV | Precio con volumen acumulado | Divergencias anticipan cambios |
| Bandas de Bollinger | SMA ± 2 desviaciones estándar | Banda superior = sobrecompra |
| Volatilidad 20 | STD de cierre 20 días | Proxy de riesgo |
| Fibonacci | Retrocesos porcentuales | Soportes y resistencias |

## Indicadores Fundamentales

| Indicador | Descripción | Interpretación |
|----------|-------------|----------------|
| PER | Precio/Ganancia | Bajo = infravalorada |
| ROE | Rentabilidad del patrimonio | Mayor = más eficiencia |
| EPS Growth | Crecimiento anual | Refleja crecimiento |
| Deuda/Patrimonio | Apalancamiento | Alto = riesgoso |
| Margen Neto | Rentabilidad neta | Más alto = más rentable |
| Dividend Yield | Dividendo/precio | Interesante para renta |
| Market Cap | Valor de mercado | Clasificación por tamaño |

# Anexo B – Documentación Técnica

## `etl_01_ext.py`

- Extrae empresas del S&P 500 y datos de Yahoo Finance.
- Funciones: `extract_top_500_marketcap()`, `descargar_datos_historicos()`, `extract_fundamentals_indicators()`.

## `etl_02_ext_diario.py`

- Descarga incremental de precios y fundamentales.

## `etl_03_transform.py`

- Limpieza, normalización y cálculo de indicadores.
- Funciones: `calcular_rsi()`, `calcular_macd()`, `calcular_resumen_inversion()`.

## `etl_04_load.py`

- Carga de datos a PostgreSQL.
- Funciones: `upsert_*` con lógica `ON CONFLICT DO UPDATE`.

## Infraestructura

- Orquestación vía `main.py`.
- Compatible con `cron` o `Airflow`.

> Todos los scripts están versionados y documentados en GitHub.