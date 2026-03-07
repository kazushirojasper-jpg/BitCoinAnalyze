from brain import MarketAnalyzer
from data_manager import MarketDataManager, NewsManager

market_dm = MarketDataManager()
news_dm = NewsManager()
analyzer = MarketAnalyzer()

# データの読み込みと可視化
df = market_dm.update_data()
#analyzer.calculate_ichimoku(df)
