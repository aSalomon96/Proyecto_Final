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
    """
    Imprime un mensaje en consola con una marca temporal.

    Esta función facilita el seguimiento cronológico de los eventos y operaciones
    dentro del script, permitiendo un registro más claro y útil para debugging o monitoreo.

    Args:
        msg (str): Mensaje que se desea imprimir junto con la marca de tiempo.

    Returns:
        None
    """
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


def transformar_empresas(input_file, output_file):
    """
    Transforma un archivo CSV con datos de empresas para conservar solo columnas clave 
    como el ticker, nombre, sector e industria, y guarda el resultado en un nuevo archivo CSV.

    Esta función es útil para estandarizar y simplificar el dataset de empresas,
    dejando solo la información esencial para análisis posteriores o visualizaciones.

    Args:
        input_file (str): Ruta al archivo CSV de entrada que contiene los datos originales.
        output_file (str): Ruta donde se guardará el archivo CSV transformado.

    Returns:
        None: La función no retorna valores, solo genera un nuevo archivo con la información filtrada.
    """
    
    log("Transformando datos de empresas...")

    # Carga el archivo CSV original en un DataFrame
    df = pd.read_csv(input_file)

    # Define las columnas que se quieren conservar: ticker, nombre, sector e industria
    columnas_finales = ["Ticker", "Name", "Sector", "Industry"]

    # Filtra el DataFrame para conservar solo las columnas seleccionadas
    df = df[columnas_finales]

    # Guarda el nuevo DataFrame en el archivo de salida sin incluir el índice
    df.to_csv(output_file, index=False)

    # Imprime un log indicando que la transformación fue exitosa
    log(f"Empresas listas guardadas en: {output_file}")


def transformar_precios_historicos(input_file, output_file):
    """
    Transforma un archivo CSV de precios históricos al formato tidy y estandariza los nombres de columnas.

    La función renombra columnas para asegurar consistencia, selecciona solo las variables relevantes
    y normaliza los formatos de fecha y precisión decimal de los precios. Ideal para preparar los datos 
    antes de análisis o visualización.

    Args:
        input_file (str): Ruta al archivo CSV con los datos históricos originales.
        output_file (str): Ruta donde se guardará el archivo CSV transformado en formato tidy.

    Returns:
        None: La función no retorna ningún valor, pero guarda el resultado procesado en disco.
    """
    
    log("Transformando precios historicos (formato tidy)...")

    # Carga el archivo CSV original
    df = pd.read_csv(input_file)

    # Renombra las columnas para asegurar nombres estandarizados
    df = df.rename(columns={
        "date": "Date",
        "ticker": "Ticker",
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume"
    })

    # Selecciona solo las columnas relevantes en el orden deseado
    df = df[['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume']]

    # Convierte la columna 'Date' a tipo datetime para análisis temporal correcto
    df['Date'] = pd.to_datetime(df['Date'])

    # Redondea los precios a 3 decimales para estandarizar la precisión
    df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']].round(3)

    # Guarda el DataFrame procesado en el archivo de salida
    df.to_csv(output_file, index=False)

    log(f"Precios historicos listos guardados en: {output_file}")


def transformar_indicadores_fundamentales(input_file, output_file):
    """
    Transforma el archivo de indicadores fundamentales para conservar solo columnas clave
    y calcular el ranking de empresas según capitalización de mercado.

    Esta función filtra las columnas más relevantes del archivo original y agrega un ranking
    descendente basado en el valor de 'Market Cap', lo que permite ordenar rápidamente
    las empresas más grandes del universo analizado.

    Args:
        input_file (str): Ruta al archivo CSV con los indicadores fundamentales crudos.
        output_file (str): Ruta donde se guardará el archivo CSV transformado.

    Returns:
        None: La función no retorna valores, pero guarda el resultado procesado en disco.
    """

    log("Transformando indicadores fundamentales...")

    # Carga el archivo CSV con los datos fundamentales
    df = pd.read_csv(input_file)

    # Define las columnas que se desean conservar
    columnas_finales = [
        "Ticker", "Name", "PER", "ROE", "EPS Growth YoY",
        "Deuda/Patrimonio", "Margen Neto", "Dividend Yield", "Market Cap", "Acciones en Circulación"
    ]

    # Filtra el DataFrame para conservar solo las columnas seleccionadas
    df = df[columnas_finales]

    # Agrega una columna de ranking por capitalización de mercado (de mayor a menor)
    df["Ranking MarketCap"] = df["Market Cap"].rank(ascending=False, method='first').astype(int)

    # Guarda el DataFrame transformado en un nuevo archivo CSV sin el índice
    df.to_csv(output_file, index=False)

    log(f"Indicadores fundamentales listos guardados en: {output_file}")


def calcular_rsi(close, window=14):
    """
    Calcula el índice de fuerza relativa (RSI) para una serie de precios de cierre.

    El RSI es un indicador técnico que mide la velocidad y el cambio de los movimientos de precios.
    Su valor oscila entre 0 y 100, y comúnmente se utiliza para identificar condiciones de sobrecompra 
    (RSI > 70) o sobreventa (RSI < 30).

    Args:
        close (pd.Series): Serie de precios de cierre.
        window (int, opcional): Ventana de cálculo para el promedio móvil de ganancias/pérdidas. 
                                Por defecto es 14 períodos.

    Returns:
        pd.Series: Serie de valores RSI calculados para cada punto temporal.
    """

    # Calcula la diferencia entre precios consecutivos
    delta = close.diff()

    # Separa los movimientos positivos (ganancias)
    gain = delta.clip(lower=0)

    # Separa los movimientos negativos (pérdidas), convirtiéndolos en positivos
    loss = -delta.clip(upper=0)

    # Calcula el promedio móvil de las ganancias sobre la ventana definida
    avg_gain = gain.rolling(window=window).mean()

    # Calcula el promedio móvil de las pérdidas sobre la misma ventana
    avg_loss = loss.rolling(window=window).mean()

    # Relación entre ganancia media y pérdida media
    rs = avg_gain / avg_loss

    # Fórmula final del RSI
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calcular_macd(close, short=12, long=26, signal=9):
    """
    Calcula el indicador MACD (Moving Average Convergence Divergence) a partir de precios de cierre.

    El MACD es un indicador de momentum basado en la diferencia entre dos medias móviles exponenciales (EMA),
    una de corto y otra de largo plazo. Además, se calcula una línea de señal (EMA del MACD) y un histograma 
    que representa la diferencia entre ambos.

    Args:
        close (pd.Series): Serie de precios de cierre.
        short (int, opcional): Ventana para la EMA de corto plazo. Por defecto es 12.
        long (int, opcional): Ventana para la EMA de largo plazo. Por defecto es 26.
        signal (int, opcional): Ventana para la EMA de la señal. Por defecto es 9.

    Returns:
        Tuple[pd.Series, pd.Series, pd.Series]: 
            - macd: Serie del MACD (EMA corta - EMA larga).
            - macd_signal: Línea de señal (EMA del MACD).
            - macd_hist: Histograma del MACD (MACD - señal), usado para detectar cambios de momentum.
    """

    # Calcula la EMA de corto plazo
    ema_short = close.ewm(span=short, adjust=False).mean()

    # Calcula la EMA de largo plazo
    ema_long = close.ewm(span=long, adjust=False).mean()

    # Resta la EMA larga de la corta → línea MACD
    macd = ema_short - ema_long

    # Calcula la línea de señal como una EMA del MACD
    macd_signal = macd.ewm(span=signal, adjust=False).mean()

    # Calcula el histograma del MACD (diferencia entre MACD y su señal)
    macd_hist = macd - macd_signal

    # Devuelve las tres series: MACD, señal e histograma
    return macd, macd_signal, macd_hist


def calcular_atr(high, low, close, window=14):
    """
    Calcula el ATR (Average True Range), un indicador técnico que mide la volatilidad del mercado.

    El ATR representa el rango de precio real durante un período determinado, teniendo en cuenta gaps 
    entre sesiones. Es ampliamente utilizado para definir niveles de stop loss dinámicos y evaluar
    el riesgo de una operación.

    Args:
        high (pd.Series): Serie de precios máximos diarios.
        low (pd.Series): Serie de precios mínimos diarios.
        close (pd.Series): Serie de precios de cierre diarios.
        window (int, opcional): Número de períodos para el promedio móvil. Por defecto es 14.

    Returns:
        pd.Series: Serie con los valores del ATR calculados.
    """

    # Rango diario: diferencia entre el máximo y el mínimo del día
    high_low = high - low

    # Diferencia absoluta entre el máximo del día y el cierre del día anterior
    high_close = (high - close.shift()).abs()

    # Diferencia absoluta entre el mínimo del día y el cierre del día anterior
    low_close = (low - close.shift()).abs()

    # Combina los tres posibles rangos para cada día
    ranges = pd.concat([high_low, high_close, low_close], axis=1)

    # Determina el "true range" como el mayor de los tres valores por fila
    true_range = ranges.max(axis=1)

    # Calcula el ATR como promedio móvil simple del true range
    atr = true_range.rolling(window=window).mean()

    # Devuelve la serie de ATR
    return atr

def calcular_obv(close, volume):
    """
    Calcula el indicador On-Balance Volume (OBV) a partir de precios de cierre y volumen negociado.

    El OBV es un indicador técnico que relaciona el volumen con el movimiento de precios. 
    Suma o resta el volumen diario en función de si el precio cierra más alto o más bajo 
    que el día anterior. Se utiliza para detectar divergencias entre precio y volumen, 
    anticipando posibles cambios de tendencia.

    Args:
        close (pd.Series): Serie de precios de cierre.
        volume (pd.Series): Serie de volúmenes negociados diarios.

    Returns:
        pd.Series: Serie con los valores acumulados del OBV.
    """

    # Calcula el signo del cambio en el precio de cierre respecto al día anterior:
    #  1 si subió, -1 si bajó, 0 si se mantuvo igual
    # Luego multiplica por el volumen para agregar (o restar) volumen al OBV
    obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()

    # Devuelve el OBV acumulado como serie
    return obv


def calcular_indicadores_tecnicos(input_file, output_file):
    """
    Calcula indicadores técnicos clásicos y niveles de retroceso de Fibonacci sobre precios históricos
    para una lista de tickers, y guarda el resultado en un archivo CSV.

    Esta función agrupa los datos por ticker y genera múltiples indicadores de análisis técnico, incluyendo:
    - Medias móviles (SMA y EMA)
    - RSI
    - MACD (línea, señal e histograma)
    - ATR (volatilidad real)
    - OBV (flujo de volumen)
    - Bandas de Bollinger
    - Volatilidad histórica (desviación estándar móvil)
    - Niveles de retroceso de Fibonacci con categorización como soporte o resistencia

    Args:
        input_file (str): Ruta al archivo CSV con los precios históricos. 
                          Debe contener columnas: 'Date', 'Ticker', 'Close', 'High', 'Low', 'Volume'.
        output_file (str): Ruta donde se guardará el archivo CSV con los indicadores calculados.

    Returns:
        None: Los resultados se guardan directamente en el archivo especificado.
    """
    log("Calculando indicadores técnicos y niveles de Fibonacci...")
    df = pd.read_csv(input_file)

    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by=['Ticker', 'Date'])

    indicadores = [] # Lista donde se guardarán los resultados por ticker

    for ticker, group in tqdm(df.groupby('Ticker')):
        group = group.copy()

        # Cálculo de indicadores tradicionales
        # Medias móviles
        group['SMA_20'] = group['Close'].rolling(window=20).mean()
        group['SMA_50'] = group['Close'].rolling(window=50).mean()
        group['EMA_20'] = group['Close'].ewm(span=20, adjust=False).mean()

        # RSI
        group['RSI_14'] = calcular_rsi(group['Close'])
        group['MACD'], group['MACD_Signal'], group['MACD_Hist'] = calcular_macd(group['Close'])

        # ATR y OBV
        group['ATR_14'] = calcular_atr(group['High'], group['Low'], group['Close'])
        group['OBV'] = calcular_obv(group['Close'], group['Volume'])

        # Bandas de Bollinger (usando media y desviación estándar de 20 días)
        group['BB_Middle'] = group['Close'].rolling(window=20).mean()
        group['BB_Upper'] = group['BB_Middle'] + 2 * group['Close'].rolling(window=20).std()
        group['BB_Lower'] = group['BB_Middle'] - 2 * group['Close'].rolling(window=20).std()

        # Volatilidad histórica (std de 20 días)
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

        #Los niveles de Fibonacci más comunes son porcentajes de retroceso desde el punto más alto (Fib_0.0% = máximo) hacia el más bajo (Fib_100% = mínimo).
        # Por ejemplo:
        # Fib_38.2% = max_close - 38.2% del rango → es un nivel en el que muchos traders esperan un rebote alcista si el precio baja hasta ahí.
        # Los valores se calculan como restas desde el máximo.
        # Este es el clásico patrón de retroceso que suele usarse tras un impulso para ver hasta dónde puede retroceder antes de continuar la tendencia.
        
        # Último Close del ticker - Se obtiene el precio de cierre más reciente, que vamos a comparar con los niveles Fibonacci.
        ultimo_close = group.iloc[-1]['Close']

        # Determinación del nivel Fibonacci más cercano
        # Calcula la distancia absoluta del último precio a cada uno de los niveles.
        # Luego selecciona el nivel más cercano (min(diffs, key=diffs.get)).
        diffs = {
            '0.0%': abs(ultimo_close - group.iloc[-1]['Fib_0.0%']),
            '23.6%': abs(ultimo_close - group.iloc[-1]['Fib_23.6%']),
            '38.2%': abs(ultimo_close - group.iloc[-1]['Fib_38.2%']),
            '50.0%': abs(ultimo_close - group.iloc[-1]['Fib_50.0%']),
            '61.8%': abs(ultimo_close - group.iloc[-1]['Fib_61.8%']),
            '100%': abs(ultimo_close - group.iloc[-1]['Fib_100%'])
        }
        nivel_cercano = min(diffs, key=diffs.get)

        #Si el precio está cerca de niveles medios (como 38.2%, 50%, 61.8%), se asume que el nivel actúa como soporte, 
        # es decir, un posible piso donde el precio rebote.
        # Si está cerca del 0% o 23.6% (más cerca del máximo), se asume resistencia.
        # El 100% (mínimo) se considera neutro, aunque podrías tratarlo como soporte extremo si querés afinar más.
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
    """
    Genera un resumen consolidado de señales de inversión para cada ticker, combinando análisis técnico 
    y fundamental, y guarda el resultado en un archivo CSV.

    Esta función cruza los datos técnicos, fundamentales e históricos, calcula señales específicas de 
    compra, venta o mantener para cada indicador, y toma una decisión final por mayoría. Además, 
    evalúa el estado de las Bandas de Bollinger y el nivel de Fibonacci más cercano.

    Args:
        precios_tecnicos_file (str): Ruta al archivo CSV con indicadores técnicos por fecha y ticker.
        fundamentales_file (str): Ruta al archivo CSV con indicadores fundamentales por ticker.
        precios_historicos_file (str): Ruta al archivo CSV con precios históricos tidy.
        output_file (str): Ruta donde se guardará el resumen generado con las decisiones de inversión.

    Returns:
        None: La función no retorna valores, pero genera un archivo CSV consolidado.

    Raises:
        FileNotFoundError: Si alguno de los archivos de entrada no se encuentra.
        ValueError: Si faltan columnas clave como 'Ticker', 'Close', 'RSI_14', etc.
        Exception: Para errores inesperados durante la lectura, procesamiento o escritura.
    """
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


