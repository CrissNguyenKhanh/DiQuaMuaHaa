import React, { useState } from "react";
import { Mail, Shield, AlertTriangle, CheckCircle, Zap } from "lucide-react";

const SpamDetector = () => {
  const [email, setEmail] = useState("");
  const [result, setResult] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Naive Bayes implementation
  const trainingData = [
    {
      text: "Chúc mừng bạn đã trúng giải 100 triệu đồng! Nhấn vào link để nhận ngay",
      label: "spam",
    },
    {
      text: "Vay tiền nhanh chóng, lãi suất thấp, không cần thế chấp. Liên hệ ngay",
      label: "spam",
    },
    {
      text: "Khuyến mãi đặc biệt! Giảm giá 90% cho tất cả sản phẩm. Mua ngay",
      label: "spam",
    },
    {
      text: "Bạn đã được chọn để nhận quà miễn phí trị giá 50 triệu",
      label: "spam",
    },
    {
      text: "Cơ hội kiếm tiền từ nhà chỉ với 2 giờ mỗi ngày. Thu nhập lên đến 20 triệu",
      label: "spam",
    },
    { text: "Xin chào, tôi muốn hỏi về dự án chúng ta đang làm", label: "ham" },
    {
      text: "Cuộc họp ngày mai sẽ diễn ra lúc 9 giờ sáng tại phòng họp A",
      label: "ham",
    },
    {
      text: "Cảm ơn bạn đã gửi báo cáo. Tôi sẽ xem xét và phản hồi sớm",
      label: "ham",
    },
    {
      text: "Bạn có thể gửi cho tôi file tài liệu về dự án không?",
      label: "ham",
    },
    {
      text: "Chúc mừng sinh nhật! Chúc bạn luôn khỏe mạnh và hạnh phúc",
      label: "ham",
    },
  ];

  const preprocess = (text) => {
    return text
      .toLowerCase()
      .replace(
        /[^a-záàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ\s]/g,
        ""
      )
      .split(/\s+/)
      .filter((w) => w.length > 0);
  };

  const trainModel = () => {
    const wordFreqSpam = {};
    const wordFreqHam = {};
    let totalWordsSpam = 0;
    let totalWordsHam = 0;
    let spamCount = 0;
    let hamCount = 0;
    const vocabulary = new Set();

    trainingData.forEach(({ text, label }) => {
      const words = preprocess(text);
      words.forEach((w) => vocabulary.add(w));

      if (label === "spam") {
        spamCount++;
        words.forEach((w) => {
          wordFreqSpam[w] = (wordFreqSpam[w] || 0) + 1;
          totalWordsSpam++;
        });
      } else {
        hamCount++;
        words.forEach((w) => {
          wordFreqHam[w] = (wordFreqHam[w] || 0) + 1;
          totalWordsHam++;
        });
      }
    });

    return {
      wordFreqSpam,
      wordFreqHam,
      totalWordsSpam,
      totalWordsHam,
      spamCount,
      hamCount,
      vocabulary,
      priorSpam: spamCount / (spamCount + hamCount),
      priorHam: hamCount / (spamCount + hamCount),
    };
  };

  const predict = (emailContent) => {
    const model = trainModel();
    const words = preprocess(emailContent);
    const vocabSize = model.vocabulary.size;

    let logProbSpam = Math.log(model.priorSpam);
    let logProbHam = Math.log(model.priorHam);

    words.forEach((word) => {
      if (model.vocabulary.has(word)) {
        const probSpam =
          ((model.wordFreqSpam[word] || 0) + 1) /
          (model.totalWordsSpam + vocabSize);
        const probHam =
          ((model.wordFreqHam[word] || 0) + 1) /
          (model.totalWordsHam + vocabSize);

        logProbSpam += Math.log(probSpam);
        logProbHam += Math.log(probHam);
      }
    });

    const expSpam = Math.exp(logProbSpam);
    const expHam = Math.exp(logProbHam);
    const confidence =
      logProbSpam > logProbHam
        ? expSpam / (expSpam + expHam)
        : expHam / (expSpam + expHam);

    return {
      label: logProbSpam > logProbHam ? "spam" : "ham",
      confidence: confidence * 100,
    };
  };

  const handleAnalyze = () => {
    if (!email.trim()) return;
    setIsAnalyzing(true);

    setTimeout(() => {
      const prediction = predict(email);
      setResult(prediction);
      setIsAnalyzing(false);
    }, 800);
  };

  return (
    <div style={styles.container}>
      <div style={styles.maxWidth}>
        {/* Header */}
        <div style={styles.header}>
          <div style={styles.iconContainer}>
            <Shield style={styles.icon} />
          </div>
          <h1 style={styles.title}>AI Spam Detector</h1>
          <p style={styles.subtitle}>
            Phát hiện email spam thông minh với thuật toán Naive Bayes
          </p>
        </div>

        {/* Main Card */}
        <div style={styles.mainCard}>
          <div style={styles.formGroup}>
            <label style={styles.label}>
              <Mail style={styles.labelIcon} />
              Nội dung email cần kiểm tra
            </label>
            <textarea
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Nhập hoặc dán nội dung email vào đây..."
              style={styles.textarea}
            />
          </div>

          <button
            onClick={handleAnalyze}
            disabled={!email.trim() || isAnalyzing}
            style={{
              ...styles.button,
              ...((!email.trim() || isAnalyzing) && styles.buttonDisabled),
            }}
          >
            {isAnalyzing ? (
              <>
                <div style={styles.spinner}></div>
                Đang phân tích...
              </>
            ) : (
              <>
                <Zap style={styles.buttonIcon} />
                Phân tích Email
              </>
            )}
          </button>
        </div>

        {/* Result Card */}
        {result && (
          <div
            style={
              result.label === "spam"
                ? styles.resultCardSpam
                : styles.resultCardHam
            }
          >
            <div style={styles.resultContent}>
              <div
                style={
                  result.label === "spam"
                    ? styles.resultIconSpam
                    : styles.resultIconHam
                }
              >
                {result.label === "spam" ? (
                  <AlertTriangle style={styles.resultIconSvg} />
                ) : (
                  <CheckCircle style={styles.resultIconSvg} />
                )}
              </div>

              <div style={styles.resultTextContainer}>
                <h2
                  style={
                    result.label === "spam"
                      ? styles.resultTitleSpam
                      : styles.resultTitleHam
                  }
                >
                  {result.label === "spam"
                    ? "🚨 Email SPAM Phát Hiện!"
                    : "✅ Email An Toàn"}
                </h2>

                <div style={styles.confidenceSection}>
                  <div style={styles.confidenceRow}>
                    <span style={styles.confidenceLabel}>Độ tin cậy:</span>
                    <span
                      style={
                        result.label === "spam"
                          ? styles.confidenceValueSpam
                          : styles.confidenceValueHam
                      }
                    >
                      {result.confidence.toFixed(1)}%
                    </span>
                  </div>
                  <div style={styles.progressBar}>
                    <div
                      style={{
                        ...styles.progressFill,
                        ...(result.label === "spam"
                          ? styles.progressFillSpam
                          : styles.progressFillHam),
                        width: `${result.confidence}%`,
                      }}
                    ></div>
                  </div>
                </div>

                <div
                  style={
                    result.label === "spam"
                      ? styles.recommendationSpam
                      : styles.recommendationHam
                  }
                >
                  <p
                    style={
                      result.label === "spam"
                        ? styles.recommendationTitleSpam
                        : styles.recommendationTitleHam
                    }
                  >
                    💡 Khuyến nghị:
                  </p>
                  <p
                    style={
                      result.label === "spam"
                        ? styles.recommendationTextSpam
                        : styles.recommendationTextHam
                    }
                  >
                    {result.label === "spam"
                      ? "Cẩn thận! Không nên click vào link hoặc cung cấp thông tin cá nhân. Đây có thể là email lừa đảo."
                      : "Email này có vẻ an toàn. Tuy nhiên, vẫn nên kiểm tra kỹ người gửi và nội dung."}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Info Footer */}
        <div style={styles.footer}>
          <p>Sử dụng thuật toán Naive Bayes với Laplace Smoothing</p>
          <p style={styles.footerSecond}>
            Độ chính xác phụ thuộc vào dữ liệu huấn luyện
          </p>
        </div>
      </div>

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
};

const styles = {
  container: {
    minHeight: "100vh",
    background: "linear-gradient(to bottom right, #eff6ff, #e0e7ff, #f3e8ff)",
    padding: "24px",
  },
  maxWidth: {
    maxWidth: "896px",
    margin: "0 auto",
  },
  header: {
    textAlign: "center",
    marginBottom: "32px",
  },
  iconContainer: {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    width: "80px",
    height: "80px",
    background: "linear-gradient(to bottom right, #3b82f6, #9333ea)",
    borderRadius: "16px",
    marginBottom: "16px",
    boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
  },
  icon: {
    width: "40px",
    height: "40px",
    color: "white",
  },
  title: {
    fontSize: "36px",
    fontWeight: "bold",
    color: "#1f2937",
    marginBottom: "8px",
  },
  subtitle: {
    color: "#4b5563",
  },
  mainCard: {
    backgroundColor: "white",
    borderRadius: "24px",
    boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
    padding: "32px",
    marginBottom: "24px",
  },
  formGroup: {
    marginBottom: "24px",
  },
  label: {
    display: "flex",
    alignItems: "center",
    fontSize: "18px",
    fontWeight: "600",
    color: "#374151",
    marginBottom: "12px",
  },
  labelIcon: {
    width: "20px",
    height: "20px",
    marginRight: "8px",
    color: "#4f46e5",
  },
  textarea: {
    width: "100%",
    height: "160px",
    padding: "12px 16px",
    border: "2px solid #e5e7eb",
    borderRadius: "12px",
    fontSize: "16px",
    color: "#374151",
    resize: "none",
    outline: "none",
    transition: "border-color 0.2s",
    fontFamily: "inherit",
    boxSizing: "border-box",
  },
  button: {
    width: "100%",
    background: "linear-gradient(to right, #3b82f6, #9333ea)",
    color: "white",
    fontWeight: "600",
    padding: "16px",
    borderRadius: "12px",
    border: "none",
    cursor: "pointer",
    transition: "all 0.3s",
    boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "16px",
  },
  buttonDisabled: {
    opacity: 0.5,
    cursor: "not-allowed",
  },
  buttonIcon: {
    width: "20px",
    height: "20px",
    marginRight: "8px",
  },
  spinner: {
    width: "20px",
    height: "20px",
    border: "2px solid transparent",
    borderBottomColor: "white",
    borderRadius: "50%",
    animation: "spin 1s linear infinite",
    marginRight: "8px",
  },
  resultCardSpam: {
    background: "linear-gradient(to bottom right, #fef2f2, #fff7ed)",
    border: "2px solid #fecaca",
    borderRadius: "24px",
    boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
    padding: "32px",
    animation: "fadeIn 0.5s ease-out",
  },
  resultCardHam: {
    background: "linear-gradient(to bottom right, #f0fdf4, #d1fae5)",
    border: "2px solid #bbf7d0",
    borderRadius: "24px",
    boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
    padding: "32px",
    animation: "fadeIn 0.5s ease-out",
  },
  resultContent: {
    display: "flex",
    alignItems: "flex-start",
  },
  resultIconSpam: {
    flexShrink: 0,
    width: "64px",
    height: "64px",
    borderRadius: "16px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#ef4444",
    boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
  },
  resultIconHam: {
    flexShrink: 0,
    width: "64px",
    height: "64px",
    borderRadius: "16px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#22c55e",
    boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
  },
  resultIconSvg: {
    width: "32px",
    height: "32px",
    color: "white",
  },
  resultTextContainer: {
    marginLeft: "24px",
    flex: 1,
  },
  resultTitleSpam: {
    fontSize: "24px",
    fontWeight: "bold",
    color: "#b91c1c",
    marginBottom: "8px",
  },
  resultTitleHam: {
    fontSize: "24px",
    fontWeight: "bold",
    color: "#15803d",
    marginBottom: "8px",
  },
  confidenceSection: {
    marginBottom: "16px",
  },
  confidenceRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "8px",
  },
  confidenceLabel: {
    color: "#374151",
    fontWeight: "500",
  },
  confidenceValueSpam: {
    fontSize: "20px",
    fontWeight: "bold",
    color: "#dc2626",
  },
  confidenceValueHam: {
    fontSize: "20px",
    fontWeight: "bold",
    color: "#16a34a",
  },
  progressBar: {
    width: "100%",
    backgroundColor: "#e5e7eb",
    borderRadius: "9999px",
    height: "12px",
    overflow: "hidden",
  },
  progressFill: {
    height: "100%",
    borderRadius: "9999px",
    transition: "width 1s",
  },
  progressFillSpam: {
    background: "linear-gradient(to right, #ef4444, #f97316)",
  },
  progressFillHam: {
    background: "linear-gradient(to right, #22c55e, #10b981)",
  },
  recommendationSpam: {
    padding: "16px",
    borderRadius: "12px",
    backgroundColor: "#fee2e2",
  },
  recommendationHam: {
    padding: "16px",
    borderRadius: "12px",
    backgroundColor: "#dcfce7",
  },
  recommendationTitleSpam: {
    fontWeight: "600",
    marginBottom: "4px",
    color: "#991b1b",
  },
  recommendationTitleHam: {
    fontWeight: "600",
    marginBottom: "4px",
    color: "#14532d",
  },
  recommendationTextSpam: {
    color: "#b91c1c",
  },
  recommendationTextHam: {
    color: "#15803d",
  },
  footer: {
    marginTop: "32px",
    textAlign: "center",
    color: "#6b7280",
    fontSize: "14px",
  },
  footerSecond: {
    marginTop: "4px",
  },
};

export default SpamDetector;
