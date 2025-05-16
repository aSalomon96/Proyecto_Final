import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import missingno as msno
import seaborn as sns
from scipy import stats

import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

def get_connection():
    """
    Carga las variables de entorno desde un archivo `.env` y asigna los valores a constantes utilizadas
    para la conexión a una base de datos.

    Esta técnica permite mantener las credenciales y parámetros sensibles fuera del código fuente,
    siguiendo buenas prácticas de seguridad y portabilidad.

    Variables esperadas en el archivo .env:
        - DB_NAME: Nombre de la base de datos.
        - DB_USER: Usuario con permisos de acceso.
        - DB_PASSWORD: Contraseña del usuario.
        - DB_HOST: Dirección del host donde corre la base de datos.
        - DB_PORT: Puerto de conexión a la base de datos.
    """
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def get_market_cap_df():
    query = """
    SELECT
        ph.ticker,
        ph.date,
        ph.close,
        f.acciones_circulacion,
        ph.close * f.acciones_circulacion AS market_cap
    FROM
        precios_historicos ph
    LEFT JOIN
        indicadores_fundamentales f
        ON ph.ticker = f.ticker
    WHERE
        ph.ticker IN ('AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOG');
    """
    conn = get_connection()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df



# funcion para obtener las variaciones diarias de precios en la base de datos
def get_variaciones_df():
    query = """
    SELECT ticker, date, var_daily
    FROM precios_variaciones
    WHERE ticker IN ('AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOG');
    """
    conn = get_connection()
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Asegurar formato de fecha
    df['date'] = pd.to_datetime(df['date'])
    return df


def get_fundamentales_df():
    query = """
    SELECT *
    FROM indicadores_fundamentales;
    """
    conn = get_connection()
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df

def get_resumen_inversion_df():
    query = """
    SELECT *
    FROM resumen_inversion;
    """
    conn = get_connection()
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df

def get_fundamentales_sector_df():
    query = """
    SELECT
        f.ticker AS ticker,
        f.per,
        f.roe,
        f.eps_growth_yoy,
        f.deuda_patrimonio,
        f.margen_neto,
        f.dividend_yield,
        f.market_cap,
        f.ranking_marketcap,
        f.acciones_circulacion,
        e.sector,
        e.industry
FROM
    indicadores_fundamentales f
LEFT JOIN
    empresas e ON f.ticker = e.ticker;
    """
    conn = get_connection()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_promedios_var_annual_por_sector():
    query = """
    SELECT
        e.sector,
        AVG(pv.var_annual::FLOAT) AS promedio_var_annual
    FROM
        precios_variaciones pv
    JOIN
        empresas e ON pv.ticker = e.ticker
    WHERE
        pv.var_annual IS NOT NULL
        AND pv.var_annual != 'NaN' -- <== EXCLUYE strings tipo 'NaN'
        AND pv.date >= '2008-01-03'
        AND e.sector IS NOT NULL
    GROUP BY
        e.sector
    ORDER BY
        promedio_var_annual DESC;
    """
    conn = get_connection()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_indicadores_tecnicos_filtrados():
    query = """
    SELECT
        ticker,
        rsi_14,
        volatility_20
    FROM
        indicadores_tecnicos
    WHERE
        rsi_14 IS NOT NULL
        AND volatility_20 IS NOT NULL;
    """
    conn = get_connection()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_volatilidad_por_sector():
    query = """
    SELECT
        e.sector,
        AVG(pv.var_annual::FLOAT) AS promedio_var_annual
    FROM
        precios_variaciones pv
    JOIN
        empresas e ON pv.ticker = e.ticker
    WHERE
        pv.var_annual IS NOT NULL
        AND pv.var_annual != 'NaN' -- <== EXCLUYE strings tipo 'NaN'
        AND e.sector IS NOT NULL
    GROUP BY
        e.sector
    ORDER BY
        promedio_var_annual DESC;
    """
    conn = get_connection()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_decisiones_por_sector():
    query = """
    SELECT
        e.sector,
        r.decision_final,
        COUNT(*) AS cantidad
    FROM
        resumen_inversion r
    JOIN
        empresas e ON r.ticker = e.ticker
    WHERE
        r.decision_final IN ('COMPRAR', 'VENDER')
        AND e.sector IS NOT NULL
    GROUP BY
        e.sector, r.decision_final
    ORDER BY
        cantidad DESC;
    """
    conn = get_connection()
    df_sectores_decision_final = pd.read_sql_query(query, conn)
    conn.close()
    return df_sectores_decision_final

def get_volumen_mensual_por_sector():
    query = """
    SELECT
        DATE_TRUNC('month', pv.date) AS mes,
        e.sector,
        AVG(pv.volume) AS volumen_promedio
    FROM
        precios_historicos pv
    JOIN
        empresas e ON pv.ticker = e.ticker
    WHERE
        pv.volume IS NOT NULL
        AND e.sector IS NOT NULL
        AND pv.date >= '2007-01-01'
    GROUP BY
        mes, e.sector
    ORDER BY
        mes, e.sector;
    """
    conn = get_connection()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_volatilidad_empresas_claves():
    tickers = ['AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOG']
    
    placeholders = ','.join(['%s'] * len(tickers))
    
    query = f"""
    SELECT 
        it.date,
        it.ticker,
        it.volatility_20,
        it.atr_14
    FROM indicadores_tecnicos it
    WHERE it.ticker IN ({placeholders})
      AND it.volatility_20 IS NOT NULL
      AND it.atr_14 IS NOT NULL
      And it.date >= '2017-01-01'
    ORDER BY it.date
    """

    conn = get_connection()
    df = pd.read_sql_query(query, conn, params=tickers)
    conn.close()
    return df


def get_rotacion_sectorial_trimestral():
    import pandas as pd

    query = """
    WITH market_cap_diario AS (
        SELECT 
            DATE_TRUNC('quarter', ph.date) AS trimestre,
            e.sector,
            (f.acciones_circulacion * ph.close) AS market_cap
        FROM precios_historicos ph
        JOIN empresas e ON ph.ticker = e.ticker
        JOIN indicadores_fundamentales f ON ph.ticker = f.ticker
        WHERE ph.close IS NOT NULL AND f.acciones_circulacion IS NOT NULL
    ),
    sector_trimestral AS (
        SELECT 
            trimestre,
            sector,
            AVG(market_cap) AS avg_sector_market_cap
        FROM market_cap_diario
        GROUP BY trimestre, sector
    ),
    total_trimestral AS (
        SELECT 
            trimestre,
            SUM(avg_sector_market_cap) AS total_market_cap
        FROM sector_trimestral
        GROUP BY trimestre
    )
    SELECT 
        s.trimestre,
        s.sector,
        s.avg_sector_market_cap,
        t.total_market_cap,
        s.avg_sector_market_cap / t.total_market_cap AS participacion
    FROM sector_trimestral s
    JOIN total_trimestral t ON s.trimestre = t.trimestre
    ORDER BY s.trimestre, s.sector;
    """

    conn = get_connection()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_retornos_anuales_por_sector():
    import pandas as pd

    query = """
    WITH precios_con_sector AS (
        SELECT 
            ph.date,
            ph.ticker,
            e.sector,
            ph.close,
            LAG(ph.close, 252) OVER (PARTITION BY ph.ticker ORDER BY ph.date) AS close_1y_ago
        FROM precios_historicos ph
        JOIN empresas e ON ph.ticker = e.ticker
    ),
    retornos_diarios AS (
        SELECT
            date,
            sector,
            (close - close_1y_ago) / NULLIF(close_1y_ago, 0) AS retorno_anual
        FROM precios_con_sector
        WHERE close IS NOT NULL AND close_1y_ago IS NOT NULL
    ),
    retornos_trimestrales AS (
        SELECT
            DATE_TRUNC('quarter', date) AS trimestre,
            sector,
            AVG(retorno_anual) AS retorno_prom_sector
        FROM retornos_diarios
        GROUP BY trimestre, sector
    )
    SELECT *
    FROM retornos_trimestrales
    ORDER BY trimestre, sector;
    """

    conn = get_connection()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def evaluar_efectividad_rsi():
    import pandas as pd

    query = """
    WITH rsi_señales AS (
        SELECT 
            it.ticker,
            it.date AS fecha_senal,
            ph1.close AS precio_senal,
            LEAD(ph1.close, 21) OVER (PARTITION BY it.ticker ORDER BY it.date) AS precio_21d_despues
        FROM indicadores_tecnicos it
        JOIN precios_historicos ph1 ON it.ticker = ph1.ticker AND it.date = ph1.date
        WHERE it.rsi_14 < 30
    ),
    retornos_senal AS (
        SELECT 
            fecha_senal,
            ticker,
            DATE_TRUNC('quarter', fecha_senal) AS trimestre,
            (precio_21d_despues - precio_senal) / NULLIF(precio_senal, 0) AS retorno_21d
        FROM rsi_señales
        WHERE precio_senal IS NOT NULL AND precio_21d_despues IS NOT NULL
    )
    SELECT 
        trimestre,
        COUNT(*) AS cantidad_senales,
        AVG(retorno_21d) AS retorno_promedio_post_senal
    FROM retornos_senal
    GROUP BY trimestre
    ORDER BY trimestre;
    """

    conn = get_connection()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def evaluar_efectividad_rsi_alto():
    import pandas as pd

    query = """
    WITH rsi_altos AS (
        SELECT 
            it.ticker,
            it.date AS fecha_senal,
            ph1.close AS precio_senal,
            LEAD(ph1.close, 21) OVER (PARTITION BY it.ticker ORDER BY it.date) AS precio_21d_despues
        FROM indicadores_tecnicos it
        JOIN precios_historicos ph1 ON it.ticker = ph1.ticker AND it.date = ph1.date
        WHERE it.rsi_14 > 70
    ),
    retornos_senal AS (
        SELECT 
            fecha_senal,
            ticker,
            DATE_TRUNC('quarter', fecha_senal) AS trimestre,
            (precio_21d_despues - precio_senal) / NULLIF(precio_senal, 0) AS retorno_21d
        FROM rsi_altos
        WHERE precio_senal IS NOT NULL AND precio_21d_despues IS NOT NULL
    )
    SELECT 
        trimestre,
        COUNT(*) AS cantidad_senales,
        AVG(retorno_21d) AS retorno_promedio_post_senal
    FROM retornos_senal
    GROUP BY trimestre
    ORDER BY trimestre;
    """

    conn = get_connection()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_sma_y_precios_empresas_clave():
    import pandas as pd

    tickers = ['AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOG']
    placeholders = ','.join(['%s'] * len(tickers))

    query = f"""
    SELECT 
        it.date,
        it.ticker,
        ph.close,
        it.sma_20,
        it.sma_50
    FROM indicadores_tecnicos it
    JOIN precios_historicos ph ON it.ticker = ph.ticker AND it.date = ph.date
    WHERE it.ticker IN ({placeholders})
      AND it.sma_20 IS NOT NULL
      AND it.sma_50 IS NOT NULL
      AND ph.close IS NOT NULL
      and ph.date >= '2018-01-01'
    ORDER BY it.ticker, it.date
    """

    conn = get_connection()
    df = pd.read_sql_query(query, conn, params=tickers)
    conn.close()
    return df

def get_precios_sectoriales():
    sectores = [
        'Technology',
        'Communication Services',
        'Consumer Cyclical',
        'Financial Services',
        'Consumer Defensive',
        'Energy'
    ]

    placeholders = ','.join(['%s'] * len(sectores))

    query = f"""
    SELECT 
        ph.date,
        e.sector,
        AVG(ph.close) AS precio_promedio
    FROM precios_historicos ph
    JOIN empresas e ON ph.ticker = e.ticker
    WHERE e.sector IN ({placeholders})
      AND ph.close IS NOT NULL
      and ph.date >= '2018-01-01'
    GROUP BY ph.date, e.sector
    ORDER BY ph.date
    """

    conn = get_connection()
    df = pd.read_sql_query(query, conn, params=sectores)
    conn.close()
    return df