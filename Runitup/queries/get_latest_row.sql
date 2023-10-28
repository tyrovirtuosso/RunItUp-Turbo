-- To retrieve the open, high, low, close, and volume values of symbol and category on the latest date
SELECT M.open, M.high, M.low, M.close, M.volume
FROM MarketData M
JOIN Symbols S ON M.symbol_id = S.symbol_id
JOIN Categories C ON M.category_id = C.category_id
WHERE S.symbol_name = 'coin' AND C.category_name = 'stock'
AND M.timestamp_utc = (
    SELECT MAX(timestamp_utc)
    FROM MarketData
    WHERE symbol_id = S.symbol_id AND category_id = C.category_id
);
