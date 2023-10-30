-- To retrieve the unique symbol and category names along with their latest date
SELECT S.symbol_name, C.category_name, MAX(M.timestamp_utc) AS latest_date
FROM MarketData M
JOIN Symbols S ON M.symbol_id = S.symbol_id
JOIN Categories C ON M.category_id = C.category_id
GROUP BY S.symbol_name, C.category_name;
