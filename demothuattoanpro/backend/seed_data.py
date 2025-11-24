import random
import json
from data.database import Database

# 1. Định nghĩa "Kiến thức y khoa" cơ bản để sinh dữ liệu hợp lý
# Cấu trúc: "Tên bệnh": ["Danh sách các triệu chứng có thể gặp"]
DISEASE_KNOWLEDGE = {
    "Cảm cúm": [
        "Sốt cao", "Ho khan", "Đau đầu", "Mệt mỏi", "Đau họng", "Sổ mũi", "Ớn lạnh"
    ],
    "Viêm phổi": [
        "Ho có đờm", "Sốt cao", "Khó thở", "Đau tức ngực", "Mệt mỏi", "Vã mồ hôi", "Nhịp tim nhanh"
    ],
    "Viêm dạ dày": [
        "Đau thượng vị", "Buồn nôn", "Ợ chua", "Đầy bụng", "Chán ăn", "Nôn", "Sụt cân"
    ],
    "Tăng huyết áp": [
        "Đau đầu", "Chóng mặt", "Hoa mắt", "Ù tai", "Mất ngủ", "Đỏ mặt", "Tim đập nhanh"
    ],
    "Tiểu đường Type 2": [
        "Khát nước nhiều", "Đi tiểu nhiều", "Sụt cân bất thường", "Mờ mắt", "Vết thương lâu lành", "Hay đói"
    ],
    "Dị ứng thời tiết": [
        "Hắt hơi", "Ngứa mũi", "Nổi mẩn đỏ", "Ngứa da", "Chảy nước mắt", "Phát ban"
    ],
    "Rối loạn tiền đình": [
        "Chóng mặt", "Mất thăng bằng", "Buồn nôn", "Ù tai", "Sợ ánh sáng", "Mệt mỏi"
    ],
    "Viêm khớp": [
        "Đau khớp", "Sưng khớp", "Cứng khớp buổi sáng", "Khó vận động", "Phát ra tiếng kêu khi cử động"
    ]
}

SEVERITY_LEVELS = ["Nhẹ", "Trung bình", "Nặng", "Nguy kịch"]

def generate_fake_data(num_records=500):
    print(f"🚀 Đang bắt đầu sinh {num_records} dữ liệu mẫu...")
    
    db = Database()
    count = 0
    
    for _ in range(num_records):
        # 1. Chọn ngẫu nhiên một bệnh
        diagnosis = random.choice(list(DISEASE_KNOWLEDGE.keys()))
        
        # 2. Chọn ngẫu nhiên 2 đến 4 triệu chứng từ danh sách của bệnh đó
        # (Để AI học được rằng không phải lúc nào cũng có đủ 100% triệu chứng)
        possible_symptoms = DISEASE_KNOWLEDGE[diagnosis]
        num_symptoms = random.randint(2, min(4, len(possible_symptoms)))
        selected_symptoms = random.sample(possible_symptoms, num_symptoms)
        
        # 3. Sinh tuổi và giới tính phù hợp ngữ cảnh (cơ bản)
        gender = random.choice(["Nam", "Nữ"])
        
        # Một số bệnh thường gặp ở người già hơn
        if diagnosis in ["Tăng huyết áp", "Tiểu đường Type 2", "Viêm khớp", "Rối loạn tiền đình"]:
            age = random.randint(40, 85)
        else:
            age = random.randint(18, 60)
            
        # 4. Mức độ nghiêm trọng ngẫu nhiên
        severity = random.choice(SEVERITY_LEVELS)
        
        # 5. Thêm vào Database
        try:
            db.add_training_data(
                symptoms=selected_symptoms,
                age=age,
                gender=gender,
                diagnosis=diagnosis,
                severity=severity
            )
            count += 1
            if count % 100 == 0:
                print(f"   ... Đã thêm {count} bản ghi")
        except Exception as e:
            print(f"❌ Lỗi khi thêm bản ghi: {e}")

    print(f"\n✅ HOÀN TẤT! Đã thêm thành công {count} dữ liệu vào database.")
    print("👉 Hãy chạy lại 'python auto_train_model.py' để AI học dữ liệu mới này.")

if __name__ == "__main__":
    # Bạn có thể sửa số lượng muốn tạo ở đây
    generate_fake_data(500)