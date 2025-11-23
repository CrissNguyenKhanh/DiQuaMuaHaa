from flask import Flask, jsonify, request
from flask_cors import CORS
from ai_analyzer import PatientAIAnalyzer

app = Flask(__name__)
CORS(app)  # Cho phép React gọi API

analyzer = PatientAIAnalyzer()

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """API lấy thống kê tổng hợp"""
    try:
        summary = analyzer.get_summary()
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict_diagnosis():
    """API dự đoán chẩn đoán từ triệu chứng"""
    try:
        data = request.json
        symptoms = data.get('symptoms', [])
        age = data.get('age', 0)
        gender = data.get('gender', 'Nam')
        
        result = analyzer.predict_diagnosis(symptoms, age, gender)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """API kiểm tra server"""
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)