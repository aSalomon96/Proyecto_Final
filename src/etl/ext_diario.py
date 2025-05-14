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
    Actualiza el CSV de datos históricos solo con las fechas nuevas.
    """
    print("📅 Verificando última fecha disponible en históricos...")

    # Cargar data existente
    if not os.path.exists(historicos_path):
        print("❌ Archivo histórico no encontrado. Ejecutá el script principal primero.")
        return

    historico_df = pd.read_csv(historicos_path)
    historico_df["Date"] = pd.to_datetime(historico_df["Date"])
    ultima_fecha = historico_df["Date"].max().date()

    fecha_inicio = ultima_fecha + timedelta(days=1)
    fecha_fin = datetime.today().date()

    if fecha_inicio > fecha_fin:
        print("✅ No hay datos nuevos para actualizar.")
        return

    tickers_df = pd.read_csv(tickers_path)
    tickers = tickers_df["Ticker"].dropna().unique().tolist()

    print(f"📈 Descargando datos desde {fecha_inicio} hasta {fecha_fin} para {len(tickers)} tickers...")

    nuevos_datos = yf.download(
        tickers,
        start=str(fecha_inicio),
        end=str(fecha_fin + timedelta(days=1)),  # para que incluya el último día
        group_by='ticker',
        threads=True
    )

    if nuevos_datos.empty:
        print("⚠️ No se encontraron nuevos datos.")
        return

    nuevos_datos_tidy = nuevos_datos.stack(level=0).rename_axis(['Date', 'Ticker']).reset_index()
    nuevos_datos_tidy["Date"] = pd.to_datetime(nuevos_datos_tidy["Date"])

    df_actualizado = pd.concat([historico_df, nuevos_datos_tidy], ignore_index=True)
    df_actualizado.drop_duplicates(subset=["Date", "Ticker"], keep="last", inplace=True)

    df_actualizado.to_csv(historicos_path, index=False)
    print(f"✅ Históricos actualizados: {historicos_path}")


def actualizar_fundamentales(
    tickers_path="../../data/raw_data/top_500_marketcap.csv",
    output_file="../../data/raw_data/nyse_top_500_fundamentals_indicators.csv"
):
    """
    Re-extrae la tabla de fundamentales con datos actualizados,
    incluyendo acciones en circulación.
    """
    print("📊 Reextrayendo fundamentales...")

    try:
        tickers_df = pd.read_csv(tickers_path)
    except Exception as e:
        print("❌ Error al leer tickers:", e)
        return

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

    data_fundamentals = []

    for ticker in tqdm(tickers_df["Ticker"]):
        try:
            yf_obj = yf.Ticker(ticker)
            info = getattr(yf_obj, "info", None)

            fila = {"Ticker": ticker}
            if info and isinstance(info, dict):
                for indicador, key in indicators_keys.items():
                    fila[indicador] = info.get(key, None)
            else:
                tqdm.write(f"⚠️ Sin info para {ticker}")
                for indicador in indicators_keys:
                    fila[indicador] = None

            data_fundamentals.append(fila)

        except Exception as e:
            tqdm.write(f"❌ Error al obtener datos de {ticker}: {e}")

    df = pd.DataFrame(data_fundamentals)
    df.to_csv(output_file, index=False)
    print(f"✅ Fundamentales actualizados: {output_file}")

if __name__ == "__main__":
    actualizar_datos_historicos()
    actualizar_fundamentales()
