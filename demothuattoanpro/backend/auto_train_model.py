import numpy as np
import pickle  # <--- BỔ SUNG QUAN TRỌNG: Thư viện để lưu model
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import sys
import os

# Import database
# Thêm đường dẫn thư mục hiện tại vào sys.path để tìm được module data
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from data.database import Database

class ModelTrainer:
    def __init__(self):
        self.db = Database()
        self.model = GaussianNB()
        self.label_encoder = LabelEncoder()
        self.symptom_list = []
        self.model_file = 'trained_model.pkl'
        
    def prepare_data(self):
        """Chuẩn bị dữ liệu từ database"""
        training_data = self.db.get_all_training_data()
        
        # Cần ít nhất 5 mẫu để train/test split hoạt động ổn định
        if len(training_data) < 5:
            print(f"❌ Không đủ dữ liệu để train (cần ít nhất 5 mẫu, hiện có {len(training_data)})")
            return None, None
        
        # 1. Lấy danh sách tất cả triệu chứng (để tạo vector đặc trưng cố định)
        all_symptoms = set()
        for data in training_data:
            # Xử lý an toàn phòng trường hợp data['symptoms'] không phải là list
            symptoms = data.get('symptoms', [])
            if isinstance(symptoms, list):
                all_symptoms.update(symptoms)
        
        # Sắp xếp để đảm bảo thứ tự index luôn nhất quán
        self.symptom_list = sorted(list(all_symptoms))
        print(f"📊 Tổng số triệu chứng unique: {len(self.symptom_list)}")
        
        # 2. Tạo feature vectors
        X = []
        y = []
        
        for data in training_data:
            # Vector triệu chứng (One-hot encoding thủ công)
            feature_vector = [0] * len(self.symptom_list)
            
            current_symptoms = data.get('symptoms', [])
            for symptom in current_symptoms:
                if symptom in self.symptom_list:
                    idx = self.symptom_list.index(symptom)
                    feature_vector[idx] = 1
            
            # Thêm tuổi (numerical)
            feature_vector.append(data.get('age', 0))
            
            # Thêm giới tính (binary: Nam=1, Khác=0)
            gender_val = 1 if data.get('gender') == 'Nam' else 0
            feature_vector.append(gender_val)
            
            X.append(feature_vector)
            y.append(data['diagnosis'])
        
        return np.array(X), y
    
    def train(self):
        print("🔄 Đang chuẩn bị dữ liệu...")
        X, y = self.prepare_data()
        
        if X is None or len(X) == 0:
            print("❌ Dữ liệu trống hoặc không đủ.")
            return False
        
        try:
            # Mã hóa nhãn (Diagnosis -> Số)
            y_encoded = self.label_encoder.fit_transform(y)

            # Chia train/test (80% train, 20% test)
            # stratify=y_encoded giúp đảm bảo tỉ lệ các bệnh trong tập train/test cân bằng nhau
            try:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
                )
            except ValueError:
                # Fallback: Nếu dữ liệu quá ít hoặc có class chỉ xuất hiện 1 lần, không thể stratify
                print("⚠️ Cảnh báo: Dữ liệu ít, không thể phân tầng (stratify). Chuyển sang split thường.")
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y_encoded, test_size=0.2, random_state=42
                )
            
            print(f"🔄 Đang train model với {len(X_train)} mẫu...")
            self.model.fit(X_train, y_train)
            
            # Đánh giá
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            print(f"📈 Accuracy trên test set: {accuracy:.2f}")
            
            # Chỉ in chi tiết nếu có đủ class trong test set
            if len(set(y_test)) > 0:
                print("📊 Classification Report:")
                # Lấy tên các class xuất hiện trong tập test để tránh lỗi index
                unique_labels = sorted(list(set(y_test) | set(y_pred)))
                target_names = [self.label_encoder.classes_[i] for i in unique_labels]
                print(classification_report(y_test, y_pred, labels=unique_labels, target_names=target_names, zero_division=0))

            # --- LƯU MODEL (PHẦN QUAN TRỌNG) ---
            model_data = {
                'model': self.model,
                'label_encoder': self.label_encoder,
                'symptom_list': self.symptom_list  # Cần lưu list này để mapping lúc predict
            }
            
            with open(self.model_file, 'wb') as f:
                pickle.dump(model_data, f)
            
            print(f"✅ Model đã lưu thành công tại: {self.model_file}")
            return True

        except Exception as e:
            print(f"❌ Lỗi trong quá trình training: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("=" * 60)
    print("🏥 HỆ THỐNG TRAIN AI CHẨN ĐOÁN Y TẾ")
    print("=" * 60)
    
    trainer = ModelTrainer()
    success = trainer.train()
    
    if success:
        print("\n✅ Hoàn tất! Model đã sẵn sàng sử dụng.")
    else:
        print("\n❌ Train thất bại!")
    
    print("=" * 60)