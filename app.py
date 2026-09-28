from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

STOCKS = {
    "005930": "삼성전자",
    "000660": "SK하이닉스",
    "005380": "현대차",
    "373220": "LG에너지솔루션",
    "207940": "삼성바이오로직스",
    "068270": "셀트리온",
    "005490": "POSCO홀딩스",
    "105560": "KB금융",
    "000270": "기아",
    "035420": "NAVER"
}

def get_naver_stock_price(code):
    url = f"https://finance.naver.com/item/main.naver?code={code}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        res = requests.get(url, headers=headers, timeout=3)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        no_today = soup.find('p', class_='no_today')
        price_str = no_today.find('span', class_='blind').text.replace(',', '')
        price = int(price_str)
        
        no_exday = soup.find('p', class_='no_exday')
        spans = no_exday.find_all('span', class_='blind')
        ico = no_exday.find('span', class_='ico')
        is_down = 'nv' in ico.get('class', []) if ico else False
        
        change_rate = float(spans[1].text.replace('%', '').strip())
        if is_down:
            change_rate = -change_rate
            
        return price, change_rate
    except Exception as e:
        return None, None

@app.route('/api/stocks', methods=['GET'])
def get_all_stocks():
    result = []
    for code, name in STOCKS.items():
        price, change = get_naver_stock_price(code)
        if price is not None:
            result.append({
                "code": code,
                "name": name,
                "price": price,
                "change": change
            })
    return jsonify(result)

if __name__ == '__main__':
    print("🚀 주가 중계 서버 시작됨 (http://localhost:5000/api/stocks)")
    app.run(host='0.0.0.0', port=5000, debug=True)