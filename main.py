from Historical_Data.crypto import CoingeckoFetcher

symbol = "mantle"
fetcher = CoingeckoFetcher(symbol=symbol)
data = fetcher.fetch_raw_data(start_date=fetcher.get_earliest_price())

print("Finsihed fetching data")
print()
print(data)
