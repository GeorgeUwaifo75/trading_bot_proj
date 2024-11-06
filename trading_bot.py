from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies import Strategy
from lumibot.traders import Trader
from datetime import datetime

from google.colab import userdata
API_KEY = userdata.get('API_KEY')
SECRET_KEY = userdata.get('SECRET_KEY')

BASE_URL = "https://paper-api.alpaca.markets/v2"

start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 6, 30)


ALPACA_CREDS ={

"API_KEY": API_KEY,
"API_SECRET": SECRET_KEY,
"PAPER": True

}

class MLTrader(Strategy):
  def initialize(self, symbol:str='SPY'):
    self.symbol = symbol
    self.sleeptime = "24h"
    self.last_trade = None

  def on_backtest_start(self):
    if self.last_trade is None:

      order = self.create_order(
          self.symbol,
          10,
          "buy",
          type="market"
      )
      self.submit_order(order)
      self.last_trade = "buy"

  def on_trading_iteration(self):
    pass

broker = Alpaca(ALPACA_CREDS)
strategy = MLTrader( name ='mlstrat', broker = broker, parameters= {"symbol":"SPY"} )
strategy.backtest(
    YahooDataBacktesting,
    start_date,
    end_date,
    parameters= {"symbol":"SPY"}
)
