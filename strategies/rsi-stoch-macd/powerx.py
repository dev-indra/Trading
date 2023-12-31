# --- Do not remove these libs ---
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame

# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


class powerx(IStrategy):
    # Trading strategy based on Markus Heitkoetter's PowerX strategy
    # https://www.youtube.com/watch?v=6C_ac36iXMw
    stoploss = -1
    timeframe = "1d"
    # trailing_stop = True
    # trailing_stop_positive = 0.3
    minimal_roi = {"0": 100.}

    order_types = {
        "buy": "limit",
        "sell": "limit",
        "emergencysell": "market",
        "stoploss": "market",
        "stoploss_on_exchange": True,
        "stoploss_on_exchange_interval": 60,
        "stoploss_on_exchange_limit_ratio": 0.99,
    }

    plot_config = {
        # Main plot indicators (Moving averages, ...)
        "main_plot": {
            "sma": {},
        },
        "subplots": {
            # Subplots - each dict defines one additional plot
            "MACD": {
                "macd": {"color": "blue"},
                "macdsignal": {"color": "orange"},
            },
            "RSI": {
                "rsi": {"color": "red"},
            },
            "STOCH": {
                "slowd": {"color": "red"},
            },
        },
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # SMA
        dataframe["SMA"] = ta.SMA(dataframe, timeperiod=20)
        # RSI
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=7)
        # SLOW STOCHASTIC
        # https://mrjbq7.github.io/ta-lib/doc_index.html
        stoch = ta.STOCH(
            dataframe,
            fastk_period=14,
            slowk_period=3,
            slowk_matype=0,
            slowd_period=3,
            slowd_matype=0,
        )
        dataframe["slowd"] = stoch["slowd"]
        dataframe["slowk"] = stoch["slowk"]
        # MACD
        # https://mrjbq7.github.io/ta-lib/func_groups/momentum_indicators.html
        macd = ta.MACD(
            dataframe,
            fastperiod=12,
            fastmatype=0,
            slowperiod=26,
            slowmatype=0,
            signalperiod=9,
            signalmatype=0,
        )
        dataframe["macd"] = macd["macd"]
        dataframe["macdsignal"] = macd["macdsignal"]
        dataframe["macdhist"] = macd["macdhist"]


        # print(metadata)
        # print(dataframe.tail(20))
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # pass
        dataframe.loc[
            (
                (dataframe["rsi"] > 50)
                & (dataframe["slowd"] > 50)
                & (dataframe["macdhist"] > 0)
            ),
            "buy",
        ] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # pass
        dataframe.loc[
            (
                (dataframe["rsi"] < 50)
                | (dataframe["slowd"] < 50)
                | (dataframe["macdhist"] < 0)
            ),
            "sell",
        ] = 1
        # print(metadata)
        # print(dataframe.tail(20))
        return dataframe
