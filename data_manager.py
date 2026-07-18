import json

import requests
import yfinance as yf
import pandas as pd
import os

from bs4 import BeautifulSoup
from dotenv import load_dotenv
import google.generativeai as genai

"""市場データの取得・CSV保存を担当"""
class MarketDataManager:
    def __init__(self, symbol="BTC-JPY", file_name="BTC_data.csv"):
        self.symbol = symbol
        self.file_name = file_name

    def update_data(self):
        if os.path.exists(self.file_name):
            # CSVを読み込み
            df = pd.read_csv(self.file_name, index_col=0, header=[0, 1], parse_dates=True)
            df.columns = df.columns.get_level_values(0)
            df = df[~df.index.isin(['Ticker', 'Price', 'Date'])]
            df.index = pd.to_datetime(df.index, utc=True)
            df.index = pd.to_datetime(df.index, utc=True).tz_localize(None)
            # 最後に取得した日の一日後をスタート地点にする
            last_date = df.index[-1]
            start_date = last_date + pd.Timedelta(days=1)
        else:
            df = pd.DataFrame()
            start_date = "2014-09-17"

        new_data = yf.download(self.symbol, start=start_date)
        if not new_data.empty:
            new_data.index = new_data.index.tz_localize(None)
            df = pd.concat([df, new_data])
            df = df[~df.index.duplicated(keep='last')]
            df.to_csv(self.file_name)
        return df

class NewsManager:
    """ニュース収集とネガポジ判定を担当"""
    def __init__(self, event_file="btc_events.csv"):
        self.event_file = event_file
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def get_historical_events(self):
        if os.path.exists(self.event_file):
            events_df = pd.read_csv(self.event_file, index_col=0, parse_dates=True)
            events_df.index = pd.to_datetime(events_df.index).tz_localize(None)
            return events_df
        return pd.DataFrame()

    def fetch_and_score(self):
        # 1. CoinPostから最新ニュースを取得（簡易版）
        url = "https://coinpost.jp/"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')

        # 最新記事のタイトルを取得（セレクタはサイト構造に合わせて調整が必要）
        news_list = []
        articles = soup.select('.cat_list li h2')[:5]  # 最新5件

        for article in articles:
            title = article.get_text(strip=True)

            # 2. Geminiに投げてスコアリング
            score_data = self.analyze_with_gemini(title)

            news_list.append({
                "title": title,
                "score": score_data.get("impact_score", 0),
                "est_impact": score_data.get("est_impact_jpy", 0),
                "direct_pop": score_data.get("direct_pop", 0)
            })
        return news_list

    def analyze_with_gemini(self, title):
        prompt = f"""
                以下の仮想通貨ニュースのタイトルから、市場への影響を予測してJSON形式で返してください。
                タイトル: "{title}"

                返却項目:
                1. impact_score: -100から100の数値（ネガポジ）
                2. est_impact_jpy: 想定される市場への影響金額（円単位、数値のみ）
                3. direct_pop: 直接影響を受ける推定人数

                JSONフォーマットのみを出力してください。
                """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            # JSON部分だけを抽出してパース
            return json.loads(clean_json)
        except:
            return {{"impact_score": 0, "est_impact_jpy": 0, "direct_pop": 0}}
