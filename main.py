import streamlit as st
import plotly.graph_objects as go
from data_manager import MarketDataManager, NewsManager
from brain import MarketAnalyzer


class BitcoinDashboard:
    """Streamlitの画面表示と全体制御"""

    def __init__(self):
        self.market_dm = MarketDataManager()
        self.news_dm = NewsManager()
        self.analyzer = MarketAnalyzer()

    def run(self):
        st.title("🛡️ ジェミーのBTC分析本部")

        if st.sidebar.button("データ最新化"):
            self.market_dm.update_data()
            st.sidebar.success("更新完了！")

        # データの読み込みと可視化
        df = self.market_dm.update_data()
        df = self.analyzer.calculate_ichimoku(df)

        # チャート描画
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'],
                                             high=df['High'], low=df['Low'], close=df['Close'])])
        st.plotly_chart(fig)

        # ニュース表示
        st.subheader("📰 市場のニュース")
        for news in self.news_dm.fetch_and_score():
            st.write(f"【{news['score']}点】{news['title']}")


if __name__ == "__main__":
    app = BitcoinDashboard()
    app.run()