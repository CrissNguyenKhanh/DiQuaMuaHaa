import os
import numpy as np
from PIL import Image
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

# 1. Cấu hình
DATA_DIR = 'dataset'
IMG_SIZE = (64, 64)
MODEL_FILE = 'simple_image_model.pkl'

def load_data():
    images = []
    labels = []
    classes = []
    
    if not os.path.exists(DATA_DIR):
        print(f"Lỗi: Không tìm thấy thư mục '{DATA_DIR}'")
        return None, None, None

    print("Đang đọc dữ liệu ảnh...")
    # --- SỬA QUAN TRỌNG: Thêm sorted() để cố định thứ tự ---
    sorted_folders = sorted(os.listdir(DATA_DIR))
    
    for idx, class_name in enumerate(sorted_folders):
        class_dir = os.path.join(DATA_DIR, class_name)
        if os.path.isdir(class_dir):
            classes.append(class_name)
            print(f" - Lớp {idx}: {class_name} (Đang xử lý...)") 
            
            count = 0
            for img_name in os.listdir(class_dir):
                img_path = os.path.join(class_dir, img_name)
                try:
                    # Chuyển đen trắng + Resize
                    img = Image.open(img_path).convert('L') 
                    img = img.resize(IMG_SIZE)
                    
                    img_array = np.array(img).flatten()
                    
                    images.append(img_array)
                    labels.append(idx)
                    count += 1
                except Exception as e:
                    pass
            print(f"   -> Đã đọc {count} ảnh.")

    return np.array(images), np.array(labels), classes

# 2. Thực thi
X, y, class_names = load_data()

if X is not None and len(X) > 0:
    print(f"\nTổng số ảnh: {len(X)}")
    print(f"Mapping nhãn: {dict(enumerate(class_names))}") # Kiểm tra xem 0 là bệnh gì, 1 là bệnh gì
    
    # Chia dữ liệu
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Đang train model (Random Forest)...")
    # Tăng số cây lên 200 để học kỹ hơn
    clf = RandomForestClassifier(n_estimators=200, random_state=42) 
    clf.fit(X_train, y_train)

    # Kiểm tra độ chính xác
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Độ chính xác trên tập test: {acc * 100:.2f}%")
    
    # In báo cáo chi tiết xem nó hay đoán sai lớp nào
    print("\nChi tiết hiệu năng:")
    print(classification_report(y_test, y_pred, target_names=class_names))

    # Lưu model
    joblib.dump(clf, MODEL_FILE)
    joblib.dump(class_names, 'class_names.pkl')
    print("✓ Đã lưu model thành công!")
else:
    print("Không có dữ liệu.")