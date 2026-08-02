def calculate_moving_average(data, window_size):
    return data.rolling(window=window_size).mean()

def calculate_volatility(data, window_size):
    return data.rolling(window=window_size).std()

def calculate_bollinger_bands(data, window_size, num_std_dev=2):
    moving_avg = calculate_moving_average(data, window_size)
    volatility = calculate_volatility(data, window_size)
    upper_band = moving_avg + (volatility * num_std_dev)
    lower_band = moving_avg - (volatility * num_std_dev)
    return upper_band, lower_band

def calculate_rsi(data, window_size=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window_size).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window_size).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def feature_engineering(data):
    data['moving_average'] = calculate_moving_average(data['close'], window_size=20)
    data['volatility'] = calculate_volatility(data['close'], window_size=20)
    data['upper_band'], data['lower_band'] = calculate_bollinger_bands(data['close'], window_size=20)
    data['rsi'] = calculate_rsi(data['close'])
    return data

def calculate_features(data):
    """
    Wrapper function used by app.py.
    Applies all feature engineering steps.
    """
    return feature_engineering(data)