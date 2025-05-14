import pandas as pd
import psycopg2
from psycopg2 import sql
from tqdm import tqdm
import os
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

def get_connection():
    """Establece conexión a la base de datos PostgreSQL."""
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def upsert_empresas(filepath):
    """Carga o actualiza la tabla empresas."""
    df = pd.read_csv(filepath)
    
    conn = get_connection()
    cursor = conn.cursor()

    insert_query = """
        INSERT INTO empresas (ticker, name, sector, industry)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (ticker) DO UPDATE
        SET name = EXCLUDED.name,
            sector = EXCLUDED.sector,
            industry = EXCLUDED.industry;
    """

    print("\n🏢 Cargando tabla de EMPRESAS...")
    for _, row in tqdm(df.iterrows(), total=len(df)):
        cursor.execute(insert_query, (
            row['Ticker'], row['Name'], row['Sector'], row['Industry']
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Empresas: {len(df)} registros insertados/actualizados.")

def upsert_precios_historicos(filepath):
    """Carga o actualiza precios históricos (solo los nuevos)."""
    df = pd.read_csv(filepath)
    df['Date'] = pd.to_datetime(df['Date'])

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(date) FROM precios_historicos;")
    max_date_db = cursor.fetchone()[0]

    if max_date_db is not None:
        df = df[df['Date'] > pd.to_datetime(max_date_db)]

    if df.empty:
        print("ℹ️ No hay nuevos precios históricos para cargar.")
        conn.close()
        return

    insert_query = """
        INSERT INTO precios_historicos (date, ticker, open, high, low, close, volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (date, ticker) DO NOTHING;
    """

    print("\n📈 Cargando tabla de PRECIOS HISTORICOS...")
    for _, row in tqdm(df.iterrows(), total=len(df)):
        cursor.execute(insert_query, (
            row['Date'], row['Ticker'], row['Open'], row['High'],
            row['Low'], row['Close'], row['Volume']
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Precios históricos: {len(df)} registros insertados.")

def upsert_fundamentales(filepath):
    """Carga o actualiza los datos fundamentales."""
    df = pd.read_csv(filepath)
    
    conn = get_connection()
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO indicadores_fundamentales (ticker, per, roe, eps_growth_yoy, deuda_patrimonio,
                                           margen_neto, dividend_yield, market_cap, ranking_marketcap, acciones_circulacion)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (ticker) DO UPDATE SET
        per = EXCLUDED.per,
        roe = EXCLUDED.roe,
        eps_growth_yoy = EXCLUDED.eps_growth_yoy,
        deuda_patrimonio = EXCLUDED.deuda_patrimonio,
        margen_neto = EXCLUDED.margen_neto,
        dividend_yield = EXCLUDED.dividend_yield,
        market_cap = EXCLUDED.market_cap,
        ranking_marketcap = EXCLUDED.ranking_marketcap,
        acciones_circulacion = EXCLUDED.acciones_circulacion;
    """
    print("\n📊 Cargando tabla de FUNDAMENTALES...")
    for _, row in tqdm(df.iterrows(), total=len(df)):
        cursor.execute(insert_query, (
            row['Ticker'], row['PER'], row['ROE'], row['EPS Growth YoY'],
            row['Deuda/Patrimonio'], row['Margen Neto'], row['Dividend Yield'],
            row['Market Cap'], row['Ranking MarketCap'], row['Acciones en Circulación']
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Fundamentales: {len(df)} registros actualizados/insertados.")

def upsert_indicadores_tecnicos(csv_path):
    """Carga incremental de indicadores técnicos incluyendo Fibonacci."""
    conn = get_connection()
    cursor = conn.cursor()

    df = pd.read_csv(csv_path)
    df['Date'] = pd.to_datetime(df['Date'])

    cursor.execute("SELECT MAX(date) FROM indicadores_tecnicos;")
    max_date_db = cursor.fetchone()[0]
    
    if max_date_db:
        max_date_db = pd.to_datetime(max_date_db)
        df = df[df['Date'] > max_date_db]

    if df.empty:
        print("ℹ️ No hay nuevos indicadores técnicos para cargar.")
        conn.close()
        return

    print("📈 Cargando indicadores técnicos...")
    for _, row in tqdm(df.iterrows(), total=len(df)):
        insert_query = """
            INSERT INTO indicadores_tecnicos (
                date, ticker, close,
                sma_20, sma_50, ema_20, rsi_14,
                macd, macd_signal, macd_hist, atr_14, obv,
                bb_middle, bb_upper, bb_lower, volatility_20,
                fib_0_0, fib_23_6, fib_38_2, fib_50_0, fib_61_8, fib_100,
                nivel_fib_cercano, estado_fibonacci
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (date, ticker) DO UPDATE SET
                close = EXCLUDED.close,
                sma_20 = EXCLUDED.sma_20,
                sma_50 = EXCLUDED.sma_50,
                ema_20 = EXCLUDED.ema_20,
                rsi_14 = EXCLUDED.rsi_14,
                macd = EXCLUDED.macd,
                macd_signal = EXCLUDED.macd_signal,
                macd_hist = EXCLUDED.macd_hist,
                atr_14 = EXCLUDED.atr_14,
                obv = EXCLUDED.obv,
                bb_middle = EXCLUDED.bb_middle,
                bb_upper = EXCLUDED.bb_upper,
                bb_lower = EXCLUDED.bb_lower,
                volatility_20 = EXCLUDED.volatility_20,
                fib_0_0 = EXCLUDED.fib_0_0,
                fib_23_6 = EXCLUDED.fib_23_6,
                fib_38_2 = EXCLUDED.fib_38_2,
                fib_50_0 = EXCLUDED.fib_50_0,
                fib_61_8 = EXCLUDED.fib_61_8,
                fib_100 = EXCLUDED.fib_100,
                nivel_fib_cercano = EXCLUDED.nivel_fib_cercano,
                estado_fibonacci = EXCLUDED.estado_fibonacci;
        """
        cursor.execute(insert_query, (
            row['Date'], row['Ticker'], row['Close'],
            row['SMA_20'], row['SMA_50'], row['EMA_20'], row['RSI_14'],
            row['MACD'], row['MACD_Signal'], row['MACD_Hist'],
            row['ATR_14'], row['OBV'],
            row['BB_Middle'], row['BB_Upper'], row['BB_Lower'], row['Volatility_20'],
            row['Fib_0.0%'], row['Fib_23.6%'], row['Fib_38.2%'], row['Fib_50.0%'], row['Fib_61.8%'], row['Fib_100%'],
            row['Nivel_Fib_Cercano'], row['Estado_Fibonacci']
        ))

    conn.commit()
    conn.close()
    print(f"✅ Indicadores técnicos cargados correctamente ({len(df)} registros nuevos).")


def upsert_resumen_inversion(csv_path):
    """Carga incremental de resumen de inversión actualizado (incluyendo Estado_Fibonacci correctamente)."""
    conn = get_connection()
    cursor = conn.cursor()

    df = pd.read_csv(csv_path)

    print("🧠 Cargando resumen de inversión...")
    for _, row in tqdm(df.iterrows(), total=len(df)):
        insert_query = """
            INSERT INTO resumen_inversion (
                ticker, pct_tecnico_buy, pct_fundamental_buy, decision_final,
                estado_bollingerbands, sma_vs_ema, macd, rsi, per, roe, 
                eps_growth_yoy, deuda_patrimonio, estado_fibonacci
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (ticker) DO UPDATE SET
                pct_tecnico_buy = EXCLUDED.pct_tecnico_buy,
                pct_fundamental_buy = EXCLUDED.pct_fundamental_buy,
                decision_final = EXCLUDED.decision_final,
                estado_bollingerbands = EXCLUDED.estado_bollingerbands,
                sma_vs_ema = EXCLUDED.sma_vs_ema,
                macd = EXCLUDED.macd,
                rsi = EXCLUDED.rsi,
                per = EXCLUDED.per,
                roe = EXCLUDED.roe,
                eps_growth_yoy = EXCLUDED.eps_growth_yoy,
                deuda_patrimonio = EXCLUDED.deuda_patrimonio,
                estado_fibonacci = EXCLUDED.estado_fibonacci;
        """
        cursor.execute(insert_query, (
            row['Ticker'],
            row['%_Tecnico_Buy'],
            row['%_Fundamental_Buy'],
            row['Decision_Final'],
            row.get('Estado_BollingerBands', None),
            row.get('SMA_vs_EMA', None),
            row.get('MACD', None),
            row.get('RSI', None),
            row.get('PER', None),
            row.get('ROE', None),
            row.get('EPS Growth YoY', None),
            row.get('Deuda/Patrimonio', None),
            row.get('Estado_Fibonacci', None)
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Resumen de inversión cargado correctamente ({len(df)} registros nuevos).")

def upsert_precios_variaciones(csv_path):
    """Carga incremental de variaciones de precios."""
    conn = get_connection()
    cursor = conn.cursor()

    df = pd.read_csv(csv_path)
    df['Date'] = pd.to_datetime(df['Date'])

    cursor.execute("SELECT MAX(date) FROM precios_variaciones;")
    max_date_db = cursor.fetchone()[0]
    
    if max_date_db:
        max_date_db = pd.to_datetime(max_date_db)
        df = df[df['Date'] > max_date_db]

    if df.empty:
        print("ℹ️ No hay nuevas variaciones de precios para cargar.")
        conn.close()
        return

    print("📈 Cargando nuevas variaciones de precios...")
    for _, row in tqdm(df.iterrows(), total=len(df)):
        insert_query = """
            INSERT INTO precios_variaciones (
                date, ticker, close,
                var_daily, var_weekly, var_monthly, var_annual, var_5y
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (date, ticker) DO UPDATE SET
                close = EXCLUDED.close,
                var_daily = EXCLUDED.var_daily,
                var_weekly = EXCLUDED.var_weekly,
                var_monthly = EXCLUDED.var_monthly,
                var_annual = EXCLUDED.var_annual,
                var_5y = EXCLUDED.var_5y
            ;
        """
        cursor.execute(insert_query, (
            row['Date'], row['Ticker'], row['Close'],
            row['var_daily'], row['var_weekly'], row['var_monthly'],
            row['var_annual'], row['var_5y']
        ))

    conn.commit()
    conn.close()
    print(f"✅ Variaciones de precios cargadas correctamente ({len(df)} registros nuevos).")

if __name__ == "__main__":
    print("⚙️ Ejecutando pruebas de carga manual...")

    # Actualizá los paths según necesites
    DIR_READY = "../../data/clean_data/"

    upsert_empresas(DIR_READY + "empresas_ready.csv")
    upsert_precios_historicos(DIR_READY + "precios_historicos_ready.csv")
    upsert_fundamentales(DIR_READY + "indicadores_fundamentales_ready.csv")
    upsert_indicadores_tecnicos(DIR_READY + "indicadores_tecnicos_ready.csv")
    upsert_resumen_inversion(DIR_READY + "resumen_inversion_ready.csv")
    upsert_precios_variaciones(DIR_READY + "precios_variaciones_ready.csv")


    print("\n✅ ¡Carga de todas las tablas finalizada correctamente!")
