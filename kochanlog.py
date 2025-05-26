
import streamlit as st
import gspread

from datetime import datetime, timedelta

import locale

# 日本語ロケールを設定（Windows用）
try:
    locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
except locale.Error:
    try:
        # Windowsで一般的なロケール名
        locale.setlocale(locale.LC_TIME, 'japanese')
    except locale.Error:
        st.warning("⚠ 日本語ロケールが見つかりません。曜日が正しく表示されない場合があります。")

# スプレッドシート認証
gc = gspread.service_account(filename = "credentials.json")

# スプレッドシートとシート名を指定
spreadsheet = gc.open("こっログ記録")
worksheet = spreadsheet.worksheet("記録")

# タイトル表示
st.title("こっログ")
st.write('毎日の離脱症状を記録するアプリです')

# 日付入力(初期値は今日)
default_date = (datetime.now() - timedelta(days = 1)).date()
date_to_use = st.date_input("日付", value = default_date)


st.write(f"選択した日付：{date_to_use.strftime('%Y年%m月%d日')}")

# 入力項目フォーム
with st.form(key = "symptom_form"):
    time_period = st.selectbox("症状の時間帯",["午前","午後","夕方","夜","深夜","なし","その他"])
    if time_period == "なし":
        duration = "0分"
        st.write("症状がないため、長さは「０分」に設定されます。")
        
    else:
        
        duration_options = [f"{i//2}時間" if i % 2 == 0 else f"{i//2}時間30分" for i in range(1,13)]
        duration = st.selectbox("症状の長さ", duration_options)
    
    sleep_score = st.slider("睡眠の評価（1～5,0.5刻み）",1.0,5.0,3.0,0.5,format = "%.1f")
    
    memo = st.text_area("備考欄（メモ）", placeholder="気づいたことや体調の変化などを自由に記入", max_chars=100)
    
    submitted = st.form_submit_button("記録する")

if submitted:
    worksheet.append_row([str(date_to_use), time_period, duration, str(sleep_score), memo])
    
    st.success("✅　スプレッドシートに記録しました！")