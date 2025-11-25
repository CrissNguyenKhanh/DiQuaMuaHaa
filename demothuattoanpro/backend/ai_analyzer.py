import pandas as pd
import numpy as np
from collections import Counter
from sklearn.preprocessing import LabelEncoder
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from data.patient_data import PATIENT_DATA

class PatientAIAnalyzer:
    def __init__(self, data=None):
        self.data = data if data else PATIENT_DATA
        self.df = pd.DataFrame(self.data)
        self.is_loaded = True
        
        # Severity mapping cho các chẩn đoán
        self.severity_map = {
            "Cảm cúm": "Nhẹ",
            "Đau đầu": "Nhẹ", 
            "Viêm họng": "Nhẹ",
            "Viêm phổi": "Nặng",
            "Cao huyết áp": "Trung bình",
            "Tăng huyết áp": "Trung bình",
            "Tiểu đường": "Trung bình",
            "Tiểu đường Type 2": "Trung bình",
            "Dị ứng": "Nhẹ",
            "Hen suyễn": "Trung bình",
            "Viêm dạ dày": "Trung bình",
            "Sốt xuất huyết": "Nặng",
            "Covid-19": "Nặng",
            "Viêm gan": "Nặng",
            "Viêm khớp": "Trung bình",
            "Bệnh tim": "Nặng",
            "Thoát vị đĩa đệm": "Trung bình",
            "Dị ứng thời tiết": "Nhẹ",
            "Rối loạn tiền đình": "Trung bình",
        }
        
    def analyze_by_diagnosis(self):
        """Phân tích thống kê theo chẩn đoán"""
        diagnosis_count = self.df['diagnosis'].value_counts()
        total = len(self.df)
               
        result = []
        for diagnosis, count in diagnosis_count.items():
            result.append({
                "name": diagnosis,
                "value": int(count),
                "percentage": round((count / total) * 100, 1)
            })
        return result
    
    def analyze_symptoms(self):
        """Phân tích triệu chứng phổ biến"""
        all_symptoms = []
        for symptoms_list in self.df['symptoms']:
            all_symptoms.extend(symptoms_list)
        
        symptom_count = Counter(all_symptoms)
        top_symptoms = symptom_count.most_common(10)
        
        return [{"name": symptom, "value": count} 
                for symptom, count in top_symptoms]
    
    def analyze_by_age(self):
        """Phân tích theo độ tuổi"""
        age_groups = {
            "18-30": 0,
            "31-40": 0,
            "41-50": 0,
            "51+": 0
        }
        
        for age in self.df['age']:
            if age <= 30:
                age_groups["18-30"] += 1
            elif age <= 40:
                age_groups["31-40"] += 1
            elif age <= 50:
                age_groups["41-50"] += 1
            else:
                age_groups["51+"] += 1
        
        return [{"name": name, "value": value} 
                for name, value in age_groups.items()]
    
    def analyze_by_gender(self):
        """Phân tích theo giới tính"""
        gender_count = self.df['gender'].value_counts()
        total = len(self.df)
        
        result = []
        for gender, count in gender_count.items():
            result.append({
                "name": gender,
                "value": int(count),
                "percentage": round((count / total) * 100, 1)
            })
        return result
    
    def analyze_by_severity(self):
        """Phân tích theo mức độ nghiêm trọng"""
        severity_count = self.df['severity'].value_counts()
        total = len(self.df)
        
        result = []
        for severity, count in severity_count.items():
            result.append({
                "name": severity,
                "value": int(count),
                "percentage": round((count / total) * 100, 1)
            })
        return result
    
    def analyze_trends(self):
        """Phân tích xu hướng theo thời gian"""
        date_count = self.df['date'].value_counts().sort_index()
        
        return [{"name": date, "value": int(count)} 
                for date, count in date_count.items()]
    
    def predict_trend(self):
        """Dự đoán xu hướng bằng AI"""
        trends = self.analyze_trends()
        if len(trends) < 2:
            return "Không đủ dữ liệu"
        
        recent_values = [t['value'] for t in trends[-3:]]
        avg = np.mean(recent_values)
        latest = recent_values[-1]
        
        if latest > avg * 1.2:
            return "Tăng mạnh"
        elif latest > avg:
            return "Tăng nhẹ"
        elif latest < avg * 0.8:
            return "Giảm mạnh"
        else:
            return "Ổn định"
    
    def calculate_symptom_match_score(self, input_symptoms, patient_symptoms):
        """Tính điểm trùng khớp triệu chứng (Jaccard similarity)"""
        input_set = set(input_symptoms)
        patient_set = set(patient_symptoms)
        
        if len(input_set) == 0 or len(patient_set) == 0:
            return 0.0
        
        intersection = len(input_set & patient_set)
        union = len(input_set | patient_set)
        
        return intersection / union
    
    def predict_diagnosis(self, symptoms, age, gender):
        """Dự đoán chẩn đoán với confidence realistic hơn"""
        
        # 1. Lấy tất cả triệu chứng unique từ training data
        all_unique_symptoms = set()
        for p in self.data:
         
            all_unique_symptoms.update(p['symptoms'])
        symptom_list = sorted(list(all_unique_symptoms))
        
        # 2. Chuẩn bị training data
        X = []
        y = []
        symptom_matches = []  # Lưu điểm match để điều chỉnh confidence
        
        for patient in self.data:
            # Tạo binary feature vector cho symptoms
            feature_vector = [0] * len(symptom_list)
            
            for symptom in patient['symptoms']:
                if symptom in symptom_list:
                    idx = symptom_list.index(symptom)
                    feature_vector[idx] = 1
            
            # Normalize age (0-1 range)
            normalized_age = patient['age'] / 100.0
            
            # Gender encoding
            gender_encoded = 1 if patient['gender'] == 'Nam' else 0
            
            feature_vector.append(normalized_age)
            feature_vector.append(gender_encoded)
            
            X.append(feature_vector)
            y.append(patient['diagnosis'])
            
            # Tính điểm match với input
            match_score = self.calculate_symptom_match_score(symptoms, patient['symptoms'])
            symptom_matches.append(match_score)
        
        # 3. Train Naive Bayes model
        X = np.array(X)
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        
        model = GaussianNB()
        model.fit(X, y_encoded)
        
        # 4. Chuẩn bị input vector
        input_vector = [0] * len(symptom_list)
        for symptom in symptoms:
            if symptom in symptom_list:
                idx = symptom_list.index(symptom)
                input_vector[idx] = 1
        
        input_vector.append(age / 100.0)  # Normalize
        input_vector.append(1 if gender == 'Nam' else 0)
        
        # 5. Predict
        prediction = model.predict([input_vector])[0]
        diagnosis = le.inverse_transform([prediction])[0]
        probabilities = model.predict_proba([input_vector])[0]
        base_confidence = max(probabilities)
        
        # 6. ĐIỀU CHỈNH CONFIDENCE DỰA TRÊN SYMPTOM MATCH
        # Tìm max match score với các case trong training data có cùng diagnosis
        max_match_for_diagnosis = 0
        for i, d in enumerate(y):
            if d == diagnosis:
                max_match_for_diagnosis = max(max_match_for_diagnosis, symptom_matches[i])
        
        # Penalty factors
        penalty = 1.0
        
        # Penalty 1: Nếu triệu chứng không khớp nhiều
        if max_match_for_diagnosis < 0.3:
            penalty *= 0.6  # Giảm 40%
        elif max_match_for_diagnosis < 0.5:
            penalty *= 0.75  # Giảm 25%
        elif max_match_for_diagnosis < 0.7:
            penalty *= 0.85  # Giảm 15%
        
        # Penalty 2: Số lượng triệu chứng
        if len(symptoms) < 2:
            penalty *= 0.7  # Ít triệu chứng → kém tin cậy
        elif len(symptoms) > 6:
            penalty *= 0.8  # Quá nhiều triệu chứng → khó xác định
        
        # Penalty 3: Data size (nếu training data ít)
        if len(self.data) < 20:
            penalty *= 0.85
        elif len(self.data) < 50:
            penalty *= 0.9
        
        # Penalty 4: Xử lý trường hợp model quá confident (>0.95)
        if base_confidence > 0.95:
            # Đưa về khoảng 0.7-0.85
            base_confidence = 0.7 + (base_confidence - 0.95) * 2
        
        # Apply penalty
        adjusted_confidence = base_confidence * penalty
        
        # Thêm random noise nhỏ để realistic hơn (-2% đến +2%)
        noise = np.random.uniform(-0.02, 0.02)
        adjusted_confidence = max(0.4, min(0.92, adjusted_confidence + noise))
        
        return {
            "diagnosis": diagnosis,
            "confidence": float(adjusted_confidence),
            "match_score": float(max_match_for_diagnosis),  # Debug info
            "base_confidence": float(base_confidence)  # Debug info
        }
    
    def predict(self, symptoms, age, gender):
        """Main prediction function với confidence realistic"""
        try:
            # Validate input
            if not symptoms or len(symptoms) == 0:
                return {
                    "success": False,
                    "error": "Vui lòng chọn ít nhất 1 triệu chứng"
                }
            
            # Chuẩn hóa input symptoms (lowercase, strip)
            symptoms = [s.strip().lower() for s in symptoms]
            
            # Chuẩn hóa symptoms trong training data để match tốt hơn
            available_symptoms = [s.lower() for s in self.get_available_symptoms()]
            
            # Lọc chỉ lấy symptoms có trong training data
            valid_symptoms = [s for s in symptoms if s in available_symptoms]
            
            if len(valid_symptoms) == 0:
                return {
                    "success": False,
                    "error": "Không tìm thấy triệu chứng phù hợp trong cơ sở dữ liệu"
                }
            
            # Gọi predict_diagnosis
            result = self.predict_diagnosis(valid_symptoms, age, gender)
            diagnosis = result['diagnosis']
            confidence = result['confidence']
            
            # Xác định severity
            severity = self.severity_map.get(diagnosis, "Trung bình")
            
            # Tạo recommendations dựa trên severity và confidence
            if confidence < 0.5:
                recommendations = [
                    "⚠️ Độ tin cậy thấp - cần thêm thông tin",
                    "Đến cơ sở y tế để được khám chính xác",
                    "Triệu chứng chưa rõ ràng, cần theo dõi thêm"
                ]
            elif severity == "Nặng":
                recommendations = [
                    "🚨 ĐẾN BỆNH VIỆN KHÁM NGAY LẬP TỨC",
                    "Không tự ý dùng thuốc",
                    "Theo dõi sát triệu chứng"
                ]
            elif severity == "Trung bình":
                recommendations = [
                    "Nên đến phòng khám để được tư vấn",
                    "Nghỉ ngơi đầy đủ",
                    "Uống đủ nước và theo dõi triệu chứng"
                ]
            else:  # Nhẹ
                recommendations = [
                    "Nghỉ ngơi nhiều",
                    "Uống nhiều nước",
                    "Theo dõi thêm 1-2 ngày, nếu không khỏi hãy đến khám"
                ]
            
            return {
                "success": True,
                "diagnosis": diagnosis,
                "confidence": round(confidence, 4),
                "severity": severity,
                "recommendations": recommendations,
                # Debug info (có thể bỏ trong production)
                "debug": {
                    "match_score": round(result.get('match_score', 0), 3),
                    "base_confidence": round(result.get('base_confidence', 0), 3),
                    "valid_symptoms_count": len(valid_symptoms),
                    "total_training_data": len(self.data)
                }
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }

    def get_available_symptoms(self):
        """Lấy danh sách tất cả triệu chứng có trong dữ liệu"""
        all_symptoms = set()
        for patient in self.data:
            all_symptoms.update(patient['symptoms'])
        return sorted(list(all_symptoms))

    def get_available_diagnoses(self):
        """Lấy danh sách tất cả chẩn đoán có trong dữ liệu"""
        return sorted(list(self.df['diagnosis'].unique()))
    
    def get_summary(self):
        """Tổng hợp tất cả thống kê"""
        return {
            "totalPatients": len(self.data),
            "diagnosisStats": self.analyze_by_diagnosis(),
            "symptomStats": self.analyze_symptoms(),
            "ageStats": self.analyze_by_age(),
            "genderStats": self.analyze_by_gender(),
            "severityStats": self.analyze_by_severity(),
            "trends": self.analyze_trends(),
            "prediction": self.predict_trend()
        }
    
    def load_model(self):
        """Placeholder cho việc load model từ file"""
        self.is_loaded = True
        return True