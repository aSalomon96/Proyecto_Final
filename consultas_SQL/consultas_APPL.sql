-- ========================
-- 1. Info de la Empresa AAPL
-- ========================
SELECT *
FROM empresas
WHERE ticker = 'AAPL';

-- ========================
-- 2. Precios históricos de AAPL (recientes)
-- ========================
SELECT *
FROM precios_historicos
WHERE ticker = 'AAPL'
ORDER BY date DESC;

-- ========================
-- 3. Indicadores fundamentales de AAPL
-- ========================
SELECT *
FROM indicadores_fundamentales
WHERE ticker = 'AAPL';

-- ========================
-- 4. Indicadores técnicos de AAPL (últimos 30 días)
-- ========================
SELECT *
FROM indicadores_tecnicos
WHERE ticker = 'AAPL'
  AND date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY date DESC;

-- ========================
-- 5. Precios + SMA + EMA de AAPL
-- ========================
SELECT 
    ph.date,
    ph.close,
    it.sma_20,
    it.ema_20
FROM precios_historicos ph
LEFT JOIN indicadores_tecnicos it
  ON ph.ticker = it.ticker AND ph.date = it.date
WHERE ph.ticker = 'AAPL'
  AND ph.date >= CURRENT_DATE - INTERVAL '60 days'
ORDER BY ph.date DESC;

-- ========================
-- 6. Top 10 días con mayor volatilidad de AAPL
-- ========================
SELECT
    date,
    ticker,
    volatility_20
FROM indicadores_tecnicos
WHERE ticker = 'AAPL'
  AND volatility_20 IS NOT NULL
ORDER BY volatility_20 desc;


-- ========================
-- 7. Días de sobrecompra (RSI > 70)
-- ========================
SELECT 
    date,
    ticker,
    rsi_14
FROM indicadores_tecnicos
WHERE ticker = 'AAPL'
  AND rsi_14 > 70 and rsi_14 IS NOT NULL
ORDER BY date DESC;

-- ========================
-- 8. Señales de compra por cruce de MACD
-- ========================
SELECT 
    date,
    ticker,
    macd,
    macd_signal
FROM indicadores_tecnicos
WHERE ticker = 'AAPL'
  AND macd > macd_signal
ORDER BY date DESC;
