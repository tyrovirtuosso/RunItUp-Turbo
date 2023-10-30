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

-- Create the Symbols table
CREATE TABLE IF NOT EXISTS Symbols (
    symbol_id SERIAL PRIMARY KEY,
    symbol_name VARCHAR(10) NOT NULL
);

-- Create the MarketData table with foreign key references
CREATE TABLE IF NOT EXISTS MarketData (
    market_data_id SERIAL PRIMARY KEY,
    timestamp_utc TIMESTAMP NOT NULL,
    category_id INT NOT NULL,
    symbol_id INT NOT NULL,
    open NUMERIC(12, 2) NOT NULL,
    high NUMERIC(12, 2) NOT NULL,
    low NUMERIC(12, 2) NOT NULL,
    close NUMERIC(12, 2) NOT NULL,
    volume NUMERIC(20, 8) NOT NULL,
    source_id INT NOT NULL,
    UNIQUE (timestamp_utc, category_id, symbol_id),
    FOREIGN KEY (category_id) REFERENCES Categories(category_id),
    FOREIGN KEY (symbol_id) REFERENCES Symbols(symbol_id),
    FOREIGN KEY (source_id) REFERENCES Sources(source_id)
);
