import yfinance as yf
import pandas as pd
import os

"""市場データの取得・CSV保存を担当"""
class MarketDataManager:
    def __init__(self, symbol="BTC-USD", file_name="BTC_data.csv"):
        self.symbol = symbol
        self.file_name = file_name

    def update_data(self):
        if os.path.exists(self.file_name):
            # CSVを読み込み
            df = pd.read_csv(self.file_name, index_col=0, parse_dates=True)
            df.index = pd.to_datetime(df.index, utc=True)
            # 最後に取得した日の一日後をスタート地点にする
            last_date = df.index[-1]
            start_date = last_date + pd.Timedelta(days=1)
        else:
            df = pd.DataFrame()
            start_date = pd.Timestamp.now() - pd.Timedelta(days=730)

        new_data = yf.download(self.symbol, start=start_date)
        if not new_data.empty:
            df = pd.concat([df, new_data])
            df = df[~df.index.duplicated(keep='last')]
            df.to_csv(self.file_name)
        return df

class NewsManager:
    """ニュース収集とネガポジ判定を担当"""
    def fetch_and_score(self):
        # ここに将来的にスクレイピングを実装
        # 今はモック（仮データ）を返すよ
        news_data = [
            {"title": "ETF流入が加速", "score": 80},
            {"title": "米雇用統計の影響", "score": -20}
        ]
        return news_data