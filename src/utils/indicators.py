import numpy as np


def calculate_rsi(prices, period=14):
    deltas = np.diff(prices)
    seed = deltas[: period + 1]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down
    rsi = np.zeros_like(prices)
    rsi[:period] = 100.0 - 100.0 / (1.0 + rs)

    for i in range(period, len(prices)):
        delta = deltas[i - 1]
        if delta > 0:
            upval = delta
            downval = 0.0
        else:
            upval = 0.0
            downval = -delta
        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period
        rs = up / down
        rsi[i] = 100.0 - 100.0 / (1.0 + rs)

    return rsi


def calculate_bollinger_bands(prices, period=20, num_std_dev=2):
    rolling_mean = np.convolve(prices, np.ones(period), "valid") / period
    rolling_std = np.std(
        [prices[i : i + period] for i in range(len(prices) - period + 1)], axis=1
    )

    upper_band = rolling_mean + (rolling_std * num_std_dev)
    lower_band = rolling_mean - (rolling_std * num_std_dev)

    return upper_band, rolling_mean, lower_band
