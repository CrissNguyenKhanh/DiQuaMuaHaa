from flask import Flask, jsonify, request
from flask_cors import CORS
from data.database import Database
from ai_analyzer import PatientAIAnalyzer
import auto_train_model

app = Flask(__name__)
CORS(app)

# Initialize
db = Database()
ai = PatientAIAnalyzer()

# Nếu chưa có model, train ngay
if not ai.is_loaded:
    print("\n⚠️ Model chưa tồn tại, đang train...")
    trainer = auto_train_model.ModelTrainer()
    if trainer.train():
        ai.load_model()


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "model_loaded": ai.is_loaded}), 200


# ========== AUTH ROUTES ==========
@app.route("/api/auth/login", methods=["POST"])
def login():
    try:
        data = request.json
        result = db.authenticate_user(data["username"], data["password"])
        return jsonify(result), 200 if result["success"] else 401
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/auth/register", methods=["POST"])
def register():
    try:
        data = request.json
        result = db.create_user(
            username=data["username"],
            password=data["password"],
            full_name=data.get("full_name", ""),
            email=data.get("email", ""),
            role=data.get("role", "user"),
        )
        return jsonify(result), 200 if result["success"] else 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ========== MEDICAL RECORD ROUTES ==========
@app.route("/api/records/<int:user_id>", methods=["GET"])
def get_records(user_id):
    try:
        print("day la user_id cua nguoi da log vao", user_id)
        records = db.get_user_medical_records(user_id)
        return jsonify({"success": True, "records": records}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/records", methods=["POST"])
def add_record():
    try:
        data = request.json

        # Predict by AI
        prediction = ai.predict(
            symptoms=data["symptoms"], age=data["age"], gender=data["gender"]
        )

        if not prediction["success"]:
            return jsonify(prediction), 400

        record_id = db.add_medical_record(
            user_id=data["user_id"],
            symptoms=data["symptoms"],
            age=data["age"],
            gender=data["gender"],
            diagnosis=prediction["diagnosis"],
            severity=prediction["severity"],
            confidence=prediction["confidence"],
            notes=data.get("notes", ""),
        )

        return (
            jsonify(
                {"success": True, "record_id": record_id, "prediction": prediction}
            ),
            200,
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ========== AI ROUTES ==========
@app.route("/api/ai/predict", methods=["POST"])
def predict():
    try:
        data = request.json
        result = ai.predict(
            symptoms=data["symptoms"], age=data["age"], gender=data["gender"]
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ai/symptoms", methods=["GET"])
def get_symptoms():
    try:
        symptoms = ai.get_available_symptoms()
        return jsonify({"success": True, "symptoms": symptoms}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ai/diagnoses", methods=["GET"])
def get_diagnoses():
    try:
        diagnoses = ai.get_available_diagnoses()
        return jsonify({"success": True, "diagnoses": diagnoses}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ai/retrain", methods=["POST"])
def retrain():
    try:
        trainer = auto_train_model.ModelTrainer()
        success = trainer.train()

        if success:
            ai.load_model()
            return (
                jsonify({"success": True, "message": "Retrain model thành công!"}),
                200,
            )

        return jsonify({"success": False, "error": "Không đủ dữ liệu để train"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ========== TRAINING DATA ROUTES ==========
@app.route("/api/training-data", methods=["POST"])
def add_training_data():
    try:
        data = request.json
        data_id = db.add_training_data(
            symptoms=data["symptoms"],
            age=data["age"],
            gender=data["gender"],
            diagnosis=data["diagnosis"],
            severity=data["severity"],
        )

        return (
            jsonify(
                {
                    "success": True,
                    "data_id": data_id,
                    "message": "Đã thêm dữ liệu. Hãy chạy /api/ai/retrain để train lại model!",
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/training-data", methods=["GET"])
def get_training_data():
    try:
        data = db.get_all_training_data()
        return jsonify({"success": True, "data": data, "count": len(data)}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


import traceback


@app.route("/api/statistics", methods=["GET"])
def get_statistics():
    import pandas as pd
    import json
    import traceback

    try:
        # 0. Lấy dữ liệu từ DB
        data = db.get_all_training_data()

        # Nếu chưa có dữ liệu
        if not data:
            return jsonify(
                {
                    "totalPatients": 0,
                    "diagnosisStats": [],
                    "symptomStats": [],
                    "ageStats": [],
                    "genderStats": [],
                    "severityStats": [],
                    "trends": [],
                    "prediction": "Không có dữ liệu",
                }
            )

        # 1. Chuyển sang DataFrame
        df = pd.DataFrame(data)

        # Chuẩn hóa tên cột (bỏ khoảng trắng thừa nếu có)
        df.columns = df.columns.str.strip()
        totalPatients = len(df)

        # Helper function để convert numpy int/float sang python native types (tránh lỗi JSON)
        def to_native(df_stats):
            records = df_stats.to_dict(orient="records")
            for rec in records:
                if "value" in rec:
                    rec["value"] = int(rec["value"])  # Ép kiểu về int thường
                if "percentage" in rec:
                    rec["percentage"] = float(rec["percentage"])
            return records

        # 2. Thống kê chẩn đoán (Diagnosis)
        if "diagnosis" in df.columns:
            diag_counts = df["diagnosis"].value_counts().reset_index()
            diag_counts.columns = ["name", "value"]
            diag_counts["percentage"] = (
                (diag_counts["value"] / totalPatients) * 100
            ).round(1)
            diagnosisStats = to_native(diag_counts)
        else:
            diagnosisStats = []

        # 3. Thống kê triệu chứng (Symptoms) - QUAN TRỌNG: Xử lý kỹ hơn
        all_symptoms = []
        if "symptoms" in df.columns:
            for raw in df["symptoms"]:
                try:
                    # Nếu là string (do lưu trong DB dạng text), parse ra list
                    if isinstance(raw, str):
                        items = json.loads(
                            raw.replace("'", '"')
                        )  # Fix lỗi quote đơn nếu có
                    elif isinstance(raw, list):
                        items = raw
                    else:
                        items = []

                    if isinstance(items, list):
                        all_symptoms.extend(items)
                except:
                    continue  # Bỏ qua lỗi parsing lẻ tẻ

        if all_symptoms:
            sym_series = (
                pd.Series(all_symptoms).value_counts().head(10).reset_index()
            )  # Lấy TOP 10 thôi
            sym_series.columns = ["name", "value"]
            symptomStats = to_native(sym_series)
        else:
            symptomStats = []

        # 4. Thống kê tuổi (Age)
        if "age" in df.columns:
            # Nhóm tuổi để biểu đồ đẹp hơn thay vì từng tuổi lẻ tẻ
            bins = [0, 18, 30, 45, 60, 100]
            labels = ["0-18", "19-30", "31-45", "46-60", ">60"]
            df["age_group"] = pd.cut(
                pd.to_numeric(df["age"], errors="coerce"), bins=bins, labels=labels
            )

            age_counts = df["age_group"].value_counts().sort_index().reset_index()
            age_counts.columns = ["name", "value"]
            ageStats = to_native(age_counts)
        else:
            ageStats = []

        # 5. Thống kê giới tính (Gender)
        if "gender" in df.columns:
            gender_counts = df["gender"].value_counts().reset_index()
            gender_counts.columns = ["name", "value"]
            gender_counts["percentage"] = (
                (gender_counts["value"] / totalPatients) * 100
            ).round(1)
            genderStats = to_native(gender_counts)
        else:
            genderStats = []

        # 6. Thống kê mức độ (Severity)
        if "severity" in df.columns:
            sev_counts = df["severity"].value_counts().reset_index()
            sev_counts.columns = ["name", "value"]
            severityStats = to_native(sev_counts)
        else:
            severityStats = []

        # 7. Xu hướng theo ngày (Trends)
        trends_data = []
        if "created_at" in df.columns:
            df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
            # Group by date và chuyển date thành string YYYY-MM-DD
            trend_counts = (
                df.groupby(df["created_at"].dt.date).size().reset_index(name="value")
            )
            trend_counts.columns = ["name", "value"]
            trend_counts["name"] = trend_counts["name"].astype(
                str
            )  # Convert date obj -> string
            trends_data = to_native(trend_counts)

        # 8. Dự đoán bệnh phổ biến nhất
        prediction_text = (
            diagnosisStats[0]["name"] if diagnosisStats else "Chưa đủ dữ liệu"
        )

        return jsonify(
            {
                "totalPatients": totalPatients,
                "diagnosisStats": diagnosisStats,
                "symptomStats": symptomStats,
                "ageStats": ageStats,
                "genderStats": genderStats,
                "severityStats": severityStats,
                "trends": trends_data,
                "prediction": prediction_text,
            }
        )

    except Exception as e:
        print("\n❌ ERROR in /api/statistics:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("\n============================================")
    print("🏥 MEDICAL AI API SERVER")
    print("📍 http://localhost:5000")
    print("============================================\n")
    app.run(debug=True, port=5000)
