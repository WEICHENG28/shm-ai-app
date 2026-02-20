import streamlit as st
import os
import json
import ai_engine
import scraper
import shutil
import time
import re
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 設定網頁標題
st.set_page_config(page_title="SHM 智能鑑價網", page_icon="💎", layout="wide")

# === 🎨 介面美化：專業電商白風格 ===
st.markdown("""
    <style>
    /* 全站背景設定為乾淨的灰白色，讓卡片更突出 */
    .stApp {
        background-color: #F0F2F6;
    }
    
    /* 核心數據卡片 (白底 + 陰影) */
    .metric-box {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #FF4B4B;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08); /* 輕微陰影增加質感 */
        margin-bottom: 10px;
    }
    
    /* 二手商品卡片 */
    .used-item {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border: 1px solid #E0E0E0; /* 淺灰邊框 */
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        color: #333333; /* 深色文字 */
    }
    
    /* 新品卡片 (綠色邊框強調) */
    .new-item {
        background-color: #F9FFF9; /* 極淺綠底 */
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border: 1px solid #28a745;
        color: #333333;
    }
    
    /* 按鈕樣式優化 */
    .stButton>button {
        border-radius: 20px;
        font-weight: bold;
    }
    
    /* 連結顏色 */
    a {text-decoration: none; color: #0066CC !important;}
    a:hover {color: #FF4B4B !important;}
    
    /* 標題優化 */
    h1, h2, h3 {
        color: #111111 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 標題區
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.markdown("<h1 style='text-align: center;'>💎</h1>", unsafe_allow_html=True)
with col_title:
    st.title("SHM 二手AI智能鑑價中心")
    st.markdown("##### 🚀 AI 視覺鑑價 / 市場大數據分析")

st.divider()

# 側邊欄
with st.sidebar:
    st.header("⚙️ 系統選單")
    st.success("🟢 系統狀態：連線正常")
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
        uploaded_files = st.file_uploader("拖曳或點擊上傳商品照片...，可多拍攝幾張以增加商品估價準確性", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

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
                
                # 2. 獲取市場數據
                status_text.text("📊 正在分析二手市場行情 & 比對新品價格...")
                progress_bar.progress(60)
                
                raw_model = data.get('model', '')
                clean_model = raw_model.split('(')[0].strip()
                search_query = f"{data.get('brand')} {clean_model}"
                
                # 雙引擎搜尋
                ai_price_range = data.get('estimated_price_range', 'NT$500 - NT$1000')
                used_items = scraper.get_used_market_data(search_query, ai_price_range)
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
                    st.markdown(f"""<div class="metric-box"><h4>❤️ 新舊評分</h4><h1 style="color:#FF4B4B;">{data.get('condition_score')}/10</h1></div>""", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""<div class="metric-box"><h4>💰 二手估價 (TWD)</h4><h2 style="color:#28a745;">{data.get('estimated_price_range')}</h2></div>""", unsafe_allow_html=True)
                with c3:
                    st.markdown(f"""<div class="metric-box"><h4>🧐 專家簡評</h4><p style="color:#555;">{data.get('analysis')}</p></div>""", unsafe_allow_html=True)
                
                st.divider()

                # === 顯示區塊 2: 二手市場行情 ===
                st.subheader("📉 二手市場成交參考")
                st.caption(f"根據 {search_query} 的近期市場數據分析：")
                
                u_col1, u_col2 = st.columns(2)
                for i, item in enumerate(used_items):
                    if i < 4:
                        with (u_col1 if i % 2 == 0 else u_col2):
                            st.markdown(f"""
                            <div class="used-item">
                                <span style="background-color: #E0E0E0; color: #333; padding: 2px 8px; border-radius: 4px; font-size: 11px;">{item['platform']}</span>
                                <span style="float: right; color: #666; font-size: 12px;">{item['tag']}</span>
                                <br>
                                <b style="color:#222; font-size: 15px;">{item['title']}</b><br>
                                <span style="font-size: 20px; color: #D93025; font-weight: bold;">NT$ {item['price']:,}</span><br>
                            </div>
                            """, unsafe_allow_html=True)
                
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

                # === 顯示區塊 3: 新品價格對照 ===
                if new_item:
                    st.subheader("🆕 新品原價對照 (PChome 24h)")
                    
                    try:
                        clean_str = ai_price_range.replace(',', '')
                        prices = [int(n) for n in re.findall(r'\d+', clean_str)]
                        avg_used = sum(prices)/len(prices) if prices else 0
                        new_price = int(new_item['price'])
                        save_money = new_price - avg_used
                        
                        if save_money > 0:
                            st.info(f"🔥 買二手超划算！相比新品約可省下 **NT$ {int(save_money):,}**")
                    except:
                        pass

                    col_new_img, col_new_info = st.columns([1, 3])
                    with col_new_img:
                         if new_item['image']:
                            st.image(new_item['image'], use_container_width=True)
                    with col_new_info:
                        st.markdown(f"""
                        <div class="new-item">
                            <b style="color:#28a745;">[全新品] 目前售價</b><br>
                            <span style="font-size: 16px; color: #333;">{new_item['title']}</span><br>
                            <span style="font-size: 24px; color: #111; font-weight: bold;">NT$ {new_item['price']:,}</span><br>
                            <a href="{new_item['link']}" target="_blank">🔗 前往 PChome 賣場</a>
                        </div>
                        """, unsafe_allow_html=True)

                st.divider()

                # === 🚀 核心商業功能：一鍵上架 ===
                st.markdown("""
                <div style="background-color: #FFF3CD; padding: 20px; border-radius: 10px; border: 1px solid #FFEEBA; margin-bottom: 20px;">
                    <h3 style="color: #856404; margin: 0;">💰 滿意這個價格嗎？</h3>
                    <p style="color: #856404; margin-top: 5px;">我們的 AI 已經幫您準備好拍賣文案，現在上架，最快 24 小時內成交！</p>
                </div>
                """, unsafe_allow_html=True)

                with st.expander("📝 點擊展開「一鍵上架表單」 (AI 自動填寫)", expanded=True):
                    with st.form("sell_form"):
                        st.caption("以下資料由 AI 自動生成，您可以自由修改：")
                        
                        # 1. 自動帶入標題
                        default_title = f"【AI認證】{data.get('brand')} {data.get('model')} - {data.get('condition_score')}成新"
                        title = st.text_input("商品標題", value=default_title)
                        
                        # 2. 自動帶入價格
                        try:
                            clean_str = ai_price_range.replace(',', '')
                            prices = [int(n) for n in re.findall(r'\d+', clean_str)]
                            avg_price = int(sum(prices)/len(prices)) if prices else 500
                        except:
                            avg_price = 500
                        price = st.number_input("預售價格 (TWD)", value=avg_price, step=50)
                        
                        # 3. 自動生成文案
                        default_desc = f"""
商品型號：{data.get('model')}
新舊程度：{data.get('condition_score')}/10
專家短評：{data.get('analysis')}

此商品經由 SHM AI 智能鑑價系統認證。
                        """
                        desc = st.text_area("商品描述", value=default_desc.strip(), height=150)
                        
                        # 4. 收集賣家資料
                        col_contact1, col_contact2 = st.columns(2)
                        with col_contact1:
                            seller_name = st.text_input("您的稱呼")
                        with col_contact2:
                            contact_info = st.text_input("聯絡方式 (Line/Email)")
                        
                        # 送出按鈕
                        submitted = st.form_submit_button("🚀 確認上架")
                        
                        if submitted:
                            if not contact_info:
                                st.error("請填寫聯絡方式，以便買家聯繫您！")
                            else:
                                with st.spinner("🔄 正在安全寫入系統資料庫..."):
                                    try:
                                        # --- 1. 讀取隱藏金鑰 ---
                                        key_dict = json.loads(st.secrets["google_credentials"])
                                        scopes = [
                                            "https://www.googleapis.com/auth/spreadsheets",
                                            "https://www.googleapis.com/auth/drive"
                                        ]
                                        creds = Credentials.from_service_account_info(key_dict, scopes=scopes)
                                        client = gspread.authorize(creds)
                                        
                                        # --- 2. 連線到 Google Sheet ---
                                        sheet = client.open("SHM_Database").sheet1
                                        
                                        # --- 3. 整理要寫入的資料 ---
                                        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        row_data = [
                                            current_time,           # A欄: 時間
                                            title,                  # B欄: 標題
                                            str(price),             # C欄: 價格
                                            f"{data.get('condition_score')}/10", # D欄: 評分
                                            seller_name,            # E欄: 賣家稱呼
                                            contact_info,           # F欄: 聯絡方式
                                            desc                    # G欄: 描述
                                        ]
                                        
                                        # --- 4. 執行寫入動作 ---
                                        sheet.append_row(row_data)
                                        
                                        st.balloons() 
                                        st.success(f"""
                                        ✅ **上架成功！** 您的商品「{title}」已安全建檔進入雲端資料庫。
                                        我們將透過 {contact_info} 與您聯繫後續事宜。
                                        """)
                                        
                                    except Exception as e:
                                        st.error(f"❌ 資料庫連線失敗，請確認是否已給予機器人「編輯者」權限: {e}")

            except Exception as e:
                st.error(f"分析失敗: {e}")

with tab2:
    st.info("歷史紀錄功能開發中...")