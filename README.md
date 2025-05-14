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

---

## 🧩 Estructura del Pipeline ETL

| Fase | Scripts | Descripción |
|:----|:--------|:------------|
| **Extracción** | `ext.py`, `ext_diario.py` | Descarga inicial y actualización diaria de datos desde Yahoo Finance y Wikipedia. |
| **Transformación** | `transform.py` |  Limpieza de datos y cálculo de indicadores técnicos y fundamentales. |
| **Carga** | `load.py` | Inserción incremental en PostgreSQL, controlando duplicados y actualizaciones. |
| **Orquestación** | `main.py` | Automatización completa del proceso ETL. |

---

## 📊 Variables de Interés

- **Históricos**: Open, High, Low, Close, Volume.  
- **Fundamentales**: PER, ROE, EPS Growth, Deuda/Patrimonio, Market Cap, Dividend Yield, Sector, Industria.  
- **Técnicos**:  
  - **Media Móvil Simple (SMA)**  
  - **Media Móvil Exponencial (EMA)**  
  - **Relative Strength Index (RSI)**  
  - **MACD**  
  - **Bollinger Bands**  
  - **Average True Range (ATR)**  
  - **On-Balance Volume (OBV)**  
  - **Volatilidad Histórica**  
  - **Niveles de Fibonacci**  

---

## 📈 Análisis Exploratorio de Datos (EDA)

El análisis exploratorio permitió detectar:
- 🔍 Columnas con alta proporción de nulos (`EPS Growth YoY`, `Dividend Yield`).
- 🧮 Variables con sesgo como `PER` y `Market Cap`, ideales para transformaciones logarítmicas.
- 🔗 Fuertes correlaciones entre variables como `Market Cap` y `Dividend Yield`.
- 🧨 Outliers identificados con Z-score y boxplots.
- 📅 Comportamientos temporales y fechas clave (como marzo 2020).

### Recomendaciones:
- Usar mediana para imputaciones en lugar de la media.
- Realizar normalización y selección de features para modelado.
- Aprovechar patrones temporales en modelos predictivos o alertas.

---

## 🗃️ Datasets Finales

- **empresas_ready.csv**: Información básica (Ticker, Nombre, Sector, Industria).
- **precios_historicos_ready.csv**: Precios diarios (Open, High, Low, Close, Volume).
- **indicadores_fundamentales_ready.csv**: PER, ROE, Deuda/Patrimonio, Margen Neto, etc.
- **indicadores_tecnicos_ready.csv**: SMA, EMA, RSI, MACD, ATR, OBV, Volatilidad, Bollinger Bands y niveles de Fibonacci.
- **precios_variacion_ready.csv**: Calculo de variaciones diarias, semanal, mensual, anual y cada 5 años.
- **resumen_inversion.csv**: Decision Final de compra o venta para cada indicador técnico y fundamental.

---

## 🛠️ Tecnologías Utilizadas

| Herramienta | Propósito |
|:------------|:----------|
| **Python 3.12** | Desarrollo del pipeline ETL. |
| **PostgreSQL** | Base de datos relacional. |
| **DBeaver** | Administración de la base de datos. |
| **Power BI (futuro)** | Visualización de dashboards. |
| **GitHub** | Control de versiones. |
| **Principales librerías Python**: | `pandas`, `numpy`, `yfinance`, `psycopg2`, `tqdm`, `python-dotenv`. |

---

## 🌎 Fuente de Datos

- **Yahoo Finance** (`yfinance`):  
  - Precios de apertura, cierre, máximo, mínimo y volumen.
  - Datos fundamentales básicos (PER, EPS, Market Cap, etc.).
  - Datos ajustados por dividendos y splits.

- **Wikipedia**:  
  - Lista actualizada del S&P 500 (símbolos, nombres, sector, industria).

---

## 🏗️ Estado del Proyecto

✅ Extracción masiva inicial completada.  
✅ Actualización diaria implementada.  
✅ Base de datos PostgreSQL funcional.  
✅ Indicadores técnicos y fundamentales calculados.  
✅ EDA completo documentado y visualizado.  
🚀 Próximo paso: dashboards y modelos predictivos.

---

## 📌 Próximos Desarrollos

- Construcción de dashboards interactivos en Power BI para análisis visual.

---

## 🤝 Colaboración

Cualquier sugerencia o colaboración para expandir este proyecto es bienvenida. ¡A construir herramientas financieras accesibles para todos! 🚀