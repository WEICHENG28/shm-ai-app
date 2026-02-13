import streamlit as st
import os
import json
import ai_engine
import scraper
import shutil
import time

# 設定網頁標題與寬度配置
st.set_page_config(page_title="SHM 智能鑑價網", page_icon="💎", layout="wide")

# 自訂 CSS (優化卡片顯示)
st.markdown("""
    <style>
    .stApp {background-color: #1E1E1E;}
    .metric-box {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #F63366;
        margin-bottom: 10px;
    }
    .used-item {
        background-color: #31333F;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        border: 1px solid #555;
    }
    .new-item {
        background-color: #1E4620; /* 深綠色背景代表新品 */
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        border: 1px solid #28a745;
    }
    a {text-decoration: none; color: #4DA6FF !important;}
    </style>
    """, unsafe_allow_html=True)

# 標題區
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.markdown("<h1>💎</h1>", unsafe_allow_html=True)
with col_title:
    st.title("SHM 二手智能鑑價中心")
    st.markdown("##### 🚀 AI 視覺鑑價 / 市場大數據分析")

st.divider()

# 側邊欄
with st.sidebar:
    st.header("⚙️ 系統選單")
    st.info("系統狀態：連線正常")
    st.markdown("---")
    st.write("📸 **拍攝指南**")
    st.caption("1. 正面：確認款式")
    st.caption("2. 底部：確認型號貼紙 (關鍵!)")

# 主功能區
tab1, tab2 = st.tabs(["📤 上傳鑑價", "📊 歷史紀錄"])

with tab1:
    if not os.path.exists("test_data"):
        os.makedirs("test_data")
    
    col_upload, col_empty = st.columns([2, 1])
    with col_upload:
        uploaded_files = st.file_uploader("拖曳或點擊上傳商品照片...", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

    if uploaded_files:
        st.write("##### 📸 預覽：")
        cols = st.columns(len(uploaded_files))
        saved_paths = []
        for idx, uploaded_file in enumerate(uploaded_files):
            file_path = os.path.join("test_data", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            saved_paths.append(file_path)
            with cols[idx]:
                st.image(uploaded_file, use_container_width=True, caption=f"圖 {idx+1}")

        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 啟動 AI 全面分析", type="primary", use_container_width=True):
            if len(saved_paths) < 2:
                st.warning("💡 建議至少上傳 2 張照片（含底部標籤）以獲得精準行情！")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # 1. AI 視覺分析
                status_text.text("🔍 AI 正在掃描特徵與標籤...")
                progress_bar.progress(30)
                
                raw_result = ai_engine.analyze_multiple_items(saved_paths)
                json_str = raw_result.replace("```json", "").replace("```", "").strip()
                data = json.loads(json_str)
                
                # 2. 獲取市場數據 (雙引擎)
                status_text.text("📊 正在分析二手市場行情 & 比對新品價格...")
                progress_bar.progress(60)
                
                # 準備關鍵字
                raw_model = data.get('model', '')
                clean_model = raw_model.split('(')[0].strip()
                search_query = f"{data.get('brand')} {clean_model}"
                
                # 引擎 A: 二手行情 (模擬數據)
                ai_price_range = data.get('estimated_price_range', 'NT$500 - NT$1000')
                used_items = scraper.get_used_market_data(search_query, ai_price_range)
                
                # 引擎 B: 新品行情 (PChome)
                new_item = scraper.get_new_price_pchome(search_query)
                
                progress_bar.progress(100)
                status_text.text("✅ 分析完成！")
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()
                
                # === 顯示區塊 1: AI 核心結果 ===
                st.success(f"🎉 辨識成功：{data.get('brand')} {data.get('model')}")
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"""<div class="metric-box"><h4>❤️ 新舊評分</h4><h1 style="color:#F63366;">{data.get('condition_score')}/10</h1></div>""", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""<div class="metric-box"><h4>💰 二手估價 (TWD)</h4><h2 style="color:#00CC96;">{data.get('estimated_price_range')}</h2></div>""", unsafe_allow_html=True)
                with c3:
                    st.markdown(f"""<div class="metric-box"><h4>🧐 專家簡評</h4><p>{data.get('analysis')}</p></div>""", unsafe_allow_html=True)
                
                st.divider()

                # === 顯示區塊 2: 二手市場行情 (這是使用者最在意的) ===
                st.subheader("📉 二手市場成交參考")
                st.caption(f"根據 {search_query} 的近期市場數據分析：")
                
                u_col1, u_col2 = st.columns(2)
                for i, item in enumerate(used_items):
                    if i < 4: # 只顯示前4筆
                        with (u_col1 if i % 2 == 0 else u_col2):
                            st.markdown(f"""
                            <div class="used-item">
                                <span style="background-color: #555; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px;">{item['platform']}</span>
                                <span style="float: right; color: #aaa; font-size: 12px;">{item['tag']}</span>
                                <br>
                                <b style="color:white; font-size: 14px;">{item['title']}</b><br>
                                <span style="font-size: 20px; color: #FFD700; font-weight: bold;">NT$ {item['price']:,}</span><br>
                            </div>
                            """, unsafe_allow_html=True)
                
                # 台灣交易平台傳送門
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**🔎 前往平台查看即時商品：**")
                shopee_url = f"https://shopee.tw/search?keyword={search_query}"
                carousell_url = f"https://tw.carousell.com/search/{search_query}"
                
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    st.link_button("🦐 蝦皮購物 (Shopee)", shopee_url, use_container_width=True)
                with btn_col2:
                    st.link_button("🎠 旋轉拍賣 (Carousell)", carousell_url, use_container_width=True)

                st.divider()

                # === 顯示區塊 3: 新品價格對照 (PChome) ===
                if new_item:
                    st.subheader("🆕 新品原價對照 (PChome 24h)")
                    
                    # 計算 CP 值
                    try:
                        prices = [int(s) for s in ai_price_range.split() if s.isdigit()]
                        avg_used = sum(prices)/len(prices) if prices else 0
                        new_price = int(new_item['price'])
                        save_money = new_price - avg_used
                        
                        if save_money > 0:
                            st.success(f"🔥 買二手超划算！相比新品約可省下 **NT$ {int(save_money):,}**")
                    except:
                        pass

                    # 顯示新品卡片
                    col_new_img, col_new_info = st.columns([1, 3])
                    with col_new_img:
                         if new_item['image']:
                            st.image(new_item['image'], use_container_width=True)
                    with col_new_info:
                        st.markdown(f"""
                        <div class="new-item">
                            <b style="color:#28a745;">[全新品] 目前售價</b><br>
                            <span style="font-size: 16px; color: white;">{new_item['title']}</span><br>
                            <span style="font-size: 24px; color: #fff; font-weight: bold;">NT$ {new_item['price']:,}</span><br>
                            <a href="{new_item['link']}" target="_blank">🔗 前往 PChome 賣場</a>
                        </div>
                        """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"分析失敗: {e}")

with tab2:
    st.info("歷史紀錄功能開發中...")