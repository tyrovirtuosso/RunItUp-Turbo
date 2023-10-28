-- Get Unique symbol, category pairs
SELECT DISTINCT S.symbol_name, C.category_name
FROM MarketData M
JOIN Symbols S ON M.symbol_id = S.symbol_id
JOIN Categories C ON M.category_id = C.category_id;
