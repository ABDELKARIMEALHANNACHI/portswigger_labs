import requests
from flask import Flask, request

app = Flask(__name__)

@app.route('/stock', methods=['POST'])
def check_stock():
    stock_api = request.form.get('stockApi')
    
    # 🚨 VULNERABLE: user controls URL
    response = requests.get(stock_api)
    
    return response.text

if __name__ == '__main__':
    app.run(debug=True)
