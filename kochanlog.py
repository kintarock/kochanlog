import streamlit as st
import gspread
import json
import os
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pandas as pd  # 2025-05-31 追加機能: 確認モードでの表表示用

# スプレッドシート認証
creds_dict = dict(st.secrets["credentials"])
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
gc = gspread.authorize(creds)

# スプレッドシートとシート名を指定
spreadsheet = gc.open("こっログ記録")
worksheet = spreadsheet.worksheet("記録")

# 2025-05-31 追加機能: モード切替（記録モード / 確認モード）
mode = st.sidebar.selectbox("モードを選んでください", ["記録モード", "確認モード"])

if mode == "記録モード":
    # タイトル表示
    st.title("こっちゃんログ")
    st.write('毎日の離脱症状を記録するアプリです')

    # 日付入力(初期値は今日)
    default_date = (datetime.now() - timedelta(days=1)).date()
    date_to_use = st.date_input("日付", value=default_date)

    # 日本語の曜日を定義（ロケールを使わない）
    weekday_name = ["月", "火", "水", "木", "金", "土", "日"]
    weekday_jp = weekday_name[date_to_use.weekday()]

    # 日付+曜日の表示
    st.write(f"選択した日付：{date_to_use.strftime('%Y年%m月%d日')}({weekday_jp})")

    # 入力項目フォーム
    with st.form(key="symptom_form"):
        time_period = st.selectbox("症状の時間帯", ["午前", "午後", "夕方", "夜", "深夜", "なし", "その他"])

        if time_period == "なし":
            duration = "0分"
            st.write("症状がないため、長さは「０分」に設定されます。")
        else:
            duration_options = [f"{i//2}時間" if i % 2 == 0 else f"{i//2}時間30分" for i in range(1, 17)]
            duration = st.selectbox("症状の長さ", duration_options)

        # 2025-05-31 追加機能: 睡眠薬のチェックボックス
        st.markdown('### 睡眠薬の服用状況')

        belsomra = st.radio(
            "ベルソムラ錠の服用量は？",
            ("なし", "半錠", "１錠", "1.3錠"),
            horizontal=True
        )

        rivotril = st.radio(
            "リボトリールの服用量は？",
            ("なし", "半錠", "１錠", "1.3錠"),
            horizontal=True
        )

        sleep_score = st.slider("睡眠の評価（1～5,0.5刻み）", 0.0, 5.0, 2.5, 0.5, format="%.1f")

        memo = st.text_area("備考欄（メモ）", placeholder="気づいたことや体調の変化などを自由に記入", max_chars=150)

        submitted = st.form_submit_button("記録する")

    if submitted:
        worksheet.append_row([str(date_to_use), time_period, duration, belsomra, rivotril, str(sleep_score), memo])
        st.success("✅　スプレッドシートに記録しました！")

elif mode == "確認モード":
    st.title("こっログ：記録の確認モード")  # 2025-05-31 追加機能: 確認モード表示
    st.write("過去の記録を確認できます（直近7日分）")

    try:
        records = worksheet.get_all_records()
        df = pd.DataFrame(records)

        if "日付" in df.columns or "date" in df.columns:
            # 列名を統一（Google Sheetsの列名が日本語なら調整）
            if "日付" in df.columns:
                df.rename(columns={"日付": "date"}, inplace=True)

            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
            df["睡眠の評価"] = df["睡眠の評価"].astype(float).round(1)
            
            df = df.sort_values("date", ascending=False)

        # 表示用の列を並べ替えて見やすくする（任意）
        df["睡眠の評価"] = df["睡眠の評価"].astype(float).round(1)
        display_df = df.head(7)[["date", "症状がでた時", "症状の長さ","ベルソムラ", "リボトリール", "睡眠の評価","メモ・備考"]]

        st.table(display_df)  # ← ここを変更 st.dataframe → st.table
        
    except Exception as e:
        st.error("⚠ スプレッドシートのデータを取得できませんでした。")
        st.exception(e)
