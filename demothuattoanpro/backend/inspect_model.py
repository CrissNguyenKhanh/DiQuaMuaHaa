import pickle
import numpy as np

MODEL_FILE = "trained_model.pkl"

print("====================================")
print("🔍 KIỂM TRA NỘI DUNG MODEL PKL")
print("====================================")

try:
    # Load file PKL
    with open(MODEL_FILE, "rb") as f:
        data = pickle.load(f)

    print("\n📦 Các trường lưu trong file PKL:")
    for key in data.keys():
        print("  -", key)

    print("\n===============================")
    print("⚙️  THÔNG TIN MODEL")
    print("===============================")
    model = data.get("model")
    print("Loại model:", type(model))
    print("\nTham số model:")
    print(model.get_params())

    print("\n===============================")
    print("🏷️  LABEL ENCODER")
    print("===============================")
    label_encoder = data.get("label_encoder")
    if label_encoder:
        print("Classes:", label_encoder.classes_)

    print("\n===============================")
    print("🩺 DANH SÁCH TRIỆU CHỨNG")
    print("===============================")
    symptom_list = data.get("symptom_list", [])
    print(f"Tổng số triệu chứng: {len(symptom_list)}")
    print(symptom_list)

    print("\n===============================")
    print("⚖️ CLASS WEIGHTS")
    print("===============================")
    class_weights = data.get("class_weights")
    if class_weights is not None:
        for cls, weight in zip(label_encoder.classes_, class_weights):
            print(f"  {cls}: {weight:.3f}")

    print("\n===============================")
    print("📊 TRAINING INFO")
    print("===============================")
    training_info = data.get("training_info")
    print(training_info)

    print("\n====================================")
    print("🔮 TEST DỰ ĐOÁN (DEMO)")
    print("====================================")
    if symptom_list:
        # Tạo vector test demo
        test_vec = [1 if s == symptom_list[0] else 0 for s in symptom_list]
        test_vec += [25/100, 1]  # age + gender

        pred = model.predict([test_vec])[0]
        decoded = label_encoder.inverse_transform([pred])[0]

        print(f"Demo predict với triệu chứng `{symptom_list[0]}`:")
        print("➡️  Kết quả:", decoded)

except Exception as e:
    print("❌ Lỗi khi đọc file PKL:", e)
