-- Create the Categories table
CREATE TABLE IF NOT EXISTS Categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL
);

-- Create the Sources table
CREATE TABLE IF NOT EXISTS Sources (
    source_id SERIAL PRIMARY KEY,
    source_name VARCHAR(50) NOT NULL
);

-- Create the MarketData table
CREATE TABLE IF NOT EXISTS MarketData (
    market_data_id SERIAL PRIMARY KEY,
    timestamp_utc TIMESTAMP NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    category_id INT NOT NULL,
    open NUMERIC(12, 2) NOT NULL,
    high NUMERIC(12, 2) NOT NULL,
    low NUMERIC(12, 2) NOT NULL,
    close NUMERIC(12, 2) NOT NULL,
    volume NUMERIC(20, 8) NOT NULL,
    source_id INT NOT NULL,
    UNIQUE (timestamp_utc, symbol, category_id)
);

-- Create the CryptoData table
CREATE TABLE IF NOT EXISTS CryptoData (
    crypto_data_id SERIAL PRIMARY KEY,
    market_data_id INT NOT NULL
);

-- Create the StockData table
CREATE TABLE IF NOT EXISTS StockData (
    stock_data_id SERIAL PRIMARY KEY,
    market_data_id INT NOT NULL
);
