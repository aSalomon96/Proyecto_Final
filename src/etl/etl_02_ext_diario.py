import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from tqdm import tqdm
import os
from time import sleep

def actualizar_datos_historicos(
    historicos_path="../../data/raw_data/nyse_top500_data.csv",
    tickers_path="../../data/raw_data/top_500_marketcap.csv"
):
    """
    Actualiza el archivo CSV de datos históricos de precios de acciones descargando solo la información 
    correspondiente a fechas nuevas, desde la última fecha registrada hasta el día actual.

    Esta función evita descargar nuevamente datos ya existentes, mejorando la eficiencia del proceso
    de actualización del dataset.

    Args:
        historicos_path (str): Ruta al archivo CSV que contiene los datos históricos existentes.
                               Por defecto: '../../data/raw_data/nyse_top500_data.csv'.
        tickers_path (str): Ruta al archivo CSV que contiene la lista actual de tickers (columna 'Ticker').
                            Por defecto: '../../data/raw_data/top_500_marketcap.csv'.

    Returns:
        None: La función no retorna valores, pero actualiza el archivo de históricos en disco.

    Raises:
        FileNotFoundError: Si el archivo de datos históricos no existe.
        Exception: Para errores inesperados durante la descarga o procesamiento de los datos.

    """

    print("📅 Verificando última fecha disponible en históricos...")

    # Verifica que el archivo de históricos exista
    if not os.path.exists(historicos_path):
        print("❌ Archivo histórico no encontrado. Ejecutá el script principal primero.")
        return

    # Carga los datos históricos existentes
    historico_df = pd.read_csv(historicos_path)

    # Convierte la columna 'Date' a formato datetime
    historico_df["Date"] = pd.to_datetime(historico_df["Date"])

    # Obtiene la última fecha registrada en los históricos
    ultima_fecha = historico_df["Date"].max().date()

    # Define el rango de fechas a descargar: desde el día siguiente hasta hoy
    fecha_inicio = ultima_fecha + timedelta(days=1)
    fecha_fin = datetime.today().date()

    # Si no hay fechas nuevas que cubrir, se termina el proceso
    if fecha_inicio > fecha_fin:
        print("✅ No hay datos nuevos para actualizar.")
        return

    # Carga el archivo con la lista de tickers
    tickers_df = pd.read_csv(tickers_path)

    # Extrae los tickers únicos y válidos
    tickers = tickers_df["Ticker"].dropna().unique().tolist()

    print(f"📈 Descargando datos desde {fecha_inicio} hasta {fecha_fin} para {len(tickers)} tickers...")

    # Descarga nuevos datos de Yahoo Finance
    nuevos_datos = yf.download(
        tickers,
        start=str(fecha_inicio),
        end=str(fecha_fin + timedelta(days=1)),  # Se suma un día para asegurar incluir el día final
        group_by='ticker',
        threads=True
    )

    # Si no se obtuvo ningún dato nuevo, se informa y finaliza
    if nuevos_datos.empty:
        print("⚠️ No se encontraron nuevos datos.")
        return

    # Reorganiza los datos descargados al formato tidy (ordenado)
    nuevos_datos_tidy = nuevos_datos.stack(level=0).rename_axis(['Date', 'Ticker']).reset_index()
    nuevos_datos_tidy["Date"] = pd.to_datetime(nuevos_datos_tidy["Date"])

    # Concatena los nuevos datos con los existentes
    df_actualizado = pd.concat([historico_df, nuevos_datos_tidy], ignore_index=True)

    # Elimina duplicados para cada combinación de fecha y ticker
    df_actualizado.drop_duplicates(subset=["Date", "Ticker"], keep="last", inplace=True)

    # Guarda el DataFrame actualizado en el mismo archivo CSV
    df_actualizado.to_csv(historicos_path, index=False)

    print(f"✅ Históricos actualizados: {historicos_path}")



def actualizar_fundamentales(
    tickers_path="../../data/raw_data/top_500_marketcap.csv",
    output_file="../../data/raw_data/nyse_top_500_fundamentals_indicators.csv"
):
    """
    Re-extrae los indicadores fundamentales actualizados para una lista de tickers y guarda los resultados en un archivo CSV.

    Esta función consulta nuevamente la API de Yahoo Finance para obtener los valores actuales de indicadores fundamentales
    de cada empresa listada en el archivo de tickers, incluyendo acciones en circulación, PER, ROE, y otros. 
    Los datos obtenidos sobrescriben cualquier versión previa del archivo de salida.

    Args:
        tickers_path (str): Ruta al archivo CSV que contiene los tickers en una columna llamada 'Ticker'.
                            Por defecto: '../../data/raw_data/top_500_marketcap.csv'.
        output_file (str): Ruta donde se guardará el archivo CSV actualizado con los indicadores fundamentales.
                           Por defecto: '../../data/raw_data/nyse_top_500_fundamentals_indicators.csv'.

    Returns:
        None: La función no retorna ningún valor, pero actualiza el archivo con los nuevos datos fundamentales.

    Raises:
        FileNotFoundError: Si el archivo de tickers no existe o no puede leerse.
        Exception: Para errores generales durante la consulta a la API o procesamiento de datos.

    """

    print("📊 Reextrayendo fundamentales...")

    # Intenta leer el archivo de tickers
    try:
        tickers_df = pd.read_csv(tickers_path)
    except Exception as e:
        # Si hay error en la lectura del archivo, se informa y termina
        print("❌ Error al leer tickers:", e)
        return

    # Diccionario de indicadores a extraer mapeados a las claves usadas por Yahoo Finance
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
        "Acciones en Circulación": "sharesOutstanding"
    }

    data_fundamentals = []  # Lista donde se acumulará la información fundamental por empresa

    # Itera sobre cada ticker de la lista
    for ticker in tqdm(tickers_df["Ticker"]):
        try:
            yf_obj = yf.Ticker(ticker)  # Objeto Yahoo Finance del ticker
            info = getattr(yf_obj, "info", None)  # Intenta acceder al diccionario de información

            fila = {"Ticker": ticker}  # Inicializa el diccionario por fila

            if info and isinstance(info, dict):
                # Si se obtuvo información válida, extrae cada indicador
                for indicador, key in indicators_keys.items():
                    fila[indicador] = info.get(key, None)
            else:
                # Si no se pudo obtener información, llena con valores nulos
                tqdm.write(f"⚠️ Sin info para {ticker}")
                for indicador in indicators_keys:
                    fila[indicador] = None

            data_fundamentals.append(fila)  # Agrega la fila al conjunto de resultados

        except Exception as e:
            # Si ocurre un error con un ticker individual, lo informa y sigue con el resto
            tqdm.write(f"❌ Error al obtener datos de {ticker}: {e}")

    # Crea un DataFrame con todos los datos recopilados
    df = pd.DataFrame(data_fundamentals)

    # Guarda el DataFrame resultante en un archivo CSV sin índice
    df.to_csv(output_file, index=False)

    print(f"✅ Fundamentales actualizados: {output_file}")


if __name__ == "__main__":
    """
    Punto de entrada principal para actualizar la información financiera.

    Este script ejecuta los siguientes procesos:
    1. Actualiza el archivo de datos históricos de precios, agregando solo fechas nuevas.
    2. Reextrae completamente los indicadores fundamentales más recientes para cada ticker.

    Se espera que los archivos originales (tickers y datos históricos) ya existan, generados previamente
    por el script principal.
    """

    # Actualiza solo las fechas nuevas en el histórico de precios (sin descargar todo de nuevo)
    actualizar_datos_historicos()

    # Vuelve a consultar todos los indicadores fundamentales actuales desde Yahoo Finance
    actualizar_fundamentales()
