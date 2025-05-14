-- 9. Performance Anual de AAPL (últimos años)
SELECT 
    EXTRACT(YEAR FROM date) AS año,
    MIN(close) AS min_close,
    MAX(close) AS max_close,
    AVG(close) AS avg_close
FROM precios_historicos
WHERE ticker = 'AAPL'
GROUP BY año
ORDER BY año DESC;


-- 10. Simular "alerta de trading" SMA vs EMA
SELECT 
    it.date,
    it.ticker,
    ph.close,
    it.sma_20,
    it.ema_20,
    CASE
        WHEN it.sma_20 < it.ema_20 THEN 'POSIBLE VENTA'
        WHEN it.sma_20 > it.ema_20 THEN 'POSIBLE COMPRA'
        ELSE 'NEUTRO'
    END AS decision_trading
FROM indicadores_tecnicos it
LEFT JOIN precios_historicos ph 
    ON it.ticker = ph.ticker AND it.date = ph.date
WHERE it.ticker = 'AAPL'
  AND it.sma_20 IS NOT NULL
  AND it.ema_20 IS NOT NULL
ORDER BY it.date DESC;

-- 11. Último precio de Apple y su posición respecto a bandas de Bollinger
SELECT 
    ph.date,
    ph.close,
    it.bb_upper,
    it.bb_lower,
    CASE
        WHEN ph.close > it.bb_upper THEN 'Sobrecomprado'
        WHEN ph.close < it.bb_lower THEN 'Sobrevendido'
        ELSE 'Neutral'
    END AS estado_bollinger
FROM precios_historicos ph
LEFT JOIN indicadores_tecnicos it
  ON ph.ticker = it.ticker AND ph.date = it.date
WHERE ph.ticker = 'AAPL'
ORDER BY ph.date DESC
LIMIT 1;



