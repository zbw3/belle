from flask import Flask, jsonify


app = Flask(__name__)

@app.route(r'D:\project\belle\集采平台\add_orderrequestMain.py')
def get_data():
    return jsonify({"message": "数据获取成功", "data": [1, 2, 3, 4, 5]})

@app.route('/api/add')
def add_data():
    return jsonify({"message": "数据添加成功", "status": "ok"})

@app.route('/api/process')
def process_data():
    return jsonify({"message": "数据处理完成", "result": "processed"})

@app.route('/api/analyze')
def analyze_data():
    return jsonify({"message": "数据分析完成", "insights": ["趋势上升", "峰值在Q3"]})

if __name__ == '__main__':
    app.run(debug=True, port=5000)