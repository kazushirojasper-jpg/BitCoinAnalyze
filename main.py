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
        st.title("BTC分析")

        # サイドバーで表示をコントロール！
        st.sidebar.header("表示設定")
        show_lines = st.sidebar.checkbox("転換線・基準線")
        show_cloud = st.sidebar.checkbox("雲を表示")

        if st.sidebar.button("データ最新化"):
            # 過去のイベントデータを取得
            self.news_dm.get_historical_events()
            st.sidebar.success("更新完了！")

        # データの読み込みと可視化
        # 市場データを取得
        df = self.market_dm.update_data()
        # 売買代金を計算
        df = self.analyzer.add_trade_value(df)
        # 過去のイベントデータを取得
        events_df = self.news_dm.get_historical_events()

        # 一目均衡表を計算
        df = self.analyzer.calculate_ichimoku(df)
        # 市場データとイベントをマージ
        df = self.analyzer.merge_market_and_events(df, events_df)

        # --- 期間切り替えのラジオボタン ---
        st.sidebar.subheader("表示期間")
        period_map = {
            "1週間": 7,
            "1か月": 30,
            "3か月": 90,
            "6か月": 180,
            "1年": 365,
            "3年": 365 * 3,
            "6年": 365 * 6,
            "すべて": 0
        }
        selected_period = st.sidebar.radio("期間を選択", list(period_map.keys()), index=0)  # デフォルト1週間

        # データの期間を絞り込み
        if selected_period != "すべて":
            days = period_map[selected_period]
            df = df.tail(days)

        # チャート描画
        fig = go.Figure()

        # メインのローソク足（これは左軸 yaxis1）
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'], name='BTC価格',
            yaxis='y1'
        ))

        # 転換線と基準線
        if show_lines:
            fig.add_trace(go.Scatter(x=df.index, y=df['tenkan_sen'], name='転換線', line=dict(color='blue')))
            fig.add_trace(go.Scatter(x=df.index, y=df['kijun_sen'], name='基準線', line=dict(color='red')))

        # 雲（先行スパン）
        if show_cloud:
            # 雲の間を塗るために fill='tonexty' を使うよ！
            fig.add_trace(
                go.Scatter(x=df.index, y=df['senkou_span_1'], name='先行1', line=dict(width=0), showlegend=False))
            fig.add_trace(go.Scatter(x=df.index, y=df['senkou_span_2'], name='雲（先行2）', fill='tonexty',
                                     fillcolor='rgba(173, 216, 230, 0.3)', line=dict(width=0)))

        # 市場のニュースをチャート上にプロット
        # イベントがある日だけを抽出
        if 'Event' in df.columns:
            events = df[df['Event'].notna()]
        if not events.empty:
            fig.add_trace(go.Scatter(
                name='イベント',
                x=events.index,
                y=events['High'] * 1.1,  # ローソク足の少し上に表示
                mode='markers+text',
                text=events['Event'],
                textposition="top center",
                marker=dict(symbol='triangle-down', size=12, color='yellow')
            ))

        # --- 売買代金（Trade_Value_JPY）を別軸 棒グラフで表示 ---
        fig.add_trace(go.Bar(
            name=' 売買代金(JPY)',
            x=df.index, y=df['Trade_Value_JPY'],
            yaxis='y2',  # 2番目の軸を使う
            marker_color='rgba(100, 100, 100, 0.3)'
        ))

        # レイアウト設定（2軸の設定とレンジスライダー非表示など）
        fig.update_layout(
            template="plotly_white",
            paper_bgcolor='white',
            plot_bgcolor='white',
            yaxis=dict(
                title="価格 (JPY)",
                side="left",
                showgrid=True,
                gridcolor='lightgrey'
            ),
            yaxis2=dict(
                title="売買代金 (JPY)",
                side='right',
                overlaying='y',
                showgrid=False,
                range=[0, df['Trade_Value_JPY'].max() * 4]
            ),
            xaxis_rangeslider_visible=False,
            height=600,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig, use_container_width=True)

        # ニュース表示
        st.subheader("市場のニュース")
        for news in self.news_dm.fetch_and_score():
            st.write(f"【{news['score']}点】{news['title']}")


if __name__ == "__main__":
    app = BitcoinDashboard()
    app.run()