import streamlit as st
import streamlit.components.v1 as components
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
import pandas as pd
from PIL import Image
from collections import Counter # 🆕 新增：用來計算熱門標籤

# 設定網頁標題
st.set_page_config(page_title="SHM 智能鑑價網", page_icon="💎", layout="wide")

# === Session State 初始化 ===
if "selected_item" not in st.session_state:
    st.session_state.selected_item = None
if "search_input" not in st.session_state:
    st.session_state.search_input = ""
if "display_count" not in st.session_state:
    st.session_state.display_count = 20 # 預設顯示 20 筆

def back_to_market():
    st.session_state.selected_item = None

def load_more():
    st.session_state.display_count += 20

def set_search_tag(tag):
    st.session_state.search_input = tag
    st.session_state.display_count = 20 # 重置顯示數量

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
    
    .hero-section { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 40px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    .hero-title { font-size: 2.5rem !important; font-weight: 800; color: white !important; margin-bottom: 15px;}
    .hero-subtitle { font-size: 1.2rem; color: #e0e0e0; margin-bottom: 20px; }
    .step-card { background-color: white; padding: 25px 20px; border-radius: 12px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05); height: 100%; border-top: 4px solid #FF4B4B;}
    
    [data-baseweb="input"], [data-baseweb="textarea"] {
        background-color: #FFFFFF !important;
        border: 2px solid #D1D5DB !important;
        border-radius: 8px !important;
        transition: border-color 0.3s;
    }
    [data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within {
        border-color: #FF4B4B !important;
    }
    
    .marketplace-img {
        width: 100%; 
        height: 200px; 
        object-fit: cover; 
        border-radius: 8px; 
        margin-bottom: 10px;
    }
    /* 標籤按鈕特效 */
    .tag-btn { margin-right: 5px; margin-bottom: 5px; }
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

# 分頁設定
tab_home, tab1, tab2, tab_seller = st.tabs(["🏠 平台首頁", "📤 上傳鑑價", "🛒 二手尋寶商城", "📦 賣家中心"])

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
            file_name_no_ext = os.path.splitext(uploaded_file.name)[0]
            file_path = os.path.join("test_data", f"{file_name_no_ext}_compressed.jpg")
            
            img = Image.open(uploaded_file)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.thumbnail((800, 800))
            img.save(file_path, "JPEG", quality=80)
            
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
                st.session_state.all_image_paths = saved_paths 
                st.session_state.analysis_done = True
                
                progress_bar.progress(100)
                status_text.text("✅ 分析完成！")
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()
                
            except Exception as e:
                error_msg = str(e).lower()
                if "429" in error_msg or "quota" in error_msg:
                    st.error("⏳ 目前全站使用人數較多，AI 鑑價伺服器暫時滿載！請等待約 1 分鐘後再重新點擊分析。")
                else:
                    st.error(f"❌ 分析失敗，請檢查照片或重試: {e}")

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
            
            with st.expander("📝 點擊展開「一鍵上架表單」 (AI 自動填寫)", expanded=True):
                with st.form("sell_form"):
                    st.caption("以下資料由 AI 自動生成，您可以自由修改：")
                    
                    default_title = f"【AI認證】{data.get('brand')} {data.get('model')} - {data.get('condition_score')}成新"
                    title = st.text_input("商品標題", value=default_title)
                    
                    try:
                        clean_str = ai_price_range.replace(',', '')
                        prices = [int(n) for n in re.findall(r'\d+', clean_str)]
                        min_price, max_price = (min(prices), max(prices)) if len(prices)>=2 else (prices[0], prices[0]*2) if len(prices)==1 else (0, 100000)
                        avg_price = int(sum(prices)/len(prices)) if prices else 500
                    except:
                        min_price, max_price, avg_price = 0, 100000, 500
                    
                    st.info(f"🛡️ **為確保平台公信力，您的定價必須符合 AI 鑑價區間：NT$ {min_price} - {max_price}**")
                    
                    price = st.number_input("💰 您的最終上架價格 (TWD)", min_value=min_price, max_value=max_price, value=avg_price, step=50)
                    
                    default_desc = f"商品型號：{data.get('model')}\n新舊程度：{data.get('condition_score')}/10\n專家短評：{data.get('analysis')}\n分類標籤：{data.get('tags', '#無標籤')}\n\n此商品經由 SHM AI 智能鑑價系統認證。"
                    desc = st.text_area("商品描述", value=default_desc.strip(), height=150)
                    
                    col_contact1, col_contact2 = st.columns(2)
                    with col_contact1:
                        seller_name = st.text_input("您的稱呼")
                    with col_contact2:
                        contact_info = st.text_input("聯絡方式 (建議填寫 Email 啟用一鍵發信，或填 Line ID)")
                    
                    submitted = st.form_submit_button("🚀 確認上架")
                    
                    if submitted:
                        if not contact_info:
                            st.error("請填寫聯絡方式，以便買家聯繫您！")
                        else:
                            with st.spinner("🔄 正在打包上傳您的多張商品圖片... 請稍候..."):
                                try:
                                    uploaded_img_urls = []
                                    if "all_image_paths" in st.session_state and st.session_state.all_image_paths:
                                        for path in st.session_state.all_image_paths:
                                            if os.path.exists(path):
                                                with open(path, "rb") as f:
                                                    img_bytes = f.read()
                                                res = requests.post("https://api.imgbb.com/1/upload", data={"key": st.secrets["IMGBB_API_KEY"], "image": base64.b64encode(img_bytes).decode('utf-8')})
                                                if res.status_code == 200:
                                                    uploaded_img_urls.append(res.json()['data']['url'])
                                    
                                    final_img_string = ",".join(uploaded_img_urls)
                                    
                                    key_dict = json.loads(st.secrets["google_credentials"])
                                    creds = Credentials.from_service_account_info(key_dict, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
                                    client = gspread.authorize(creds)
                                    sheet = client.open("SHM_Database").sheet1
                                    
                                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    sheet.append_row([current_time, title, str(price), f"{data.get('condition_score')}/10", seller_name, contact_info, desc, final_img_string, "上架中"])
                                    
                                    st.balloons() 
                                    st.success(f"✅ **上架成功！** 您的商品「{title}」已安全建檔進入雲端資料庫。")
                                    time.sleep(3)
                                    st.session_state.analysis_done = False
                                    st.session_state.uploader_key += 1 
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ 上架失敗，請檢查設定: {e}")

# ==========================================
# 🛒 二手商城區塊 (Tab 2)
# ==========================================
# === 取得與清理資料函數 ===
def fetch_and_clean_data():
    key_dict = json.loads(st.secrets["google_credentials"])
    creds = Credentials.from_service_account_info(key_dict, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
    client = gspread.authorize(creds)
    sheet = client.open("SHM_Database").sheet1
    records = sheet.get_all_records() 
    
    cleaned_records = []
    now = datetime.now()
    for idx, r in enumerate(records):
        r['sheet_row'] = idx + 2
        # === 🆕 核心升級 1：30 天自動過期機制 ===
        status = str(r.get('商品狀態', '上架中'))
        if status != '已售出':
            try:
                upload_time = datetime.strptime(str(r.get('上架時間', '')), "%Y-%m-%d %H:%M:%S")
                if (now - upload_time).days > 30:
                    r['商品狀態'] = '已過期'
            except: pass
        cleaned_records.append(r)
    return cleaned_records, sheet

with tab2:
    if st.session_state.selected_item is not None:
        components.html("<script>window.parent.scrollTo({top: 0, behavior: 'smooth'});</script>", height=0)
        item = st.session_state.selected_item
        
        st.button("⬅️ 返回商城列表", on_click=back_to_market)
        st.divider()
        
        col_img, col_details = st.columns([1, 1.2])
        
        with col_img:
            all_imgs = [url.strip() for url in str(item.get('圖片網址', '')).split(',') if url.strip()]
            if all_imgs:
                gallery_html = f"""
                <!DOCTYPE html><html><head><style>
                    body {{ margin: 0; font-family: sans-serif; }}
                    .main-img-container {{ width: 100%; height: 400px; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 15px; background-color: #f8f9fa; display: flex; justify-content: center; align-items: center; }}
                    .main-img {{ max-width: 100%; max-height: 100%; object-fit: contain; }}
                    .thumb-container {{ display: flex; gap: 12px; overflow-x: auto; padding: 5px 2px; }}
                    .thumb-img {{ width: 75px; height: 75px; object-fit: cover; border-radius: 8px; border: 2px solid transparent; cursor: pointer; transition: all 0.2s ease; opacity: 0.7; }}
                    .thumb-img:hover, .thumb-img.active {{ border-color: #FF4B4B; opacity: 1; }}
                    .thumb-container::-webkit-scrollbar {{ display: none; }}
                </style>
                <script>
                    function changeMainImg(element, src) {{
                        document.getElementById('mainImage').src = src;
                        var thumbs = document.getElementsByClassName('thumb-img');
                        for (var i = 0; i < thumbs.length; i++) thumbs[i].classList.remove('active');
                        element.classList.add('active');
                    }}
                </script></head><body>
                <div class="main-img-container"><img id="mainImage" class="main-img" src="{all_imgs[0]}"></div>
                <div class="thumb-container">
                """
                for i, img_url in enumerate(all_imgs):
                    active_class = " active" if i == 0 else ""
                    gallery_html += f'<img class="thumb-img{active_class}" src="{img_url}" onmouseover="changeMainImg(this, \'{img_url}\')" onclick="changeMainImg(this, \'{img_url}\')">'
                gallery_html += "</div></body></html>"
                components.html(gallery_html, height=550)
            else:
                st.info("此商品未提供圖片")
                
        with col_details:
            status = str(item.get('商品狀態', '上架中'))
            score = item.get('評分', 'N/A')
            title = item.get('商品標題', '未命名商品')
            price = item.get('預售價格', '0')
            contact_info = str(item.get('聯絡方式', ''))
            
            st.markdown(f"""
            <span style="background-color: #FF4B4B; color: white; padding: 4px 12px; border-radius: 20px; font-size: 14px; font-weight: bold;">評分 {score}</span>
            <h2 style="margin-top: 10px; color: #222;">{title}</h2>
            <div style="background-color: #F8F9FA; padding: 20px; border-radius: 10px; margin: 15px 0; border: 1px solid #E0E0E0;">
                <p style="margin: 0; color: #666; font-size: 14px;">直購價</p>
                <h1 style="color: #FF4B4B; margin: 0; font-size: 36px;">NT$ {price}</h1>
            </div>
            **👤 賣家：** {item.get('賣家稱呼', '匿名')}<br>
            **🕒 上架時間：** {item.get('上架時間', '未知')}
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if status == '已售出':
                st.markdown('<div style="background-color: #ddd; color: #666; text-align: center; padding: 15px; border-radius: 8px; font-weight: bold; font-size: 18px; letter-spacing: 2px;">🛑 此商品已售出</div>', unsafe_allow_html=True)
            elif status == '已過期':
                st.markdown('<div style="background-color: #FFF3CD; color: #856404; text-align: center; padding: 15px; border-radius: 8px; font-weight: bold; font-size: 18px; letter-spacing: 2px;">⚠️ 此商品已超過 30 天未更新，自動隱藏</div>', unsafe_allow_html=True)
            else:
                if "@" in contact_info:
                    mail_subject, mail_body = urllib.parse.quote(f"【SHM 智能鑑價網】我想購買您的「{title}」"), urllib.parse.quote(f"您好！我在 SHM AI 認證平台上看到您的商品：「{title}」，請問還在嗎？")
                    st.markdown(f'<a href="https://mail.google.com/mail/?view=cm&fs=1&to={contact_info}&su={mail_subject}&body={mail_body}" target="_blank" style="display: block; width: 100%; text-align: center; background-color: #EA4335; color: white; padding: 15px 0; border-radius: 8px; font-weight: bold; font-size: 18px; text-decoration: none;">✉️ 立即發送 Email 聯絡賣家</a>', unsafe_allow_html=True)
                elif contact_info:
                    st.markdown(f'<div style="width: 100%; text-align: center; background-color: #E8F0FE; color: #1967D2; padding: 15px 0; border-radius: 8px; font-weight: bold; font-size: 18px; border: 1px solid #D2E3FC;">📱 賣家聯絡方式：{contact_info}</div>', unsafe_allow_html=True)

            # === 🆕 核心升級 3：歷史價格分佈圖 ===
            try:
                all_records, _ = fetch_and_clean_data()
                # 抓取標題前兩個字作為關鍵字比對
                title_words = title.split()
                search_key = f"{title_words[0]} {title_words[1]}".lower() if len(title_words) >= 2 else title_words[0].lower() if title_words else ""
                
                history_data = []
                for r in all_records:
                    if search_key and search_key in str(r.get('商品標題', '')).lower():
                        try:
                            p = int(str(r.get('預售價格', '0')).replace(',', ''))
                            t = pd.to_datetime(r.get('上架時間'))
                            # 簡化狀態顯示
                            state = "已售出" if r.get('商品狀態') == '已售出' else "上架/過期"
                            history_data.append({"時間": t, "價格": p, "狀態": state})
                        except: pass
                
                if len(history_data) > 1: # 有兩筆以上才畫圖
                    st.divider()
                    st.markdown("#### 📊 同款商品歷史價格分佈")
                    st.caption(f"系統自動抓取標題含有「{search_key}」的商品進行大數據比對。")
                    df_hist = pd.DataFrame(history_data).sort_values("時間")
                    st.scatter_chart(df_hist, x="時間", y="價格", color="狀態")
            except: pass

            st.divider()
            st.markdown("#### 📝 商品詳細描述")
            st.write(item.get('描述', '無商品描述'))

    else:
        st.header("🛒 二手尋寶商城")
        st.caption("點擊下方商品卡片，即可查看多張實拍圖與商品詳情！")
        
        try:
            records, _ = fetch_and_clean_data()
            
            if not records:
                st.info("目前商城還沒有商品，趕快去上架第一個商品吧！")
            else:
                # === 🆕 核心升級 2：熱門標籤快速篩選 ===
                all_tags = []
                for r in records:
                    if r.get('商品狀態') not in ['已售出', '已過期']:
                        tags = re.findall(r'#\S+', str(r.get('描述', '')))
                        all_tags.extend(tags)
                
                top_tags = [t[0] for t in Counter(all_tags).most_common(6)]
                
                if top_tags:
                    st.markdown("🔥 **熱門分類：**")
                    tag_cols = st.columns(len(top_tags) + 1)
                    for i, tag in enumerate(top_tags):
                        with tag_cols[i]:
                            if st.button(tag, use_container_width=True):
                                set_search_tag(tag)
                    with tag_cols[-1]:
                        if st.button("🔄 清除過濾", use_container_width=True):
                            set_search_tag("")
                
                st.markdown("<br>", unsafe_allow_html=True)

                with st.container():
                    col_search, col_price, col_score = st.columns(3)
                    with col_search:
                        # 將搜尋框綁定到 session_state
                        search_term = st.text_input("關鍵字搜尋 (支援文字與標籤)", value=st.session_state.search_input, key="search_input")
                    with col_price:
                        max_price = st.number_input("最高預算 (NT$)", min_value=0, value=100000, step=100)
                    with col_score:
                        min_score = st.slider("最低新舊評分", min_value=1.0, max_value=10.0, value=1.0, step=0.5)
                
                show_sold = st.checkbox("👁️ 顯示已售出商品 (歷史成交參考)", value=False)
                st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)

                filtered_records = []
                for item in reversed(records):
                    status = str(item.get('商品狀態', '上架中'))
                    
                    # 過濾狀態
                    if status == '已過期': continue
                    if status == '已售出' and not show_sold: continue 
                    
                    # 過濾關鍵字
                    title = str(item.get('商品標題', '')).lower()
                    desc = str(item.get('描述', '')).lower()
                    if search_term and search_term.lower() not in title and search_term.lower() not in desc:
                        continue
                    
                    # 過濾價格與評分
                    try:
                        if int(str(item.get('預售價格', '0')).replace(',', '')) > max_price: continue
                        if float(str(item.get('評分', '0/10')).split('/')[0]) < min_score: continue
                    except: pass
                    
                    filtered_records.append(item)

                if not filtered_records:
                    st.warning("找不到符合條件的商品，請調整上面的篩選條件喔！")
                else:
                    # === 🆕 核心升級 4：分頁/延遲載入系統 ===
                    displayed_records = filtered_records[:st.session_state.display_count]
                    
                    cols = st.columns(4) 
                    for i, item in enumerate(displayed_records):
                        with cols[i % 4]:
                            with st.container(border=True): 
                                all_imgs = [url.strip() for url in str(item.get('圖片網址', '')).split(',') if url.strip()]
                                img_src = all_imgs[0] if all_imgs else ''
                                status = str(item.get('商品狀態', '上架中'))
                                
                                if status == '已售出':
                                    st.markdown(f'<div style="position: relative;"><div style="position: absolute; top: 10px; right: 5px; background-color: #555; color: white; padding: 3px 10px; font-weight: bold; transform: rotate(15deg); border-radius: 5px; font-size: 12px; z-index: 10; border: 1px solid white;">SOLD</div><img src="{img_src}" class="marketplace-img" style="opacity: 0.5; filter: grayscale(80%);"></div>', unsafe_allow_html=True)
                                else:
                                    if img_src: st.markdown(f'<img src="{img_src}" class="marketplace-img">', unsafe_allow_html=True)
                                    else: st.markdown('<div class="marketplace-img" style="background-color: #f0f2f6; display: flex; align-items: center; justify-content: center; color: #aaa;">無圖片</div>', unsafe_allow_html=True)
                                
                                st.markdown(f"<div style='font-size: 14px; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #333;' title=\"{item.get('商品標題', '未命名')}\">{item.get('商品標題', '未命名')}</div>", unsafe_allow_html=True)
                                st.markdown(f"<div style='color: #FF4B4B; font-size: 18px; font-weight: bold; margin-top: 5px;'>NT$ {item.get('預售價格', '0')}</div>", unsafe_allow_html=True)
                                
                                if st.button("🔍 查看詳情", key=f"view_{item['sheet_row']}", use_container_width=True):
                                    st.session_state.selected_item = item
                                    st.rerun()

                    # 載入更多按鈕
                    st.markdown("<br>", unsafe_allow_html=True)
                    if len(filtered_records) > st.session_state.display_count:
                        col_space1, col_btn, col_space2 = st.columns([1, 1, 1])
                        with col_btn:
                            st.button("⬇️ 載入更多商品", on_click=load_more, use_container_width=True)

        except Exception as e:
            st.error(f"無法讀取商城資料，請檢查資料庫連線或表頭設定：{e}")

# ==========================================
# 📦 賣家專屬中心區塊 (Tab Seller)
# ==========================================
with tab_seller:
    st.header("📦 賣家專屬中心")
    st.caption("請輸入您的聯絡方式，查看並管理您專屬的商品營運數據。")
    
    seller_id = st.text_input("🔑 請輸入您上架時使用的聯絡方式 (Email/電話/Line ID)：", key="seller_login")
    
    if seller_id:
        try:
            records, sheet = fetch_and_clean_data()
            df = pd.DataFrame(records)
            
            my_df = df if seller_id == "shm_admin" else df[df['聯絡方式'] == seller_id]
            
            if my_df.empty:
                st.warning("找不到您的商品紀錄，趕快去上架吧！")
            else:
                if seller_id == "shm_admin": st.success("🔐 解鎖成功！歡迎回來，老闆 (全站數據模式)。")
                else: st.success("歡迎回來！這是您專屬的賣家數據分析。")
                st.divider()
                
                total_items = len(my_df)
                sold_items = len(my_df[my_df['商品狀態'] == '已售出'])
                expired_items = len(my_df[my_df['商品狀態'] == '已過期'])
                active_items = total_items - sold_items - expired_items
                
                total_value = sum([int(str(p).replace(',', '')) for p in my_df['預售價格'] if str(p).replace(',', '').isdigit()])
                
                st.subheader("💡 您的銷售指標")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("總上架數", f"{total_items} 件")
                col2.metric("架上流通商品", f"{active_items} 件")
                col3.metric("自動下架 (過期)", f"{expired_items} 件")
                col4.metric("成功售出", f"{sold_items} 件")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                st.subheader("📊 您的商品明細與管理")
                chart_col1, chart_col2 = st.columns([1, 2])
                with chart_col1:
                    st.write("**商品狀態分佈**")
                    st.bar_chart(my_df['商品狀態'].value_counts(), color="#FF4B4B")
                    
                with chart_col2:
                    st.write("**商品管理清單 (可操作)**")
                    for _, row in my_df.iloc[::-1].iterrows():
                        with st.container(border=True):
                            c_title, c_price, c_status, c_action = st.columns([3, 1.5, 1.5, 2])
                            c_title.write(f"**{row['商品標題']}**")
                            c_price.write(f"NT$ {row['預售價格']}")
                            
                            status_color = "green" if row['商品狀態'] == '上架中' else "red" if row['商品狀態'] == '已過期' else "gray"
                            c_status.markdown(f"<span style='color:{status_color}; font-weight:bold;'>{row['商品狀態']}</span>", unsafe_allow_html=True)
                            
                            with c_action:
                                if row['商品狀態'] == '上架中':
                                    if st.button("標記售出", key=f"sold_{row['sheet_row']}", use_container_width=True):
                                        sheet.update_cell(row['sheet_row'], 9, "已售出")
                                        st.rerun()
                                # === 🆕 核心升級 1：一鍵延長上架 ===
                                elif row['商品狀態'] == '已過期':
                                    if st.button("🔄 延長30天", key=f"renew_{row['sheet_row']}", type="primary", use_container_width=True):
                                        new_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        sheet.update_cell(row['sheet_row'], 1, new_time) # 更新上架時間
                                        st.success("已重新上架！")
                                        time.sleep(1)
                                        st.rerun()
                                else:
                                    st.write("已結案")
        except Exception as e:
            st.error(f"無法讀取資料：{e}")