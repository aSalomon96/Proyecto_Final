import pandas as pd
import os
from tqdm import tqdm
from datetime import datetime
import numpy as np

# Directorios
DIR_RAW = "../../data/raw_data/"
DIR_READY = "../../data/clean_data/"
os.makedirs(DIR_READY, exist_ok=True)

def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def transformar_empresas(input_file, output_file):
    log("Transformando datos de empresas...")
    df = pd.read_csv(input_file)

    columnas_finales = ["Ticker", "Name", "Sector", "Industry"]
    df = df[columnas_finales]

    df.to_csv(output_file, index=False)
    log(f"Empresas listas guardadas en: {output_file}")

def transformar_precios_historicos(input_file, output_file):
    log("Transformando precios historicos (formato tidy)...")
    df = pd.read_csv(input_file)

    df = df.rename(columns={
        "date": "Date",
        "ticker": "Ticker",
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume"
    })

    df = df[['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume']]
    df['Date'] = pd.to_datetime(df['Date'])
    df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']].round(3)

    df.to_csv(output_file, index=False)
    log(f"Precios historicos listos guardados en: {output_file}")

def transformar_indicadores_fundamentales(input_file, output_file):
    log("Transformando indicadores fundamentales...")
    df = pd.read_csv(input_file)

    columnas_finales = [
        "Ticker", "Name", "PER", "ROE", "EPS Growth YoY",
        "Deuda/Patrimonio", "Margen Neto", "Dividend Yield", "Market Cap", "Acciones en Circulación"
    ]

    df = df[columnas_finales]
    df["Ranking MarketCap"] = df["Market Cap"].rank(ascending=False, method='first').astype(int)

    df.to_csv(output_file, index=False)
    log(f"Indicadores fundamentales listos guardados en: {output_file}")

def calcular_rsi(close, window=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calcular_macd(close, short=12, long=26, signal=9):
    ema_short = close.ewm(span=short, adjust=False).mean()
    ema_long = close.ewm(span=long, adjust=False).mean()
    macd = ema_short - ema_long
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    macd_hist = macd - macd_signal
    return macd, macd_signal, macd_hist

def calcular_atr(high, low, close, window=14):
    high_low = high - low
    high_close = (high - close.shift()).abs()
    low_close = (low - close.shift()).abs()
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    atr = true_range.rolling(window=window).mean()
    return atr

def calcular_obv(close, volume):
    obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
    return obv

def calcular_indicadores_tecnicos(input_file, output_file):
    """Calcula indicadores técnicos + niveles de Fibonacci sobre precios históricos."""
    log("Calculando indicadores técnicos y niveles de Fibonacci...")
    df = pd.read_csv(input_file)

    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by=['Ticker', 'Date'])

    indicadores = []

    for ticker, group in tqdm(df.groupby('Ticker')):
        group = group.copy()

        # Cálculo de indicadores tradicionales
        group['SMA_20'] = group['Close'].rolling(window=20).mean()
        group['SMA_50'] = group['Close'].rolling(window=50).mean()
        group['EMA_20'] = group['Close'].ewm(span=20, adjust=False).mean()

        group['RSI_14'] = calcular_rsi(group['Close'])
        group['MACD'], group['MACD_Signal'], group['MACD_Hist'] = calcular_macd(group['Close'])

        group['ATR_14'] = calcular_atr(group['High'], group['Low'], group['Close'])
        group['OBV'] = calcular_obv(group['Close'], group['Volume'])

        group['BB_Middle'] = group['Close'].rolling(window=20).mean()
        group['BB_Upper'] = group['BB_Middle'] + 2 * group['Close'].rolling(window=20).std()
        group['BB_Lower'] = group['BB_Middle'] - 2 * group['Close'].rolling(window=20).std()

        group['Volatility_20'] = group['Close'].rolling(window=20).std()

        # Cálculo de Niveles Fibonacci
        max_close = group['Close'].max()
        min_close = group['Close'].min()
        diff = max_close - min_close

        group['Fib_0.0%'] = max_close
        group['Fib_23.6%'] = max_close - diff * 0.236
        group['Fib_38.2%'] = max_close - diff * 0.382
        group['Fib_50.0%'] = max_close - diff * 0.50
        group['Fib_61.8%'] = max_close - diff * 0.618
        group['Fib_100%'] = min_close

        # Último Close del ticker
        ultimo_close = group.iloc[-1]['Close']

        diffs = {
            '0.0%': abs(ultimo_close - group.iloc[-1]['Fib_0.0%']),
            '23.6%': abs(ultimo_close - group.iloc[-1]['Fib_23.6%']),
            '38.2%': abs(ultimo_close - group.iloc[-1]['Fib_38.2%']),
            '50.0%': abs(ultimo_close - group.iloc[-1]['Fib_50.0%']),
            '61.8%': abs(ultimo_close - group.iloc[-1]['Fib_61.8%']),
            '100%': abs(ultimo_close - group.iloc[-1]['Fib_100%'])
        }
        nivel_cercano = min(diffs, key=diffs.get)

        if nivel_cercano in ['38.2%', '50.0%', '61.8%']:
            estado_fib = 'SOPORTE'
        elif nivel_cercano in ['0.0%', '23.6%']:
            estado_fib = 'RESISTENCIA'
        else:
            estado_fib = 'NEUTRO'

        group['Nivel_Fib_Cercano'] = nivel_cercano
        group['Estado_Fibonacci'] = estado_fib

        indicadores.append(group[['Date', 'Ticker', 'Close',
                                  'SMA_20', 'SMA_50', 'EMA_20',
                                  'RSI_14', 'MACD', 'MACD_Signal', 'MACD_Hist',
                                  'ATR_14', 'OBV',
                                  'BB_Middle', 'BB_Upper', 'BB_Lower',
                                  'Volatility_20',
                                  'Fib_0.0%', 'Fib_23.6%', 'Fib_38.2%', 'Fib_50.0%', 'Fib_61.8%', 'Fib_100%',
                                  'Nivel_Fib_Cercano', 'Estado_Fibonacci']])

    df_indicadores = pd.concat(indicadores)
    df_indicadores.to_csv(output_file, index=False)
    log(f"Indicadores técnicos + Fibonacci guardados en: {output_file}")

def calcular_resumen_inversion(
    precios_tecnicos_file=DIR_READY + "indicadores_tecnicos_ready.csv",
    fundamentales_file=DIR_READY + "indicadores_fundamentales_ready.csv",
    precios_historicos_file=DIR_READY + "precios_historicos_ready.csv",
    output_file=DIR_READY + "resumen_inversion_ready.csv"
):
    print("🔍 Calculando resumen detallado de inversión...")

    # Cargar datasets
    df_tecnicos = pd.read_csv(precios_tecnicos_file)
    df_fundamentales = pd.read_csv(fundamentales_file)
    df_precios = pd.read_csv(precios_historicos_file)

    # Tomar último registro por ticker
    df_ultimos_tecnicos = df_tecnicos.sort_values('Date').groupby('Ticker').tail(1)
    df_ultimos_precios = df_precios.sort_values('Date').groupby('Ticker').tail(1)[['Ticker', 'Close']]

    # Merge
    df = pd.merge(df_ultimos_tecnicos, df_fundamentales, on='Ticker', how='inner')
    # Elimina esta línea, porque no hace falta:
    # df = pd.merge(df, df_ultimos_precios, on='Ticker', how='left')

    resultados = []

    for _, row in tqdm(df.iterrows(), total=len(df)):

        ticker = row['Ticker']

        ### Análisis Técnico ###
        señales_tec = {}
        
        # SMA vs EMA
        if pd.notna(row['SMA_20']) and pd.notna(row['EMA_20']):
            señales_tec['SMA_vs_EMA'] = 'COMPRAR' if row['SMA_20'] > row['EMA_20'] else 'VENDER'

        # MACD
        if pd.notna(row['MACD']) and pd.notna(row['MACD_Signal']):
            señales_tec['MACD'] = 'COMPRAR' if row['MACD'] > row['MACD_Signal'] else 'VENDER'

        # RSI
        if pd.notna(row['RSI_14']):
            if row['RSI_14'] < 30:
                señales_tec['RSI'] = 'COMPRAR'
            elif row['RSI_14'] > 70:
                señales_tec['RSI'] = 'VENDER'
            else:
                señales_tec['RSI'] = 'MANTENER'

        ### Estado de Bollinger Bands (solo informativo)
        estado_bb = np.nan
        if pd.notna(row['BB_Upper']) and pd.notna(row['BB_Lower']) and pd.notna(row['Close']):
            if row['Close'] > row['BB_Upper']:
                estado_bb = "Sobrecompra"
            elif row['Close'] < row['BB_Lower']:
                estado_bb = "Sobreventa"
            else:
                estado_bb = "Normal"
        
        ### Estado de Fibonacci ###
        estado_fib = np.nan
        if 'Estado_Fibonacci' in row and pd.notna(row['Estado_Fibonacci']):
            if row['Estado_Fibonacci'] == 'SOPORTE':
                señales_tec['Estado_Fibonacci'] = 'COMPRAR'
            elif row['Estado_Fibonacci'] == 'RESISTENCIA':
                señales_tec['Estado_Fibonacci'] = 'VENDER'
            else:
                señales_tec['Estado_Fibonacci'] = 'MANTENER'

        ### Análisis Fundamental ###
        señales_fund = {}

        # PER
        if pd.notna(row['PER']):
            if row['PER'] < 20:
                señales_fund['PER'] = 'COMPRAR'
            elif row['PER'] > 30:
                señales_fund['PER'] = 'VENDER'
            else:
                señales_fund['PER'] = 'MANTENER'

        # ROE
        if pd.notna(row['ROE']):
            if row['ROE'] > 0.15:
                señales_fund['ROE'] = 'COMPRAR'
            elif row['ROE'] < 0.05:
                señales_fund['ROE'] = 'VENDER'
            else:
                señales_fund['ROE'] = 'MANTENER'

        # EPS Growth
        if pd.notna(row['EPS Growth YoY']):
            if row['EPS Growth YoY'] > 0.10:
                señales_fund['EPS Growth YoY'] = 'COMPRAR'
            elif row['EPS Growth YoY'] < 0:
                señales_fund['EPS Growth YoY'] = 'VENDER'
            else:
                señales_fund['EPS Growth YoY'] = 'MANTENER'

        # Deuda/Patrimonio
        if pd.notna(row['Deuda/Patrimonio']):
            if row['Deuda/Patrimonio'] < 100:
                señales_fund['Deuda/Patrimonio'] = 'COMPRAR'
            elif row['Deuda/Patrimonio'] > 200:
                señales_fund['Deuda/Patrimonio'] = 'VENDER'
            else:
                señales_fund['Deuda/Patrimonio'] = 'MANTENER'

        ### 3. Conteo de Señales de Compra y Venta

        compras = list(señales_tec.values()).count('COMPRAR') + list(señales_fund.values()).count('COMPRAR')
        ventas = list(señales_tec.values()).count('VENDER') + list(señales_fund.values()).count('VENDER')

        pct_tecnico_buy = round(
            list(señales_tec.values()).count('COMPRAR') / len(señales_tec) * 100, 2
        ) if len(señales_tec) > 0 else np.nan

        pct_fundamental_buy = round(
            list(señales_fund.values()).count('COMPRAR') / len(señales_fund) * 100, 2
        ) if len(señales_fund) > 0 else np.nan

        ### 4. Decisión Final basada en mayoría simple
        if compras > ventas:
            decision = "COMPRAR"
        elif ventas > compras:
            decision = "VENDER"
        else:
            decision = "MANTENER"

        ### Resultado ###
        resultados.append({
            "Ticker": ticker,
            "%_Tecnico_Buy": pct_tecnico_buy,
            "%_Fundamental_Buy": pct_fundamental_buy,
            "Decision_Final": decision,
            "Estado_BollingerBands": estado_bb,
            "SMA_vs_EMA": señales_tec.get('SMA_vs_EMA', np.nan),
            "MACD": señales_tec.get('MACD', np.nan),
            "RSI": señales_tec.get('RSI', np.nan),
            "PER": señales_fund.get('PER', np.nan),
            "ROE": señales_fund.get('ROE', np.nan),
            "EPS Growth YoY": señales_fund.get('EPS Growth YoY', np.nan),
            "Deuda/Patrimonio": señales_fund.get('Deuda/Patrimonio', np.nan),
            "Estado_Fibonacci": row['Estado_Fibonacci']
        })

    # Guardar CSV
    df_resultado = pd.DataFrame(resultados)
    df_resultado.to_csv(output_file, index=False)

    print(f"✅ Resumen de inversión detallado generado: {output_file}")

def calcular_variaciones_precios(input_file=DIR_READY + "precios_historicos_ready.csv",
                                 output_file=DIR_READY + "precios_variaciones_ready.csv"):
    """
    Calcula variaciones porcentuales diarias, semanales, mensuales, anuales y a 5 años de los precios de cierre.

    Args:
        input_file (str): Ruta del archivo de precios históricos limpio.
        output_file (str): Ruta donde guardar el nuevo archivo de variaciones.
    """
    log("Calculando variaciones porcentuales de precios...")

    df = pd.read_csv(input_file, parse_dates=["Date"])[["Date", "Ticker", "Close"]]

    df = df.sort_values(["Ticker", "Date"])

    periods = {
        "daily": 1,
        "weekly": 5,
        "monthly": 21,
        "annual": 252,
        "5y": 252 * 5
    }

    for name, days in periods.items():
        df[f"var_{name}"] = df.groupby("Ticker")["Close"].pct_change(periods=days).round(4)

    cols = ["Date", "Ticker", "Close"] + [f"var_{name}" for name in periods]
    df_variaciones = df[cols]

    df_variaciones.to_csv(output_file, index=False)
    log(f"Variaciones de precios guardadas en: {output_file}")


if __name__ == "__main__":
    tqdm.pandas()

    transformar_empresas(
        input_file=DIR_RAW + "top_500_marketcap.csv",
        output_file=DIR_READY + "empresas_ready.csv"
    )

    transformar_precios_historicos(
        input_file=DIR_RAW + "nyse_top500_data.csv",
        output_file=DIR_READY + "precios_historicos_ready.csv"
    )

    transformar_indicadores_fundamentales(
        input_file=DIR_RAW + "nyse_top_500_fundamentals_indicators.csv",
        output_file=DIR_READY + "indicadores_fundamentales_ready.csv"
    )

    calcular_indicadores_tecnicos(
        input_file=DIR_READY + "precios_historicos_ready.csv",
        output_file=DIR_READY + "indicadores_tecnicos_ready.csv"
    )

    calcular_resumen_inversion()

    calcular_variaciones_precios(
    input_file=DIR_READY + "precios_historicos_ready.csv",
    output_file=DIR_READY + "precios_variaciones_ready.csv"
)


