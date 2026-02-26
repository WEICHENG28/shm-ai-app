import google.generativeai as genai
import PIL.Image
import streamlit as st

# 🔒 從 Streamlit 的隱藏密碼庫讀取 API KEY
GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

def analyze_multiple_items(image_paths):
    """
    接收一個圖片路徑的清單，讓 AI 進行嚴格的影像審核與綜合判斷
    """
    images = []
    for path in image_paths:
        img = PIL.Image.open(path)
        images.append(img)
    
    # 🛑 針對多圖的更強指令（加入嚴格審核機制）
    prompt = """
    你現在是一位極度嚴格的「AI 影像品管員」兼「二手鑑價專家」。
    請先審查照片品質，再進行鑑價。如果照片不合格，你必須拒絕估價！
    請以 JSON 格式回傳以下欄位：
    
    1. "is_qualified": 布林值 (true 或 false)。如果照片太模糊、只有局部、看不出具體型號、或缺乏關鍵資訊（如底部型號標籤），請毫不猶豫設為 false。
    2. "rejection_reason": 如果 is_qualified 為 false，請給出具體的退件原因（例如：「照片太模糊，請重新拍攝」、「請補拍商品底部的確切型號標籤」，約 20 字內）。若為 true 則留空 ""。
    3. "brand": 品牌名稱（若不合格可留空）。
    4. "model": 商品確切型號（若不合格可留空）。
    5. "condition_score": 1到10分的新舊評分（若不合格可設為 0）。
    6. "estimated_price_range": 預估的二手「快速成交價」區間（格式如：NT$600 - NT$900）。嚴格考量 Outlet 倒貨折扣與二手折舊。
    7. "analysis": 一段給賣家的專業短評（約 50 字內）。
    
    請確保只回傳純 JSON 格式，不要包含任何 Markdown 標籤（如 ```json）。
    """
    
    content = [prompt] + images
    response = model.generate_content(content)
    return response.text