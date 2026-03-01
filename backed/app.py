from flask import Flask, request, jsonify
from flask_cors import CORS  # 解决跨域问题（不同端口通信）
from core import BaikeRPABot

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 允许前端访问

# 这是一个测试接口：当访问 http://localhost:5000/test 时返回
@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': '后端跑通了！'})

# 这是你要用的搜索接口
@app.route('/api/search', methods=['POST'])
def search():
    # 1. 接收前端发来的数据
    data = request.get_json()
    keyword = data.get('keyword', '')
    
    print(f"收到搜索请求：{keyword}")
    
    # 2. 这里先模拟搜索结果（先不调RPA）
    #   后面你会改成调用你的core.py去真实搜索
    mock_result = {
        'success': True,
        'keyword': keyword,
        'title': f'{keyword} - 百度百科',
        'summary': f'这是关于{keyword}的简介...（模拟数据）',
        'url': f'https://baike.baidu.com/item/{keyword}'
    }
    
    # 3. 返回给前端
    return jsonify(mock_result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)