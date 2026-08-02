import yfinance as yf


def load_historical_data(symbol, period="1y"):

    data = yf.download(
        symbol,
        period=period,
        auto_adjust=True,
        progress=False
    )

    if data.empty:
        raise ValueError(f"No data found for {symbol}")

    # Handle MultiIndex columns returned by yfinance
    if hasattr(data.columns, "levels"):
        data.columns = data.columns.get_level_values(0)

    # Convert column names to lowercase
    data.columns = [str(col).lower() for col in data.columns]
    
    return data


def preprocess_data(data):
    return data.dropna()


def prepare_data_for_analysis(data):
    return preprocess_data(data)