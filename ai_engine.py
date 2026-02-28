import google.generativeai as genai
import PIL.Image
import streamlit as st
import random

# === 🆕 核心升級：建立 4 把鑰匙的「鑰匙圈」 ===
# 系統會從這四把金鑰中，隨機盲抽一把來使用，完美分散流量！
api_keys = [
    st.secrets["GEMINI_API_KEY_1"],
    st.secrets["GEMINI_API_KEY_2"],
    st.secrets["GEMINI_API_KEY_3"],
    st.secrets["GEMINI_API_KEY_4"]
]

# 隨機抽取一把鑰匙
chosen_key = random.choice(api_keys)

# 告訴 Google 系統這次用這把被抽中的鑰匙
genai.configure(api_key=chosen_key)

# 初始化模型 (建議使用最新的 1.5 flash 版本名稱)
model = genai.GenerativeModel('gemini-1.5-flash')

def analyze_multiple_items(image_paths):
    """
    接收一個圖片路徑的清單，讓 AI 進行嚴格的影像審核與綜合判斷
    """
    images = []
    for path in image_paths:
        img = PIL.Image.open(path)
        images.append(img)
    
    # 🛑 針對多圖的更強指令（加入嚴格審核機制與標籤生成）
    prompt = """
    你現在是一位極度嚴格的「AI 影像品管員」兼「二手鑑價專家」。
    請先審查照片品質，再進行鑑價。如果照片不合格，你必須拒絕估價！
    請以 JSON 格式回傳以下欄位：
    
    1. "is_qualified": 布林值 (true 或 false)。如果照片太模糊、只有局部、看不出具體型號、或缺乏關鍵資訊（如底部型號標籤），請毫不猶豫設為 false。
    2. "rejection_reason": 如果 is_qualified 為 false，請給具體退件原因（約 20 字內）。若為 true 則留空 ""。
    3. "brand": 品牌名稱。
    4. "model": 商品確切型號。
    5. "condition_score": 1到10分的新舊評分。
    6. "estimated_price_range": 預估的二手「快速成交價」區間（格式如：NT$600 - NT$900）。
    7. "analysis": 一段給賣家的專業短評（約 50 字內）。
    8. "tags": 根據商品生成 3~5 個精準的 Hashtag。請務必確保第一個 Hashtag 是最通俗的「大分類」（例如：#鞋子、#滑鼠、#手機），後面再接細節屬性（如：#運動鞋 #PUMA）。
    
    請確保只回傳純 JSON 格式，不要包含任何 Markdown 標籤（如 ```json）。
    """
    
    content = [prompt] + images
    response = model.generate_content(content)
    return response.text