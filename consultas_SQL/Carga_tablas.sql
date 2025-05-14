CREATE TABLE empresas (
    ticker VARCHAR(10) PRIMARY KEY,
    name TEXT,
    sector TEXT,
    industry TEXT
);
---------------------------------------------------------------------------

CREATE TABLE precios_historicos (
    date DATE,
    ticker VARCHAR(10),
    open NUMERIC(12,3),
    high NUMERIC(12,3),
    low NUMERIC(12,3),
    close NUMERIC(12,3),
    volume BIGINT,
    PRIMARY KEY (date, ticker),
    FOREIGN KEY (ticker) REFERENCES empresas(ticker)
);
---------------------------------------------------------------------------

CREATE TABLE indicadores_fundamentales (
    ticker VARCHAR(10) PRIMARY KEY,
    name TEXT,
    per NUMERIC,
    roe NUMERIC,
    eps_growth_yoy NUMERIC,
    deuda_patrimonio NUMERIC,
    margen_neto NUMERIC,
    dividend_yield NUMERIC,
    market_cap BIGINT,
    ranking_marketcap INTEGER,
    FOREIGN KEY (ticker) REFERENCES empresas(ticker)
);
---------------------------------------------------------------------------
CREATE TABLE indicadores_tecnicos (
    date DATE,
    ticker VARCHAR(10),
    sma_20 NUMERIC(12,3),
    sma_50 NUMERIC(12,3),
    ema_20 NUMERIC(12,3),
    rsi_14 NUMERIC(6,2),
    macd NUMERIC(12,6),
    macd_signal NUMERIC(12,6),
    macd_hist NUMERIC(12,6),
    atr_14 NUMERIC(12,6),
    obv BIGINT,
    bb_middle NUMERIC(12,3),
    bb_upper NUMERIC(12,3),
    bb_lower NUMERIC(12,3),
    volatility_20 NUMERIC(12,6),
    PRIMARY KEY (date, ticker),
    FOREIGN KEY (ticker) REFERENCES empresas(ticker)
);

ALTER TABLE indicadores_tecnicos
ADD COLUMN close NUMERIC(12, 3);

ALTER TABLE indicadores_tecnicos
ADD COLUMN fib_0_0 NUMERIC(12,3),
ADD COLUMN fib_23_6 NUMERIC(12,3),
ADD COLUMN fib_38_2 NUMERIC(12,3),
ADD COLUMN fib_50_0 NUMERIC(12,3),
ADD COLUMN fib_61_8 NUMERIC(12,3),
ADD COLUMN fib_100 NUMERIC(12,3),
ADD COLUMN nivel_fib_cercano VARCHAR(10),
ADD COLUMN estado_fibonacci VARCHAR(20);
---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS resumen_inversion (
    ticker VARCHAR(10) PRIMARY KEY,
    pct_tecnico_buy NUMERIC(5,2),
    pct_fundamental_buy NUMERIC(5,2),
    decision_final VARCHAR(20),
    estado_bollingerbands VARCHAR(20),
    sma_vs_ema VARCHAR(10),
    macd VARCHAR(10),
    rsi VARCHAR(10),
    per VARCHAR(10),
    roe VARCHAR(10),
    eps_growth_yoy VARCHAR(10),
    deuda_patrimonio VARCHAR(10)
);

ALTER TABLE resumen_inversion
ADD COLUMN estado_fibonacci VARCHAR(20);

---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS precios_variaciones (
    date DATE,
    ticker VARCHAR(10),
    close NUMERIC(12,3),
    var_daily NUMERIC(8,4),
    var_weekly NUMERIC(8,4),
    var_monthly NUMERIC(8,4),
    var_annual NUMERIC(8,4),
    var_5y NUMERIC(8,4),
    PRIMARY KEY (date, ticker),
    FOREIGN KEY (ticker) REFERENCES empresas(ticker)
);
