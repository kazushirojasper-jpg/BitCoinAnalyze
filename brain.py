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

        # 雲（先行スパン） ---
        # 先行スパン1：転換線と基準線の平均を26日先に表示
        df['senkou_span_1'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)

        # 先行スパン2：過去52日間の最高値と最安値の平均を26日先に表示
        high_52 = df['High'].rolling(window=52).max()
        low_52 = df['Low'].rolling(window=52).min()
        df['senkou_span_2'] = ((high_52 + low_52) / 2).shift(26)
        return df

    # 価格データとイベントデータのマージ
    def merge_market_and_events(self, market_df, events_df):
        # インデックス（日付）で結合
        combined_df = market_df.join(events_df, how='left')

        # 数値カラムの欠損値を0で埋める（イベントがない日はインパクト0）
        fill_cols = ['Direct_Pop', 'Indirect_Pop', 'Est_Impact_JPY']
        for col in fill_cols:
            if col in combined_df.columns:
                combined_df[col] = combined_df[col].fillna(0)
        # 詳しい分析用の「答え（翌日の変化率）」も作る
        combined_df['Target_Return'] = combined_df['Close'].shift(-1) / combined_df['Close'] - 1

        return combined_df

    """
    Volume（BTC数）にClose（価格）を掛けて
    売買代金（Trade_Value_JPY）を算出
    """
    def add_trade_value(self, df):
        # 「その日に動いた総額（円）」を産出
        df['Trade_Value_JPY'] = df['Close'] * df['Volume']

        # 💡 学習用に、過去の平均と比べて「何倍動いたか」という
        # スコア（Volume_Intensity）も作っておく
        df['Volume_Intensity'] = df['Trade_Value_JPY'] / df['Trade_Value_JPY'].rolling(window=20).mean()

        return df

    def get_ai_advice(self, user_input, market_data):
        # ここにジェミー（AI）との連携を書くよ
        return f"パーコさん、現在の価格は{market_data['Close'].iloc[-1]:.0f}ドルだね。ボクの分析では…"
