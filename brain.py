import pandas as pd

class MarketAnalyzer:
    """テクニカル指標の計算と予測を担当"""
    def calculate_ichimoku(self, df):
        # 一目均衡表の計算（転換線、基準線、先行スパン）
        high_9 = df['High'].rolling(window=9).max()
        low_9 = df['Low'].rolling(window=9).min()
        df['tenkan_sen'] = (high_9 + low_9) / 2

        high_26 = df['High'].rolling(window=26).max()
        low_26 = df['Low'].rolling(window=26).min()
        df['kijun_sen'] = (high_26 + low_26) / 2
        return df

    def get_ai_advice(self, user_input, market_data):
        # ここにジェミー（AI）との連携を書くよ
        return f"パーコさん、現在の価格は{market_data['Close'].iloc[-1]:.0f}ドルだね。ボクの分析では…"