import pickle
import os

# File paths
MODEL_FILE = "model.pkl"
VECTORIZER_FILE = "vectorizer.pkl"
DISEASE_DATA_FILE = "disease_data.pkl"

# Hàm load file pkl
def load_pkl_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return pickle.load(f)
    else:
        print(f"❌ File not found: {file_path}")
        return None

# Load từng file
model = load_pkl_file(MODEL_FILE)
vectorizer = load_pkl_file(VECTORIZER_FILE)
disease_data = load_pkl_file(DISEASE_DATA_FILE)

# Kiểm tra
print("Model loaded:", model is not None)
print("Vectorizer loaded:", vectorizer is not None)
print("Disease data loaded:", disease_data is not None)

# Nếu muốn xem dữ liệu disease_data
if disease_data:
    for disease, info in disease_data.items():
        print(f"Disease: {disease}, Severity: {info['severity']}, Recommendations: {info['recommendations']}")
