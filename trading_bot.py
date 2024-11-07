from dotenv import load_dotenv
from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies import Strategy
from lumibot.traders import Trader
from datetime import datetime
from alpaca_trade_api.rest import REST, TimeFrame
from timedelta import Timedelta
from finbert_utils import estimmate_sentiment

from google.colab import userdata
load_dotenv()

#API_KEY = userdata.get('API_KEY')
#SECRET_KEY = userdata.get('SECRET_KEY')

BASE_URL = "https://paper-api.alpaca.markets"


#start_date = datetime(2021, 1, 1)
#end_date = datetime(2021, 12, 30)

start_date = datetime(2020,1,1)
end_date = datetime(2023,12,31) 


ALPACA_CREDS ={
"API_KEY": API_KEY,
"API_SECRET": SECRET_KEY,
"PAPER": True
}

class MLTrader(Strategy):
  def initialize(self, symbol:str='SPY', cash_at_risk:float=0.5):
    self.symbol = symbol
    self.sleeptime = "24h"
    self.last_trade = None
    self.cash_at_risk = cash_at_risk
    self.api = REST(
        base_url=BASE_URL,
        key_id = API_KEY,
        secret_key = SECRET_KEY
        )


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

  def get_dates(self):
      today = self.get_datetime()
      three_days_prior = today - Timedelta(days=3)
      return today.strftime("%Y-%m-%d"), three_days_prior.strftime("%Y-%m-%d")

  def get_sentiment(self): 
      today, three_days_prior = self.get_dates()
      news = self.api.get_news(symbol=self.symbol, 
                                   start=three_days_prior , 
                                   end=today)
      news = [ev.__dict__["_raw"]["headline"] for ev in news] 
     
      probability, sentiment = estimate_sentiment(news)
      return probability, sentiment  

      #news = estimate_sentiment(news)
      #return news  


  def position_sizing(self):
      cash = self.get_cash()
      last_price = self.get_last_price(self.symbol)
      quantity = round(cash * self.cash_at_risk/last_price,0)
      return cash, last_price, quantity
      
      
      
  def on_trading_iteration(self):
    cash, last_price, quantity = self.position_sizing()
    probability, sentiment = self.get_sentiment()
    #news = self.get_sentiment()
    #print(news)
    if cash > last_price:
          if sentiment == "positive" and probability>.999:
                if self.last_trade == "sell":
                  self.sell_all()

                order = self.create_order(
                    self.symbol,
                    10,
                    "buy",
                    type="bracket",
                    take_profit_price = last_price * 1.20,
                    stop_loss_price = last_price * 0.95
                )
                self.submit_order(order)
                self.last_trade = "buy"

          elif sentiment == "negative" and probability>.999:
                if self.last_trade == "buy":
                  self.sell_all()
                  
                order = self.create_order(
                    self.symbol,
                    10,
                    "sell",
                    type="bracket",
                    take_profit_price = last_price * .8,
                    stop_loss_price = last_price * 1.05
                )
                self.submit_order(order)
                self.last_trade = "sell"



broker = Alpaca(ALPACA_CREDS)
strategy = MLTrader( name ='mlstrat', broker = broker, parameters= {"symbol":"SPY", "cash_at_risk":0.5} )

#Comment out the Backtest section if we need to go live
strategy.backtest(
    YahooDataBacktesting,
    start_date,
    end_date,
    parameters= {"symbol":"SPY", "cash_at_risk":0.5}
)

#Uncomment to go into live trading. First method
#trader = Trader(strategy)
#trader.run()

#Uncomment to go into live trading. Second method
#trader = Trader()
#trader.add_strategy(strategy)
#trader.run_all()
