import google.generativeai as genai
import PIL.Image

# 🔒 你的 API KEY
GOOGLE_API_KEY = "AIzaSyC8DX-vtm_SlH-K2hZOo6karZZMn84tAR8"

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
    你是一位資深的二手交易鑑定專家。請綜合分析這幾張照片（可能包含正面、背面標籤、細節特寫），並回傳 JSON 格式：
    1. brand: 品牌名稱
    2. model: 精確的型號 (請仔細查看照片中的標籤貼紙或序號)
    3. condition_score: 綜合新舊評分 (1-10分)
    4. analysis: 50字以內的專業鑑定評論 (請說明你是根據哪個細節確認型號的，例如底部的標籤)
    5. estimated_price_range: 建議的二手市場售價區間 (台幣)
    
    注意：如果照片中有清楚的型號標籤，請以標籤上的文字為準。
    """
    
    # 把指令放在最前面，後面跟著一堆圖片
    content = [prompt] + images
    
    response = model.generate_content(content)
    return response.text