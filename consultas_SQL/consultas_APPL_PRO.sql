-- 📊 Mini Dashboard de Trading para AAPL
SELECT 
    it.date,
    it.ticker,
    ph.close AS precio_actual,
    ROUND(it.rsi_14, 2) AS rsi_14,
    ROUND(it.volatility_20, 2) AS volatilidad_20,
    ROUND(it.macd, 4) AS macd,
    ROUND(it.macd_signal, 4) AS macd_signal,
    CASE
        WHEN it.macd > it.macd_signal THEN 'MACD: Señal de COMPRA'
        WHEN it.macd < it.macd_signal THEN 'MACD: Señal de VENTA'
        ELSE 'MACD: Neutro'
    END AS estado_macd,
    CASE
        WHEN ph.close > it.bb_upper THEN 'Precio FUERA de Bandas: Sobrecompra'
        WHEN ph.close < it.bb_lower THEN 'Precio FUERA de Bandas: Sobreventa'
        ELSE 'Precio dentro de Bandas'
    END AS estado_bollinger
FROM indicadores_tecnicos it
LEFT JOIN precios_historicos ph 
    ON it.ticker = ph.ticker AND it.date = ph.date
WHERE it.ticker = 'AAPL'
ORDER BY it.date DESC
LIMIT 20;
