import pandas as pd
import yfinance as yf
from tqdm import tqdm
from datetime import datetime

def extract_top_500_marketcap(output_file="../../data/raw_data/top_500_marketcap.csv"):
    """
    Extrae los 500 tickers del índice S&P 500 con mayor capitalización de mercado y guarda la información en un archivo CSV.

    Esta función accede a la lista actualizada de empresas del S&P 500 desde Wikipedia, obtiene información financiera
    relevante para cada ticker usando la API de Yahoo Finance, calcula las capitalizaciones de mercado, y guarda 
    las 500 empresas con mayor market cap en un archivo CSV.

    Args:
        output_file (str): Ruta donde se guardará el archivo CSV con el top 500. 
                           Por defecto: "../../data/raw_data/top_500_marketcap.csv".

    Returns:
        None: La función no retorna ningún valor; guarda el resultado directamente en el archivo especificado.

    Raises:
        No se propagan excepciones explícitamente, pero los errores durante la obtención de datos de cada ticker 
        se capturan e imprimen en consola.

    """

    # Imprime un mensaje indicando que está comenzando a obtener la lista de empresas del S&P 500
    print("🔍 Obteniendo lista del S&P 500 desde Wikipedia...")

    try:
        # Lee la tabla de empresas del S&P 500 desde Wikipedia
        sp500_df = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
    except Exception as e:
        # Si hay un error al leer la tabla, se muestra el error y se termina la función
        print(f"❌ Error al leer la página de Wikipedia: {e}")
        return

    # Reemplaza puntos en los símbolos por guiones, por compatibilidad con Yahoo Finance
    sp500_df["Symbol"] = sp500_df["Symbol"].str.replace(".", "-", regex=False)

    # Convierte la columna de símbolos en una lista de tickers
    tickers = sp500_df["Symbol"].tolist()

    results = []  # Lista que almacenará la información recopilada

    # Informa que comenzará la descarga de información financiera
    print("📊 Descargando market caps (esto puede tardar unos minutos)...")

    # Itera sobre cada ticker para obtener su información desde Yahoo Finance
    for ticker in tqdm(tickers):
        try:
            info = yf.Ticker(ticker).info  # Obtiene la información del ticker
            # Agrega un diccionario con los datos relevantes al resultado
            results.append({
                "Ticker": ticker,
                "Name": info.get("shortName", ""),
                "Sector": info.get("sector", ""),
                "Industry": info.get("industry", ""),
                "MarketCap": info.get("marketCap", 0)
            })
        except Exception as e:
            # Si hay un error con un ticker individual, lo muestra pero continúa con los demás
            tqdm.write(f"⚠️ Error con {ticker}: {e}")

    # Crea un DataFrame con todos los resultados obtenidos
    df = pd.DataFrame(results)

    # Ordena el DataFrame por capitalización de mercado de forma descendente
    df.sort_values("MarketCap", ascending=False, inplace=True)

    # Selecciona los primeros 500 registros (top 500 por market cap)
    df_top500 = df.head(500)

    # Guarda el DataFrame resultante en un archivo CSV sin índice
    df_top500.to_csv(output_file, index=False)

    # Informa que el archivo se guardó correctamente
    print(f"✅ Top 500 empresas guardadas en: {output_file}")



def descargar_datos_historicos(tickers_csv_path: str,
                               salida_csv_path: str,
                               fecha_inicio: str = "2007-01-01",
                               fecha_fin: str = None) -> pd.DataFrame:
    """
    Descarga datos históricos de acciones desde Yahoo Finance en formato tidy y los guarda en un archivo CSV.

    Esta función lee una lista de tickers desde un archivo CSV, descarga los datos históricos de precios 
    (Open, High, Low, Close, Adj Close y Volume) desde Yahoo Finance para el rango de fechas indicado, 
    los transforma a un formato "tidy" (ordenado), y los guarda en un archivo CSV.

    Args:
        tickers_csv_path (str): Ruta al archivo CSV que contiene una columna 'Ticker' con los símbolos bursátiles.
        salida_csv_path (str): Ruta donde se guardará el archivo CSV con los datos descargados.
        fecha_inicio (str, opcional): Fecha de inicio para la descarga en formato 'YYYY-MM-DD'. Por defecto, '2007-01-01'.
        fecha_fin (str, opcional): Fecha de fin para la descarga en formato 'YYYY-MM-DD'. Si no se especifica,
                                   se utiliza la fecha actual.

    Returns:
        pd.DataFrame: Un DataFrame en formato tidy con columnas: ['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'].

    Raises:
        FileNotFoundError: Si el archivo de tickers no existe.
        ValueError: Si no se encuentra la columna 'Ticker' en el archivo CSV.
        Exception: Para otros errores durante la descarga o procesamiento de datos.

    """

    # Si no se proporciona fecha de fin, se toma la fecha actual en formato YYYY-MM-DD
    if fecha_fin is None:
        fecha_fin = datetime.today().strftime('%Y-%m-%d')

    # Lee el archivo CSV con los tickers
    tickers_df = pd.read_csv(tickers_csv_path)

    # Extrae los tickers únicos y válidos (sin valores nulos)
    tickers = tickers_df["Ticker"].dropna().unique().tolist()

    # Informa al usuario sobre cuántos tickers se descargarán y el rango de fechas
    print(f"📥 Descargando datos históricos para {len(tickers)} tickers desde {fecha_inicio} hasta {fecha_fin}...")

    # Descarga los datos históricos desde Yahoo Finance
    data = yf.download(tickers, start=fecha_inicio, end=fecha_fin, group_by='ticker', threads=True)

    # Convierte los datos a formato tidy:
    # 'stack' reorganiza los niveles del índice, y luego se renombra y se resetea el índice
    data_tidy = data.stack(level=0).rename_axis(['Date', 'Ticker']).reset_index()

    # Guarda el DataFrame tidy en un archivo CSV sin índice
    data_tidy.to_csv(salida_csv_path, index=False)

    # Informa al usuario que la exportación fue exitosa
    print(f"✅ Datos históricos guardados en {salida_csv_path}")

    # Devuelve el DataFrame con los datos descargados
    return data_tidy


def extract_fundamentals_indicators(
    info_csv="../../data/raw_data/top_500_marketcap.csv",
    output_file="../../data/raw_data/nyse_top_500_fundamentals_indicators.csv"
):
    """
    Extrae indicadores fundamentales para cada ticker listado en un archivo CSV y los guarda en otro archivo CSV.

    La función lee una lista de tickers desde un archivo CSV, consulta la API de Yahoo Finance para cada símbolo,
    y extrae múltiples métricas fundamentales (como PER, ROE, crecimiento de EPS, deuda/patrimonio, etc.).
    Los resultados se consolidan en un DataFrame y se exportan a un archivo CSV.

    Args:
        info_csv (str): Ruta al archivo CSV que contiene los tickers en una columna llamada 'Ticker'. 
                        Por defecto: '../../data/raw_data/top_500_marketcap.csv'.
        output_file (str): Ruta donde se guardará el archivo CSV con los indicadores fundamentales.
                           Por defecto: '../../data/raw_data/nyse_top_500_fundamentals_indicators.csv'.

    Returns:
        None: La función no retorna ningún valor; guarda el DataFrame con los indicadores en un archivo CSV.

    Raises:
        FileNotFoundError: Si el archivo de entrada no existe.
        Exception: Captura e imprime cualquier error durante la obtención o procesamiento de los datos.

    """

    # Intenta leer el archivo CSV de entrada con los tickers
    try:
        tickers_df = pd.read_csv(info_csv)
    except Exception as e:
        # Si falla la lectura, se informa el error y se termina la función
        print("❌ Error al leer el CSV de tickers:", e)
        return

    # Diccionario que mapea los nombres de indicadores a las claves de Yahoo Finance
    indicators_keys = {
        "Name": "shortName",
        "PER": "trailingPE",
        "ROE": "returnOnEquity",
        "EPS Growth YoY": "earningsQuarterlyGrowth",
        "Deuda/Patrimonio": "debtToEquity",
        "Market Cap": "marketCap",
        "Margen Neto": "profitMargins",
        "Dividend Yield": "dividendYield",
        "Industria": "industry",
        "Sector": "sector",
        "Acciones en Circulación": "sharesOutstanding"  # Campo agregado para análisis financiero
    }

    fundamentals_list = []  # Lista donde se acumularán los datos fundamentales por ticker

    print("📊 Extrayendo indicadores fundamentales...")

    # Itera sobre cada ticker en la columna "Ticker" del DataFrame
    for ticker in tqdm(tickers_df["Ticker"]):
        try:
            yf_obj = yf.Ticker(ticker)  # Instancia del objeto Yahoo Finance para el ticker
            info = getattr(yf_obj, "info", None)  # Intenta obtener el atributo 'info'

            data = {"Ticker": ticker}  # Diccionario base con el ticker

            # Si se obtiene un diccionario válido de información
            if info and isinstance(info, dict):
                # Extrae cada indicador usando su clave correspondiente en Yahoo Finance
                for indicador, key in indicators_keys.items():
                    data[indicador] = info.get(key, None)
            else:
                # Si no se pudo obtener la info, asigna None a todos los indicadores
                tqdm.write(f"⚠️ No se pudo obtener info para {ticker}")
                for indicador in indicators_keys:
                    data[indicador] = None

            fundamentals_list.append(data)  # Agrega los datos al listado

        except Exception as e:
            # En caso de error con un ticker, lo muestra pero continúa
            tqdm.write(f"❌ Error al obtener datos de {ticker}: {e}")

    # Crea un DataFrame a partir de la lista de resultados
    df_fundamentals = pd.DataFrame(fundamentals_list)

    # Exporta el DataFrame a un archivo CSV
    df_fundamentals.to_csv(output_file, index=False)

    # Informa que el proceso finalizó correctamente
    print(f"✅ Tabla de indicadores fundamentales guardada en: {output_file}")


if __name__ == "__main__":
    """
    Punto de entrada principal del script.

    Ejecuta en secuencia los siguientes procesos:
    1. Extrae los 500 tickers con mayor capitalización de mercado del S&P 500 desde Wikipedia.
    2. Descarga datos históricos de precios para esos tickers desde Yahoo Finance.
    3. Extrae indicadores fundamentales para cada uno de los tickers.

    Todos los resultados se guardan como archivos CSV en rutas predefinidas dentro de la carpeta `data/raw_data/`.

    Este bloque permite que el script sea ejecutado de forma independiente.
    """

    # Rutas para guardar los resultados
    marketcap_path = "../../data/raw_data/top_500_marketcap.csv"  # Archivo con los tickers y capitalización
    historicos_path = "../../data/raw_data/nyse_top500_data.csv"  # Archivo con datos históricos de precios
    fundamentales_path = "../../data/raw_data/nyse_top_500_fundamentals_indicators.csv"  # Archivo con indicadores fundamentales

    # Paso 1: Extraer los 500 tickers con mayor capitalización de mercado del S&P 500
    extract_top_500_marketcap(output_file=marketcap_path)

    # Paso 2: Descargar los datos históricos de precios desde Yahoo Finance
    descargar_datos_historicos(
        tickers_csv_path=marketcap_path,
        salida_csv_path=historicos_path,
        fecha_inicio="2007-01-01"  # Fecha de inicio arbitraria para análisis de largo plazo
    )

    # Paso 3: Extraer los indicadores fundamentales de cada empresa
    extract_fundamentals_indicators(
        info_csv=marketcap_path,
        output_file=fundamentales_path
    )
