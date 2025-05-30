
import streamlit as st
import gspread
import json
import os
from google.oauth2.service_account import Credentials

from datetime import datetime, timedelta


# スプレッドシート認証
creds_dict = dict(st.secrets["credentials"])
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
gc = gspread.authorize(creds)

# スプレッドシートとシート名を指定
spreadsheet = gc.open("こっログ記録")
worksheet = spreadsheet.worksheet("記録")

# タイトル表示
st.title("こっログ")
st.write('毎日の離脱症状を記録するアプリです')

# 日付入力(初期値は今日)
default_date = (datetime.now() - timedelta(days = 1)).date()
date_to_use = st.date_input("日付", value = default_date)

#　日本語の曜日を定義（ロケールを使わない）
weekday_name = ["月","火","水","木","金","土","日"]
weekday_jp = weekday_name[date_to_use.weekday()]

# 日付+曜日の表示
st.write(f"選択した日付：{date_to_use.strftime('%Y年%m月%d日')}({weekday_jp})")


# 入力項目フォーム
with st.form(key = "symptom_form"):
    time_period = st.selectbox("症状の出始めた時間帯",["午前","午後","夕方","夜","深夜","なし","その他"])
    
    if time_period == "なし":
        duration = "0分"
        st.write("症状がないため、長さは「０分」に設定されます。")
        
    else:
        
        duration_options = [f"{i//2}時間" if i % 2 == 0 else f"{i//2}時間30分" for i in range(1,17)]
        duration = st.selectbox("症状の長さ", duration_options)
    
    sleep_score = st.slider("睡眠の評価（0～5,0.5刻み）",0.0,5.0,3.0,0.5,format = "%.1f")
    
    memo = st.text_area("備考欄（メモ）", placeholder="気づいたことや体調の変化などを自由に記入", max_chars=150)
    
    submitted = st.form_submit_button("記録する")

if submitted:
    worksheet.append_row([str(date_to_use), time_period, duration, str(sleep_score), memo])
    
    st.success("✅　スプレッドシートに記録しました！")
