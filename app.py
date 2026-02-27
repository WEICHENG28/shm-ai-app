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
import requests
import base64
import urllib.parse
import pandas as pd # 🆕 新增：用於數據分析與畫圖表

# 設定網頁標題
st.set_page_config(page_title="SHM 智能鑑價網", page_icon="💎", layout="wide")

# === 🎨 介面美化 ===
st.markdown("""
    <style>
    .stApp { background-color: #F0F2F6; }
    .metric-box { background-color: #FFFFFF; padding: 20px; border-radius: 12px; border-left: 5px solid #FF4B4B; box-shadow: 0 2px 6px rgba(0,0,0,0.08); margin-bottom: 10px; }
    .used-item { background-color: #FFFFFF; padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #E0E0E0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); color: #333333; }
    .new-item { background-color: #F9FFF9; padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #28a745; color: #333333; }
    .stButton>button { border-radius: 20px; font-weight: bold; }
    a {text-decoration: none; color: #0066CC !important;}
    a:hover {color: #FF4B4B !important;}
    h1, h2, h3 { color: #111111 !important; }
    
    /* 首頁專屬美化 */
    .hero-section { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 40px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    .hero-title { font-size: 2.5rem !important; font-weight: 800; color: white !important; margin-bottom: 15px;}
    .hero-subtitle { font-size: 1.2rem; color: #e0e0e0; margin-bottom: 20px; }
    .step-card { background-color: white; padding: 25px 20px; border-radius: 12px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05); height: 100%; border-top: 4px solid #FF4B4B;}
    </style>
    """, unsafe_allow_html=True)

# 標題區
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.markdown("<h1 style='text-align: center;'>💎</h1>", unsafe_allow_html=True)
with col_title:
    st.title("SHM 二手AI智能鑑價中心")
    st.markdown("##### 🚀 全台首創 · AI 視覺鑑價與無摩擦交易平台")

st.divider()

# 側邊欄
with st.sidebar:
    st.header("⚙️ 系統選單")
    st.success("🟢 系統狀態：連線正常")
    st.markdown("---")
    st.write("📸 **AI 拍攝指南**")
    st.caption("1. 確保光源充足，避免嚴重反光。")
    st.caption("2. 正面：確認商品款式與主體。")
    st.caption("3. 底部/標籤：確認確切型號 (極度關鍵!)")
    st.markdown("---")
    st.info("🛡️ 本平台由 AI 嚴格審查圖片品質，不合格之照片將無法進入鑑價與上架流程，敬請配合。")

# === 🆕 核心修改：加入「營運後台」分頁 ===
tab_home, tab1, tab2, tab_admin = st.tabs(["🏠 平台首頁", "📤 上傳鑑價", "🛒 二手尋寶商城", "📈 營運後台"])

# ==========================================
# 🏠 平台首頁 (Landing Page)
# ==========================================
with tab_home:
    st.markdown("""
    <div class="hero-section">
        <div class="hero-title">讓閒置好物，遇見對的人</div>
        <div class="hero-subtitle">全台第一套整合「AI 影像品管、精準大數據估價、一鍵自動上架」的智能平台</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 💡 簡單 4 步驟，立刻將好物變現")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_step1, col_step2, col_step3, col_step4 = st.columns(4)
    with col_step1:
        st.markdown("""
        <div class="step-card">
            <h1 style="margin:0; color:#FF4B4B;">📸 1</h1>
            <h4 style="margin-top:10px;">拍照上傳</h4>
            <p style="font-size: 13px; color: #666;">拍下商品正面與型號標籤，由 AI 進行嚴格影像品管，杜絕假圖與模糊照。</p>
        </div>
        """, unsafe_allow_html=True)
    with col_step2:
        st.markdown("""
        <div class="step-card">
            <h1 style="margin:0; color:#FF4B4B;">🧠 2</h1>
            <h4 style="margin-top:10px;">AI 精準鑑價</h4>
            <p style="font-size: 13px; color: #666;">結合視覺特徵與網路市場大數據，10 秒內給出最合理的二手成交價格區間。</p>
        </div>
        """, unsafe_allow_html=True)
    with col_step3:
        st.markdown("""
        <div class="step-card">
            <h1 style="margin:0; color:#FF4B4B;">🛒 3</h1>
            <h4 style="margin-top:10px;">一鍵自動上架</h4>
            <p style="font-size: 13px; color: #666;">AI 自動生成專業文案與智慧搜尋標籤，圖片自動上傳圖床，無縫進入商城。</p>
        </div>
        """, unsafe_allow_html=True)
    with col_step4:
        st.markdown("""
        <div class="step-card">
            <h1 style="margin:0; color:#FF4B4B;">🤝 4</h1>
            <h4 style="margin-top:10px;">買賣無縫對接</h4>
            <p style="font-size: 13px; color: #666;">買家透過商城專屬「一鍵發信按鈕」直達賣家信箱，去除所有溝通摩擦力。</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.info("👈 **準備好體驗了嗎？請點擊上方的「📤 上傳鑑價」分頁開始測試，或是進入「🛒 二手尋寶商城」尋找好物！**")


# ==========================================
# 📤 上傳鑑價區塊 (Tab 1)
# ==========================================
with tab1:
    if not os.path.exists("test_data"):
        os.makedirs("test_data")

    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0
    
    col_upload, col_empty = st.columns([2, 1])
    with col_upload:
        uploaded_files = st.file_uploader(
            "拖曳或點擊上傳商品照片...", 
            type=["jpg", "png", "jpeg"], 
            accept_multiple_files=True,
            key=f"uploader_{st.session_state.uploader_key}"
        )

    if "analysis_done" not in st.session_state:
        st.session_state.analysis_done = False

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
                status_text.text("🔍 AI 正在進行影像品質與特徵審查...")
                progress_bar.progress(30)
                raw_result = ai_engine.analyze_multiple_items(saved_paths)
                json_str = raw_result.replace("```json", "").replace("```", "").strip()
                data = json.loads(json_str)
                
                if not data.get('is_qualified', True):
                    progress_bar.empty()
                    status_text.empty()
                    st.error(f"❌ **AI 影像審查未通過：** {data.get('rejection_reason')}")
                    st.warning("💡 為了確保平台鑑價公信力，請根據上述提示重新拍攝，並再次上傳照片。")
                    st.stop()
                
                raw_tags = data.get('tags', '')
                if isinstance(raw_tags, list):
                    data['tags'] = " ".join(raw_tags)
                elif isinstance(raw_tags, str):
                    data['tags'] = raw_tags.replace("'", "").replace('"', "").replace("[", "").replace("]", "").replace(",", " ")

                status_text.text("📊 正在分析二手市場行情 & 比對新品價格...")
                progress_bar.progress(60)
                raw_model = data.get('model', '')
                clean_model = raw_model.split('(')[0].strip()
                search_query = f"{data.get('brand')} {clean_model}"
                
                ai_price_range = data.get('estimated_price_range', 'NT$500 - NT$1000')
                used_items = scraper.get_used_market_data(search_query, ai_price_range)
                new_item = scraper.get_new_price_pchome(search_query)
                
                st.session_state.data = data
                st.session_state.search_query = search_query
                st.session_state.ai_price_range = ai_price_range
                st.session_state.used_items = used_items
                st.session_state.new_item = new_item
                st.session_state.main_image_path = saved_paths[0] if saved_paths else None
                st.session_state.analysis_done = True
                
                progress_bar.progress(100)
                status_text.text("✅ 分析完成！")
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()
                
            except Exception as e:
                st.error(f"分析失敗: {e}")

        if st.session_state.analysis_done:
            data = st.session_state.data
            search_query = st.session_state.search_query
            ai_price_range = st.session_state.ai_price_range
            used_items = st.session_state.used_items
            new_item = st.session_state.new_item

            st.success(f"🎉 辨識成功：{data.get('brand')} {data.get('model')}")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""<div class="metric-box"><h4>❤️ 新舊評分</h4><h1 style="color:#FF4B4B;">{data.get('condition_score')}/10</h1></div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""<div class="metric-box"><h4>💰 二手估價 (TWD)</h4><h2 style="color:#28a745;">{data.get('estimated_price_range')}</h2></div>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""<div class="metric-box"><h4>🧐 專家簡評</h4><p style="color:#555;">{data.get('analysis')}</p></div>""", unsafe_allow_html=True)
            
            st.divider()

            st.subheader("📉 二手市場成交參考")
            u_col1, u_col2 = st.columns(2)
            for i, item in enumerate(used_items):
                if i < 4:
                    with (u_col1 if i % 2 == 0 else u_col2):
                        st.markdown(f"""
                        <div class="used-item">
                            <span style="background-color: #E0E0E0; color: #333; padding: 2px 8px; border-radius: 4px; font-size: 11px;">{item['platform']}</span>
                            <span style="float: right; color: #666; font-size: 12px;">{item['tag']}</span>
                            <br><b style="color:#222; font-size: 15px;">{item['title']}</b><br>
                            <span style="font-size: 20px; color: #D93025; font-weight: bold;">NT$ {item['price']:,}</span><br>
                        </div>""", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
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
                    </div>""", unsafe_allow_html=True)

            st.divider()

            st.markdown("""
            <div style="background-color: #FFF3CD; padding: 20px; border-radius: 10px; border: 1px solid #FFEEBA; margin-bottom: 20px;">
                <h3 style="color: #856404; margin: 0;">💰 滿意這個價格嗎？</h3>
                <p style="color: #856404; margin-top: 5px;">我們的 AI 已經幫您準備好拍賣文案，現在上架，最快 24 小時內成交！</p>
            </div>""", unsafe_allow_html=True)

            with st.expander("📝 點擊展開「一鍵上架表單」 (AI 自動填寫)", expanded=True):
                with st.form("sell_form"):
                    st.caption("以下資料由 AI 自動生成，您可以自由修改：")
                    
                    default_title = f"【AI認證】{data.get('brand')} {data.get('model')} - {data.get('condition_score')}成新"
                    title = st.text_input("商品標題", value=default_title)
                    
                    try:
                        clean_str = ai_price_range.replace(',', '')
                        prices = [int(n) for n in re.findall(r'\d+', clean_str)]
                        if len(prices) >= 2:
                            min_price = min(prices)
                            max_price = max(prices)
                        elif len(prices) == 1:
                            min_price = prices[0]
                            max_price = prices[0] * 2
                        else:
                            min_price, max_price = 0, 100000
                            
                        avg_price = int(sum(prices)/len(prices)) if prices else 500
                        if avg_price < min_price: avg_price = min_price
                        if avg_price > max_price: avg_price = max_price
                    except:
                        min_price, max_price, avg_price = 0, 100000, 500
                    
                    st.info(f"🛡️ **為確保平台公信力，您的定價必須符合 AI 鑑價區間：NT$ {min_price} - {max_price}**")
                    
                    price = st.number_input(
                        "💰 您的最終上架價格 (TWD)", 
                        min_value=min_price, 
                        max_value=max_price, 
                        value=avg_price, 
                        step=50
                    )
                    
                    default_desc = f"""
商品型號：{data.get('model')}
新舊程度：{data.get('condition_score')}/10
專家短評：{data.get('analysis')}
分類標籤：{data.get('tags', '#無標籤')}

此商品經由 SHM AI 智能鑑價系統認證。"""
                    desc = st.text_area("商品描述", value=default_desc.strip(), height=150)
                    
                    col_contact1, col_contact2 = st.columns(2)
                    with col_contact1:
                        seller_name = st.text_input("您的稱呼")
                    with col_contact2:
                        contact_info = st.text_input("聯絡方式 (建議填寫 Email 啟用一鍵發信，或填 Line ID/電話)")
                    
                    submitted = st.form_submit_button("🚀 確認上架")
                    
                    if submitted:
                        if not contact_info:
                            st.error("請填寫聯絡方式，以便買家聯繫您！")
                        else:
                            with st.spinner("🔄 正在上傳圖片與寫入資料庫..."):
                                try:
                                    img_url = ""
                                    if "main_image_path" in st.session_state and os.path.exists(st.session_state.main_image_path):
                                        with open(st.session_state.main_image_path, "rb") as f:
                                            img_bytes = f.read()
                                        payload = {
                                            "key": st.secrets["IMGBB_API_KEY"],
                                            "image": base64.b64encode(img_bytes).decode('utf-8')
                                        }
                                        res = requests.post("https://api.imgbb.com/1/upload", data=payload)
                                        if res.status_code == 200:
                                            img_url = res.json()['data']['url']
                                    
                                    key_dict = json.loads(st.secrets["google_credentials"])
                                    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
                                    creds = Credentials.from_service_account_info(key_dict, scopes=scopes)
                                    client = gspread.authorize(creds)
                                    sheet = client.open("SHM_Database").sheet1
                                    
                                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    row_data = [current_time, title, str(price), f"{data.get('condition_score')}/10", seller_name, contact_info, desc, img_url, "上架中"]
                                    sheet.append_row(row_data)
                                    
                                    st.balloons() 
                                    st.success(f"✅ **上架成功！** 您的商品「{title}」已安全建檔進入雲端資料庫。畫面將在 3 秒後自動重置。")
                                    
                                    time.sleep(3)
                                    st.session_state.analysis_done = False
                                    st.session_state.uploader_key += 1 
                                    st.rerun()
                                    
                                except Exception as e:
                                    st.error(f"❌ 上架失敗，請檢查設定: {e}")

# ==========================================
# 🛒 二手商城區塊 (Tab 2)
# ==========================================
with tab2:
    st.header("🛒 二手尋寶商城")
    st.caption("這裡展示了平台上所有經過 AI 鑑價認證的二手好物！")
    
    if st.button("🔄 刷新商城商品"):
        st.rerun()

    try:
        key_dict = json.loads(st.secrets["google_credentials"])
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(key_dict, scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open("SHM_Database").sheet1
        records = sheet.get_all_records() 
        
        for idx, r in enumerate(records):
            r['sheet_row'] = idx + 2

        if not records:
            st.info("目前商城還沒有商品，趕快去上架第一個商品吧！")
        else:
            st.markdown("### 🔍 篩選商品")
            with st.container():
                col_search, col_price, col_score = st.columns(3)
                with col_search:
                    search_term = st.text_input("關鍵字搜尋", placeholder="例如：PUMA, 滑鼠...")
                with col_price:
                    max_price = st.number_input("最高預算 (NT$)", min_value=0, value=10000, step=100)
                with col_score:
                    min_score = st.slider("最低新舊評分", min_value=1.0, max_value=10.0, value=1.0, step=0.5)
            
            show_sold = st.checkbox("👁️ 顯示已售出商品 (歷史成交參考)", value=False)
            
            st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)

            filtered_records = []
            for item in reversed(records):
                status = str(item.get('商品狀態', '上架中'))
                if status == '已售出' and not show_sold:
                    continue 
                
                title = str(item.get('商品標題', '')).lower()
                desc = str(item.get('描述', '')).lower()
                if search_term and search_term.lower() not in title and search_term.lower() not in desc:
                    continue
                
                try:
                    price = int(str(item.get('預售價格', '0')).replace(',', ''))
                except:
                    price = 0
                if price > max_price:
                    continue
                
                try:
                    score_str = str(item.get('評分', '0/10')).split('/')[0]
                    score = float(score_str)
                except:
                    score = 0.0
                if score < min_score:
                    continue
                
                filtered_records.append(item)

            if not filtered_records:
                st.warning("找不到符合條件的商品，請調整上面的篩選條件喔！")
            else:
                cols = st.columns(3)
                for i, item in enumerate(filtered_records):
                    with cols[i % 3]:
                        img_src = item.get('圖片網址', '')
                        contact_info = str(item.get('聯絡方式', ''))
                        item_title = str(item.get('商品標題', '未命名商品'))
                        item_price = str(item.get('預售價格', '0'))
                        status = str(item.get('商品狀態', '上架中'))
                        
                        if status == '已售出':
                            card_style = "background-color: #f8f9fa; padding: 15px; border-radius: 12px; border: 1px solid #ddd; margin-bottom: 20px; opacity: 0.6; filter: grayscale(80%); position: relative;"
                            stamp_html = '<div style="position: absolute; top: 30px; right: 10px; background-color: #555; color: white; padding: 5px 15px; font-weight: bold; transform: rotate(15deg); border-radius: 5px; font-size: 14px; letter-spacing: 2px; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.2); z-index: 10;">SOLD</div>'
                            img_html = f'<img src="{img_src}" style="width: 100%; height: 200px; object-fit: cover; border-radius: 8px; margin-bottom: 10px;">' if img_src else '<div style="width: 100%; height: 200px; background-color: #f0f2f6; border-radius: 8px; margin-bottom: 10px; display: flex; align-items: center; justify-content: center; color: #aaa;">無圖片</div>'
                            contact_html = f'<div style="width: 100%; text-align: center; background-color: #ddd; color: #666; padding: 10px 0; border-radius: 8px; font-weight: bold; margin-top: 15px;">🚫 商品已售出</div>'
                        else:
                            card_style = "background-color: white; padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 5px; border: 1px solid #E0E0E0; position: relative;"
                            stamp_html = ''
                            img_html = f'<img src="{img_src}" style="width: 100%; height: 200px; object-fit: cover; border-radius: 8px; margin-bottom: 10px;">' if img_src else '<div style="width: 100%; height: 200px; background-color: #f0f2f6; border-radius: 8px; margin-bottom: 10px; display: flex; align-items: center; justify-content: center; color: #aaa;">無圖片</div>'
                            
                            if "@" in contact_info:
                                mail_subject = f"【SHM 智能鑑價網】我想購買您的「{item_title}」"
                                mail_body = f"您好！\n\n我在 SHM AI 認證平台上看到您上架的商品：「{item_title}」，售價為 NT$ {item_price}。\n請問商品還在嗎？希望能與您進一步討論交易細節，謝謝！"
                                safe_subject = urllib.parse.quote(mail_subject)
                                safe_body = urllib.parse.quote(mail_body)
                                gmail_link = f"https://mail.google.com/mail/?view=cm&fs=1&to={contact_info}&su={safe_subject}&body={safe_body}"
                                contact_html = f'<a href="{gmail_link}" target="_blank" style="display: block; width: 100%; text-align: center; background-color: #EA4335; color: white; padding: 10px 0; border-radius: 8px; font-weight: bold; text-decoration: none; margin-top: 15px;">✉️ 開啟 Gmail 聯絡賣家</a>'
                            elif contact_info:
                                contact_html = f'<div style="width: 100%; text-align: center; background-color: #E8F0FE; color: #1967D2; padding: 10px 0; border-radius: 8px; font-weight: bold; margin-top: 15px; border: 1px solid #D2E3FC;">📱 Line/電話：{contact_info}</div>'
                            else:
                                contact_html = f'<div style="width: 100%; text-align: center; background-color: #F8F9FA; color: #aaa; padding: 10px 0; border-radius: 8px; font-weight: bold; margin-top: 15px; border: 1px solid #E0E0E0;">🚫 未提供聯絡方式</div>'

                        st.markdown(
f"""<div style="{card_style}">
{stamp_html}
{img_html}
<span style="background-color: #FF4B4B; color: white; padding: 3px 8px; border-radius: 15px; font-size: 12px; font-weight: bold;">{item.get('評分', 'N/A')}</span>
<h4 style="margin-top: 10px; color: #333; font-size: 16px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{item_title}">{item_title}</h4>
<h2 style="color: #28a745; margin: 10px 0;">NT$ {item_price}</h2>
<p style="font-size: 13px; color: #666; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 5px;">{item.get('描述', '無商品描述')}</p>
<hr style="margin: 10px 0;">
<p style="font-size: 12px; color: #888; margin: 0;">👤 賣家：{item.get('賣家稱呼', '匿名')}</p>
{contact_html}
</div>""", 
                        unsafe_allow_html=True)
                        
                        if status != '已售出':
                            with st.expander("⚙️ 管理商品 (標記售出)", expanded=False):
                                verify_contact = st.text_input("請輸入您上架時留的聯絡方式以驗證：", key=f"verify_{i}_{item.get('sheet_row')}")
                                if st.button("✅ 確認標記為已售出", key=f"btn_sold_{i}_{item.get('sheet_row')}"):
                                    if verify_contact == contact_info:
                                        with st.spinner("正在更新商品狀態..."):
                                            try:
                                                sheet.update_cell(item['sheet_row'], 9, "已售出")
                                                st.success("成功！此商品已標記為售出。")
                                                time.sleep(1)
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"更新失敗，請檢查權限: {e}")
                                    else:
                                        st.error("驗證失敗：聯絡方式不符，無法修改此商品狀態！")
                        else:
                            st.markdown("<br>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"無法讀取商城資料，請檢查資料庫連線或表頭設定：{e}")

# ==========================================
# 📈 營運後台區塊 (Tab Admin)
# ==========================================
with tab_admin:
    st.header("📈 平台營運後台")
    st.caption("此區塊僅供平台管理員查看營運數據。")
    
    # 簡單的密碼鎖
    admin_pwd = st.text_input("請輸入管理員密碼解鎖：", type="password")
    
    # 預設密碼設為：shm_admin (你可以自己改)
    if admin_pwd == "shm_admin":
        st.success("解鎖成功！歡迎回來，老闆。")
        st.divider()
        
        try:
            # 讀取資料庫
            key_dict = json.loads(st.secrets["google_credentials"])
            scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_service_account_info(key_dict, scopes=scopes)
            client = gspread.authorize(creds)
            sheet = client.open("SHM_Database").sheet1
            records = sheet.get_all_records()
            
            if not records:
                st.info("目前還沒有任何營運數據。")
            else:
                # 使用 pandas 將資料轉換成容易處理的格式
                df = pd.DataFrame(records)
                
                # 計算核心營運指標
                total_items = len(df)
                sold_items = len(df[df['商品狀態'] == '已售出'])
                active_items = total_items - sold_items
                
                # 計算總價值 (需要把字串 NT$ 1,000 變成純數字)
                total_value = 0
                for price_str in df['預售價格']:
                    try:
                        clean_price = int(str(price_str).replace(',', ''))
                        total_value += clean_price
                    except:
                        pass
                
                # 顯示頂部大數字指標
                st.subheader("💡 核心營運指標 (KPI)")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("平台總商品數", f"{total_items} 件")
                col2.metric("架上流通商品", f"{active_items} 件")
                col3.metric("已售出商品", f"{sold_items} 件")
                col4.metric("累計商品總價值 (GMV)", f"NT$ {total_value:,}")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # 畫圖表
                st.subheader("📊 數據視覺化分析")
                chart_col1, chart_col2 = st.columns(2)
                
                with chart_col1:
                    st.write("**商品狀態分佈**")
                    status_counts = df['商品狀態'].value_counts()
                    st.bar_chart(status_counts, color="#FF4B4B")
                    
                with chart_col2:
                    st.write("**最新上架紀錄 (前 5 筆)**")
                    recent_df = df[['上架時間', '商品標題', '預售價格', '商品狀態']].tail(5).iloc[::-1]
                    st.dataframe(recent_df, use_container_width=True, hide_index=True)
                    
        except Exception as e:
            st.error(f"無法讀取後台資料：{e}")
            
    elif admin_pwd:
        st.error("密碼錯誤，請重新輸入！")