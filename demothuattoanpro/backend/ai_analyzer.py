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
    
    def predict_diagnosis(self, symptoms, age, gender):
        """Dự đoán chẩn đoán dựa trên triệu chứng (sử dụng Naive Bayes)"""
        # Chuẩn bị dữ liệu training
        X = []
        y = []
        
        for patient in self.data:
            # Tạo feature vector từ symptoms
            feature_vector = [0] * 20  # Giả sử có tối đa 20 triệu chứng khác nhau
            all_unique_symptoms = set()
            for p in self.data:
                all_unique_symptoms.update(p['symptoms'])
            symptom_list = sorted(list(all_unique_symptoms))
            
            for symptom in patient['symptoms']:
                if symptom in symptom_list:
                    idx = symptom_list.index(symptom)
                    if idx < 20:
                        feature_vector[idx] = 1
            
            # Thêm age và gender
            feature_vector.append(patient['age'])
            feature_vector.append(1 if patient['gender'] == 'Nam' else 0)
            
            X.append(feature_vector)
            y.append(patient['diagnosis'])
        
        # Train model
        X = np.array(X)
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        
        model = GaussianNB()
        model.fit(X, y_encoded)
        
        # Predict
        input_vector = [0] * 20
        for symptom in symptoms:
            if symptom in symptom_list:
                idx = symptom_list.index(symptom)
                if idx < 20:
                    input_vector[idx] = 1
        
        input_vector.append(age)
        input_vector.append(1 if gender == 'Nam' else 0)
        
        prediction = model.predict([input_vector])[0]
        diagnosis = le.inverse_transform([prediction])[0]
        
        # Tính confidence
        probabilities = model.predict_proba([input_vector])[0]
        confidence = max(probabilities) * 100
        
        return {
            "diagnosis": diagnosis,
            "confidence": round(confidence, 2)
        }
    
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