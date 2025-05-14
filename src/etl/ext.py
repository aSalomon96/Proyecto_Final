import pandas as pd
import yfinance as yf
from tqdm import tqdm
from datetime import datetime

def extract_top_500_marketcap(output_file="../../data/raw_data/top_500_marketcap.csv"):
    """
    Extrae los 500 tickers del S&P 500 con mayor capitalización de mercado.
    """
    print("🔍 Obteniendo lista del S&P 500 desde Wikipedia...")
    try:
        sp500_df = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
    except Exception as e:
        print(f"❌ Error al leer la página de Wikipedia: {e}")
        return

    sp500_df["Symbol"] = sp500_df["Symbol"].str.replace(".", "-", regex=False)
    tickers = sp500_df["Symbol"].tolist()

    results = []
    print("📊 Descargando market caps (esto puede tardar unos minutos)...")
    for ticker in tqdm(tickers):
        try:
            info = yf.Ticker(ticker).info
            results.append({
                "Ticker": ticker,
                "Name": info.get("shortName", ""),
                "Sector": info.get("sector", ""),
                "Industry": info.get("industry", ""),
                "MarketCap": info.get("marketCap", 0)
            })
        except Exception as e:
            tqdm.write(f"⚠️ Error con {ticker}: {e}")

    df = pd.DataFrame(results)
    df.sort_values("MarketCap", ascending=False, inplace=True)
    df_top500 = df.head(500)

    df_top500.to_csv(output_file, index=False)
    print(f"✅ Top 500 empresas guardadas en: {output_file}")


def descargar_datos_historicos(tickers_csv_path: str,
                               salida_csv_path: str,
                               fecha_inicio: str = "2007-01-01",
                               fecha_fin: str = None) -> pd.DataFrame:
    """
    Descarga datos históricos de acciones desde Yahoo Finance en formato tidy y los guarda en un CSV.
    """
    if fecha_fin is None:
        fecha_fin = datetime.today().strftime('%Y-%m-%d')

    tickers_df = pd.read_csv(tickers_csv_path)
    tickers = tickers_df["Ticker"].dropna().unique().tolist()

    print(f"📥 Descargando datos históricos para {len(tickers)} tickers desde {fecha_inicio} hasta {fecha_fin}...")

    data = yf.download(tickers, start=fecha_inicio, end=fecha_fin, group_by='ticker', threads=True)

    data_tidy = data.stack(level=0).rename_axis(['Date', 'Ticker']).reset_index()

    data_tidy.to_csv(salida_csv_path, index=False)
    print(f"✅ Datos históricos guardados en {salida_csv_path}")

    return data_tidy



def extract_fundamentals_indicators(
    info_csv="../../data/raw_data/top_500_marketcap.csv",
    output_file="../../data/raw_data/nyse_top_500_fundamentals_indicators.csv"
):
    """
    Extrae indicadores fundamentales para cada ticker que aparece en el CSV inicial,
    incluyendo acciones en circulación.
    """
    try:
        tickers_df = pd.read_csv(info_csv)
    except Exception as e:
        print("❌ Error al leer el CSV de tickers:", e)
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
        "Acciones en Circulación": "sharesOutstanding"  # campo agregado
    }

    fundamentals_list = []

    print("📊 Extrayendo indicadores fundamentales...")
    for ticker in tqdm(tickers_df["Ticker"]):
        try:
            yf_obj = yf.Ticker(ticker)
            info = getattr(yf_obj, "info", None)

            data = {"Ticker": ticker}

            if info and isinstance(info, dict):
                for indicador, key in indicators_keys.items():
                    data[indicador] = info.get(key, None)
            else:
                tqdm.write(f"⚠️ No se pudo obtener info para {ticker}")
                for indicador in indicators_keys:
                    data[indicador] = None

            fundamentals_list.append(data)

        except Exception as e:
            tqdm.write(f"❌ Error al obtener datos de {ticker}: {e}")

    df_fundamentals = pd.DataFrame(fundamentals_list)
    df_fundamentals.to_csv(output_file, index=False)
    print(f"✅ Tabla de indicadores fundamentales guardada en: {output_file}")



if __name__ == "__main__":
    # Rutas
    marketcap_path = "../../data/raw_data/top_500_marketcap.csv"
    historicos_path = "../../data/raw_data/nyse_top500_data.csv"
    fundamentales_path = "../../data/raw_data/nyse_top_500_fundamentals_indicators.csv"

    # Ejecutar procesos
    extract_top_500_marketcap(output_file=marketcap_path)

    descargar_datos_historicos(
        tickers_csv_path=marketcap_path,
        salida_csv_path=historicos_path,
        fecha_inicio="2007-01-01"
    )

    extract_fundamentals_indicators(
        info_csv=marketcap_path,
        output_file=fundamentales_path
    )
