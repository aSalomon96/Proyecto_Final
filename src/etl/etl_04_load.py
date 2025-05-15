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

def upsert_empresas(filepath):
    """
    Inserta o actualiza registros en la tabla `empresas` de una base de datos PostgreSQL a partir de un archivo CSV.

    Esta función realiza un *upsert* (insert or update) para cada fila del archivo especificado, 
    asegurando que si ya existe un `ticker`, se actualicen sus campos `name`, `sector` e `industry` 
    con los nuevos valores. Utiliza la cláusula `ON CONFLICT` de PostgreSQL para evitar duplicados.

    Args:
        filepath (str): Ruta al archivo CSV que contiene las columnas: 'Ticker', 'Name', 'Sector', 'Industry'.

    Returns:
        None: La función no devuelve ningún valor, pero actualiza la base de datos con los datos del archivo.

    Raises:
        FileNotFoundError: Si el archivo CSV no existe.
        psycopg2.DatabaseError: Si hay un error de conexión o ejecución de consulta SQL.
        KeyError: Si faltan columnas esperadas en el archivo.

    Requisitos:
        - La tabla `empresas` debe existir en la base de datos con los campos:
          `ticker` (clave primaria), `name`, `sector`, `industry`.
        - La función `get_connection()` debe devolver una conexión válida a la base de datos.
    """

    # Carga el archivo CSV como DataFrame
    df = pd.read_csv(filepath)

    # Establece la conexión a la base de datos y crea un cursor para ejecutar consultas
    conn = get_connection()
    cursor = conn.cursor()

    # Consulta SQL que realiza un UPSERT: inserta si no existe, actualiza si ya existe el ticker
    insert_query = """
        INSERT INTO empresas (ticker, name, sector, industry)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (ticker) DO UPDATE
        SET name = EXCLUDED.name,
            sector = EXCLUDED.sector,
            industry = EXCLUDED.industry;
    """

    # Mensaje informativo
    print("\n🏢 Cargando tabla de EMPRESAS...")

    # Itera sobre cada fila del DataFrame e inserta/actualiza en la base de datos
    for _, row in tqdm(df.iterrows(), total=len(df)):
        cursor.execute(insert_query, (
            row['Ticker'], row['Name'], row['Sector'], row['Industry']
        ))

    # Confirma los cambios en la base de datos
    conn.commit()

    # Cierra el cursor y la conexión
    cursor.close()
    conn.close()

    # Informa que el proceso fue exitoso
    print(f"✅ Empresas: {len(df)} registros insertados/actualizados.")

def upsert_precios_historicos(filepath):
    """
    Inserta nuevos registros de precios históricos en la base de datos, omitiendo los duplicados ya existentes.

    Esta función compara las fechas del archivo CSV con la última fecha disponible en la tabla 
    `precios_historicos` y carga únicamente los registros más recientes. Usa un `ON CONFLICT` para 
    evitar insertar filas duplicadas basadas en la combinación `(date, ticker)`.

    Args:
        filepath (str): Ruta al archivo CSV que contiene precios históricos con columnas:
                        'Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume'.

    Returns:
        None: La función no devuelve valores, pero actualiza la tabla `precios_historicos` en la base de datos.

    Raises:
        FileNotFoundError: Si el archivo CSV no existe.
        psycopg2.DatabaseError: Si ocurre un error durante la conexión o ejecución de SQL.
        KeyError: Si faltan columnas esperadas en el CSV.
        ValueError: Si la conversión de fechas falla.

    Requisitos:
        - La tabla `precios_historicos` debe tener una restricción de unicidad en (date, ticker).
        - La función `get_connection()` debe retornar una conexión válida a PostgreSQL.
    """
    df = pd.read_csv(filepath)
    df['Date'] = pd.to_datetime(df['Date'])

    conn = get_connection()
    cursor = conn.cursor()

    # Consulta la última fecha de precios ya registrada en la tabla
    cursor.execute("SELECT MAX(date) FROM precios_historicos;")
    max_date_db = cursor.fetchone()[0]

    # Si hay datos en la tabla, filtra solo los registros más nuevos
    if max_date_db is not None:
        df = df[df['Date'] > pd.to_datetime(max_date_db)]

    # Si no hay datos nuevos para insertar, termina el proceso
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
    """
    Inserta o actualiza los indicadores fundamentales de empresas en la base de datos.

    Esta función realiza un *upsert* (insertar o actualizar) en la tabla `indicadores_fundamentales` 
    utilizando como clave el `ticker`. Si ya existe, se actualizan los campos con los valores nuevos; 
    si no existe, se inserta como nuevo registro.

    Args:
        filepath (str): Ruta al archivo CSV que contiene las columnas:
            - 'Ticker'
            - 'PER'
            - 'ROE'
            - 'EPS Growth YoY'
            - 'Deuda/Patrimonio'
            - 'Margen Neto'
            - 'Dividend Yield'
            - 'Market Cap'
            - 'Ranking MarketCap'
            - 'Acciones en Circulación'

    Returns:
        None: La función no retorna valores, pero actualiza la base de datos con los datos del archivo.

    Raises:
        FileNotFoundError: Si el archivo CSV no existe.
        psycopg2.DatabaseError: Si ocurre un error al ejecutar la consulta SQL.
        KeyError: Si faltan columnas esperadas en el archivo.
        Exception: Para errores inesperados durante la ejecución.

    Requisitos:
        - La tabla `indicadores_fundamentales` debe existir con una restricción de unicidad sobre `ticker`.
        - La función `get_connection()` debe retornar una conexión activa a la base de datos.
    """
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
    """
    Inserta o actualiza indicadores técnicos en la base de datos de forma incremental,
    incluyendo medias móviles, RSI, MACD, ATR, OBV, Bandas de Bollinger y niveles de Fibonacci.

    Solo se insertan registros posteriores a la última fecha registrada en la tabla `indicadores_tecnicos`.
    En caso de conflicto por `(date, ticker)`, los datos existentes se actualizan.

    Args:
        csv_path (str): Ruta al archivo CSV que contiene los indicadores técnicos procesados. 
                        Debe incluir columnas como 'Date', 'Ticker', 'Close', 'RSI_14', 'MACD', 
                        'Fib_38.2%', 'Estado_Fibonacci', entre otras.

    Returns:
        None: La función no devuelve un valor explícito, pero actualiza la base de datos y 
              muestra por consola el número de registros insertados.

    Raises:
        FileNotFoundError: Si el archivo CSV no existe.
        psycopg2.DatabaseError: Si ocurre un error al ejecutar la consulta SQL.
        KeyError: Si faltan columnas necesarias en el DataFrame.
        Exception: Para cualquier otro error durante la ejecución del proceso.

    Requisitos:
        - La tabla `indicadores_tecnicos` debe tener una restricción de unicidad en `(date, ticker)`.
        - La función `get_connection()` debe retornar una conexión activa a la base de datos PostgreSQL.
    """
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
    """
    Inserta o actualiza de forma incremental el resumen de inversión por ticker en la base de datos.

    Esta función carga un archivo CSV con señales combinadas de análisis técnico y fundamental, 
    incluyendo el estado del indicador de Fibonacci, y lo sincroniza con la tabla `resumen_inversion`.
    Se utiliza un `ON CONFLICT` sobre `ticker` para actualizar los datos si ya existen.

    Args:
        csv_path (str): Ruta al archivo CSV que contiene el resumen de inversión generado por el análisis.

    Returns:
        None: La función no retorna un valor explícito, pero actualiza la base de datos y muestra un mensaje
              con la cantidad de registros insertados o actualizados.

    Raises:
        FileNotFoundError: Si el archivo CSV no existe.
        psycopg2.DatabaseError: Si ocurre un error de conexión o ejecución de SQL.
        KeyError: Si faltan columnas requeridas en el archivo.
        Exception: Para errores generales durante la ejecución.

    Requisitos:
        - La tabla `resumen_inversion` debe existir con una restricción de unicidad sobre `ticker`.
        - Las columnas del CSV deben incluir: 'Ticker', '%_Tecnico_Buy', '%_Fundamental_Buy', 'Decision_Final',
          'Estado_BollingerBands', 'SMA_vs_EMA', 'MACD', 'RSI', 'PER', 'ROE', 'EPS Growth YoY',
          'Deuda/Patrimonio' y 'Estado_Fibonacci'.
    """
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
    """
    Inserta o actualiza de forma incremental los registros de variaciones porcentuales de precios 
    en la tabla `precios_variaciones`.

    La función compara las fechas del archivo CSV con la última fecha disponible en la tabla y 
    carga únicamente los registros más recientes. Utiliza `ON CONFLICT` para evitar duplicados, 
    actualizando los valores si el `ticker` y la `date` ya existen.

    Args:
        csv_path (str): Ruta al archivo CSV con las variaciones de precios. 
                        Debe incluir las columnas:
                        'Date', 'Ticker', 'Close', 'var_daily', 'var_weekly',
                        'var_monthly', 'var_annual', 'var_5y'.

    Returns:
        None: No devuelve un valor explícito. Inserta o actualiza los datos en la base de datos.

    Raises:
        FileNotFoundError: Si el archivo CSV no existe.
        psycopg2.DatabaseError: Si ocurre un error de conexión o en la ejecución SQL.
        KeyError: Si el CSV no contiene todas las columnas necesarias.
        Exception: Para otros errores durante la ejecución.

    Requisitos:
        - La tabla `precios_variaciones` debe tener una restricción de unicidad en (date, ticker).
        - La función `get_connection()` debe retornar una conexión válida a PostgreSQL.
    """
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
