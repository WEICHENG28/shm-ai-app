import google.generativeai as genai
import PIL.Image
import streamlit as st

# 🔒 從 Streamlit 的隱藏密碼庫讀取 API KEY (絕對不要把密碼明碼寫在這裡！)
GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=GOOGLE_API_KEY)
# 使用我們確認過能用的模型名稱
model = genai.GenerativeModel('gemini-flash-latest')

def analyze_multiple_items(image_paths):
    """
    接收一個圖片路徑的「清單 (List)」，讓 AI 綜合判斷
    """
    images = []
    for path in image_paths:
        img = PIL.Image.open(path)
        images.append(img)
    
    # 針對多圖的更強指令
    prompt = """
    你是一位台灣最頂尖、最懂市場行情的「二手鑑價專家」。
    請分析這些商品照片，並以 JSON 格式回傳以下欄位：
    
    1. "brand": 品牌名稱。
    2. "model": 商品確切型號（請盡量精準，包含英文或代號）。
    3. "condition_score": 1到10分的新舊評分（10為全新未拆）。
    4. "estimated_price_range": 預估的二手「快速成交價」區間（格式如：NT$600 - NT$900）。
       【⚠️ 估價極致要求 - 請嚴格遵守】：
       - 絕對不要只拿「官方原價(MSRP)」直接打折！
       - 請強烈考量「Outlet 倒貨折扣」、「電商促銷」與「二手市場實際流通的折舊率」。
       - 即使看到全新未拆的吊牌，也要預設賣家可能是在 Outlet 以極低折扣購入。
       - 請給出一個「只要賣家開這個價格，買家就會覺得划算而立刻買單」的地氣價格。
    5. "analysis": 一段給賣家的專業短評（約 50 字內）。請直接說明這個品項在二手市場的熱度。如果有吊牌，可以委婉提醒「雖然全新，但市場已有 Outlet 破盤價，建議以實際流通價出售」。
    
    請確保只回傳純 JSON 格式，不要包含任何 Markdown 標籤（如 ```json）。
    """
    
    # 把指令放在最前面，後面跟著一堆圖片
    content = [prompt] + images
    
    response = model.generate_content(content)
    return response.text