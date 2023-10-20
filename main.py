from Historical_Data import CoingeckoFetcher

symbol = "dydx"
fetcher = CoingeckoFetcher(symbol=symbol)
data = fetcher.fetch_data(start_date=fetcher.get_earliest_price())

print("Finsihed fetching data")
print()
print(data)
