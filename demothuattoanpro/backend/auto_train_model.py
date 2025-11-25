import numpy as np
import pickle
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, balanced_accuracy_score
from sklearn.utils.class_weight import compute_class_weight
from collections import Counter
import sys
import os

# Import database
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
        
        if len(training_data) < 5:
            print(f"❌ Không đủ dữ liệu để train (cần ít nhất 5 mẫu, hiện có {len(training_data)})")
            return None, None, None
        
        # 1. Phân tích phân bố dữ liệu
        diagnoses = [data['diagnosis'] for data in training_data]
        diagnosis_counts = Counter(diagnoses)
        
        print(f"\n📊 Phân tích dữ liệu training:")
        print(f"   Tổng số mẫu: {len(training_data)}")
        print(f"   Số loại bệnh: {len(diagnosis_counts)}")
        print(f"\n   Phân bố theo bệnh:")
        for diagnosis, count in diagnosis_counts.most_common():
            percentage = (count / len(training_data)) * 100
            print(f"   - {diagnosis}: {count} mẫu ({percentage:.1f}%)")
        
        # Cảnh báo nếu dữ liệu quá không cân bằng
        max_count = max(diagnosis_counts.values())
        min_count = min(diagnosis_counts.values())
        imbalance_ratio = max_count / min_count if min_count > 0 else float('inf')
        
        if imbalance_ratio > 5:
            print(f"\n⚠️  CẢNH BÁO: Dữ liệu rất không cân bằng!")
            print(f"   Tỉ lệ class đa số/thiểu số: {imbalance_ratio:.1f}:1")
            print(f"   Model có thể bị bias về class '{max(diagnosis_counts, key=diagnosis_counts.get)}'")
        
        # 2. Lấy danh sách triệu chứng
        all_symptoms = set()
        for data in training_data:
            symptoms = data.get('symptoms', [])
            if isinstance(symptoms, list):
                # Chuẩn hóa triệu chứng về lowercase
                all_symptoms.update([s.lower().strip() for s in symptoms])
        
        self.symptom_list = sorted(list(all_symptoms))
        print(f"   Tổng số triệu chứng unique: {len(self.symptom_list)}\n")
        
        # 3. Tạo feature vectors
        X = []
        y = []
        
        for data in training_data:
            # One-hot encoding cho triệu chứng
            feature_vector = [0] * len(self.symptom_list)
            
            current_symptoms = data.get('symptoms', [])
            for symptom in current_symptoms:
                symptom_normalized = symptom.lower().strip()
                if symptom_normalized in self.symptom_list:
                    idx = self.symptom_list.index(symptom_normalized)
                    feature_vector[idx] = 1
            
            # Normalize age về 0-1
            age = data.get('age', 30)
            normalized_age = age / 100.0
            feature_vector.append(normalized_age)
            
            # Gender binary
            gender_val = 1 if data.get('gender') == 'Nam' else 0
            feature_vector.append(gender_val)
            
            X.append(feature_vector)
            y.append(data['diagnosis'])
        
        return np.array(X), y, diagnosis_counts
    
    def balance_data_with_smote_like(self, X, y):
        """
        Tạo synthetic samples cho minority classes (SMOTE-like approach)
        """
        from collections import defaultdict
        
        # Group samples by class
        class_samples = defaultdict(list)
        for i, label in enumerate(y):
            class_samples[label].append(X[i])
        
        # Find max class size
        max_size = max(len(samples) for samples in class_samples.values())
        target_size = max(5, int(max_size * 0.7))  # Oversample to 70% of majority
        
        X_balanced = []
        y_balanced = []
        
        for label, samples in class_samples.items():
            samples = np.array(samples)
            X_balanced.extend(samples)
            y_balanced.extend([label] * len(samples))
            
            # Nếu class này ít hơn target_size, tạo thêm synthetic samples
            if len(samples) < target_size:
                n_synthetic = target_size - len(samples)
                
                for _ in range(n_synthetic):
                    # Chọn ngẫu nhiên 2 samples từ class này
                    if len(samples) >= 2:
                        idx1, idx2 = np.random.choice(len(samples), 2, replace=False)
                        # Tạo sample mới bằng cách trung bình có trọng số
                        alpha = np.random.uniform(0.3, 0.7)
                        synthetic = alpha * samples[idx1] + (1 - alpha) * samples[idx2]
                        
                        # Round binary features (symptoms)
                        synthetic[:-2] = np.round(synthetic[:-2])
                        
                        X_balanced.append(synthetic)
                        y_balanced.append(label)
        
        return np.array(X_balanced), y_balanced
    
    def train(self, use_balancing=True):
        print("🔄 Đang chuẩn bị dữ liệu...")
        X, y, diagnosis_counts = self.prepare_data()
        
        if X is None or len(X) == 0:
            print("❌ Dữ liệu trống hoặc không đủ.")
            return False
        
        try:
            # BƯỚC 1: Balance data nếu cần
            if use_balancing and len(diagnosis_counts) > 1:
                max_count = max(diagnosis_counts.values())
                min_count = min(diagnosis_counts.values())
                
                if max_count / min_count > 3:
                    print("🔄 Đang cân bằng dữ liệu (SMOTE-like)...")
                    X, y = self.balance_data_with_smote_like(X, y)
                    print(f"   Sau khi balance: {len(X)} mẫu")
            
            # BƯỚC 2: Encode labels
            y_encoded = self.label_encoder.fit_transform(y)
            
            # BƯỚC 3: Tính class weights để xử lý imbalance
            class_weights = compute_class_weight(
                class_weight='balanced',
                classes=np.unique(y_encoded),
                y=y_encoded
            )
            
            print(f"\n📊 Class weights để xử lý imbalance:")
            for i, cls in enumerate(self.label_encoder.classes_):
                print(f"   {cls}: {class_weights[i]:.2f}")
            
            # BƯỚC 4: Split data
            try:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
                )
            except ValueError:
                print("⚠️ Không thể stratify, chuyển sang split thường")
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y_encoded, test_size=0.2, random_state=42
                )
            
            # BƯỚC 5: Train model với prior probabilities điều chỉnh
            print(f"\n🔄 Đang train model với {len(X_train)} mẫu...")
            
            # Tính prior probability có điều chỉnh (smooth với uniform)
            prior_probs = []
            total_samples = len(y_train)
            n_classes = len(self.label_encoder.classes_)
            
            for cls_idx in range(n_classes):
                count = np.sum(y_train == cls_idx)
                # Smooth với uniform distribution (Laplace smoothing concept)
                smoothed_prior = (count + 1) / (total_samples + n_classes)
                prior_probs.append(smoothed_prior)
            
            prior_probs = np.array(prior_probs)
            
            # Train với custom priors
            self.model = GaussianNB(priors=prior_probs)
            self.model.fit(X_train, y_train)
            
            # BƯỚC 6: Evaluate
            y_pred = self.model.predict(X_test)
            
            accuracy = accuracy_score(y_test, y_pred)
            balanced_acc = balanced_accuracy_score(y_test, y_pred)
            
            print(f"\n📈 Kết quả đánh giá:")
            print(f"   Accuracy: {accuracy:.2%}")
            print(f"   Balanced Accuracy: {balanced_acc:.2%}")
            print(f"   (Balanced Accuracy quan trọng hơn với imbalanced data)")
            
            # Classification report
            if len(set(y_test)) > 0:
                print("\n📊 Classification Report:")
                unique_labels = sorted(list(set(y_test) | set(y_pred)))
                target_names = [self.label_encoder.classes_[i] for i in unique_labels]
                print(classification_report(
                    y_test, y_pred, 
                    labels=unique_labels, 
                    target_names=target_names, 
                    zero_division=0
                ))
            
            # Confusion matrix
            print("\n🔢 Confusion Matrix:")
            cm = confusion_matrix(y_test, y_pred)
            print(cm)
            
            # BƯỚC 7: Lưu model
            model_data = {
                'model': self.model,
                'label_encoder': self.label_encoder,
                'symptom_list': self.symptom_list,
                'class_weights': class_weights,
                'training_info': {
                    'n_samples': len(X),
                    'n_features': X.shape[1],
                    'n_classes': len(self.label_encoder.classes_),
                    'balanced_accuracy': balanced_acc
                }
            }
            
            with open(self.model_file, 'wb') as f:
                pickle.dump(model_data, f)
            
            print(f"\n✅ Model đã lưu thành công tại: {self.model_file}")
            
            # Cảnh báo nếu accuracy quá thấp
            if balanced_acc < 0.5:
                print("\n⚠️  CẢNH BÁO: Balanced accuracy thấp!")
                print("   Khuyến nghị:")
                print("   1. Thêm nhiều dữ liệu training hơn")
                print("   2. Đảm bảo dữ liệu cân bằng giữa các loại bệnh")
                print("   3. Kiểm tra chất lượng triệu chứng trong dữ liệu")
            
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
    success = trainer.train(use_balancing=True)
    
    if success:
        print("\n✅ Hoàn tất! Model đã sẵn sàng sử dụng.")
    else:
        print("\n❌ Train thất bại!")
    
    print("=" * 60)