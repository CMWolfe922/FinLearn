# PRICE HISTORY SCRIPT
# This script is responsible for getting the price
# history of any symbol passed to the constructor
from .urls import TDA_BASE
from config.secrets import TDA_APIKEY, PERIOD, PERIODTYPE, FREQUENCY, FREQUENCYTYPE
import requests
import pandas as pd
from models.mysql_db import create_pricehistory_engine

"""
=================================================================================
THE PRICE HISTORY CLASS|
-----------------------+
This will be responsible for getting the price history for every symbol
stored in the database. Using a generator function in the models.mysql_db
script, I will be able to generate one symbol at a time and then execute
the insert_price_data() method.

I am going to try two different approaches. First, I will try the map()
function to see if it can handle executing the function on that long of
a list.

If that doesn't work, I will try to utilize the generator function to
generate one symbol at a time and only execute the insert method one
stock at a time.
=================================================================================
"""


class PriceHistory:

    def __init__(self, **params):
        self.params = params  # params are set at bottom, imported from config.ini file
        self.table_name = self._set_table_name()
        self.pricehistory_engine = create_pricehistory_engine()

    def _set_table_name(self):
        """
        Simple way to set the name of the table to save the price data to
        dynamically. This way no matter what the params are, the data will
        be saved to correct table.
        """
        if FREQUENCY > 1:
            name = f"_{FREQUENCY}_{FREQUENCYTYPE}_data"
            return name
        else:
            name = f"one_{FREQUENCYTYPE}_data"
            return name

    def data(self, stock):
        """
        :param symbol: company symbol/ticker
        :Example: MSFT 10 day minute 10

        :returns:
        raw json data (Open, High, Low, close, Volume, and Time (epoch time))
        """
        url = TDA_BASE + f"marketdata/{stock}/pricehistory"

        params = {
            'period': self.params['params']['period'],
            'periodType': self.params['params']['periodType'],
            'frequency': self.params['params']['frequency'],
            'frequencyType': self.params['params']['frequencyType'],
        }

        # Other users will need their own TD Ameritrade API Key
        params.update({"apikey": TDA_APIKEY})

        # request price history data
        req = requests.get(url, params=params).json()

        candles = dict(req)  # turn candles into a dict() type
        extracted_candles_list = candles["candles"]
        symbol = candles["symbol"]  # symbol of the compan's price data

        # Create data frame from extracted data
        df = pd.DataFrame.from_dict(extracted_candles_list, orient="columns")
        df.rename(columns={"datetime": "unix"}, inplace=True)
        df["unix"] = [x for x in df["unix"] // 10 ** 3]

        # This is to insert the companies symbol into the data frame
        # in every row next to the unix_time so that I can identify
        # who the data belongs to.
        df["symbol"] = symbol

        return df

    def insert_price_data(self, stock):
        data = self.data(stock)
        table = self.table_name
        engine = self.pricehistory_engine
        data.to_sql(name=table, con=engine, if_exists='append', index=False)

    def execute_main(self):

        pass


params = {
    'symbol': 'stock',
    'period': PERIOD,
    'periodType': PERIODTYPE,
    'frequency': FREQUENCY,
    'frequencyType': FREQUENCYTYPE,
}

price_history = PriceHistory(params=params)
