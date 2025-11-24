import React, { useState, useEffect } from "react";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Users, Activity, TrendingUp, Brain, AlertCircle } from "lucide-react";
import "./PatientStatistics.css";

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#6366f1"];

const PatientStatistics = () => {
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("http://localhost:5000/api/statistics")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Lỗi kết nối đến server");
        }
        return response.json();
      })
      .then((data) => {
        setStats(data);
        setIsLoading(false);
        setError(null);
      })
      .catch((err) => {
        setError("Không thể kết nối đến server Python. Đảm bảo backend đang chạy.");
        setIsLoading(false);
        console.error("Error:", err);
      });
  }, []);

  if (isLoading) {
    return (
      <div className="patient-statistics-loading">
        <div className="patient-statistics-spinner"></div>
        <p>AI đang phân tích dữ liệu bệnh nhân...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="patient-statistics-error">
        <AlertCircle className="patient-statistics-error-icon" />
        <h2 className="patient-statistics-error-title">Lỗi kết nối</h2>
        <p className="patient-statistics-error-message">{error}</p>
        <button onClick={() => window.location.reload()} className="patient-statistics-retry-button">
          Thử lại
        </button>
      </div>
    );
  }

  if (!stats) return null;

  return (
    <div className="patient-statistics-container">
      <div className="patient-statistics-max-width">
        {/* Header */}
        <div className="patient-statistics-header">
          <div className="patient-statistics-icon-container">
            <Users className="patient-statistics-icon" />
          </div>
          <h1 className="patient-statistics-title">Thống Kê Bệnh Nhân</h1>
          <p className="patient-statistics-subtitle">
            Phân tích thông minh với AI về triệu chứng và chẩn đoán
          </p>
        </div>

        {/* Summary Cards */}
        <div className="patient-statistics-summary-grid">
          <div className="patient-statistics-summary-card">
            <Users className="patient-statistics-summary-icon" />
            <div>
              <h3 className="patient-statistics-summary-value">{stats.totalPatients}</h3>
              <p className="patient-statistics-summary-label">Tổng số bệnh nhân</p>
            </div>
          </div>

          <div className="patient-statistics-summary-card">
            <Activity className="patient-statistics-summary-icon" />
            <div>
              <h3 className="patient-statistics-summary-value">{stats.diagnosisStats?.length || 0}</h3>
              <p className="patient-statistics-summary-label">Loại chẩn đoán</p>
            </div>
          </div>

          <div className="patient-statistics-summary-card">
            <TrendingUp className="patient-statistics-summary-icon" />
            <div>
              <h3 className="patient-statistics-summary-value" style={{ fontSize: '1.2rem' }}>
                {stats.prediction || "N/A"}
              </h3>
              <p className="patient-statistics-summary-label">Xu hướng dự đoán</p>
            </div>
          </div>

          <div className="patient-statistics-summary-card">
            <Brain className="patient-statistics-summary-icon" />
            <div>
              <h3 className="patient-statistics-summary-value">AI</h3>
              <p className="patient-statistics-summary-label">Phân tích thông minh</p>
            </div>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="patient-statistics-charts-grid">
          
          {/* --- [FIXED] PIE CHART: Chẩn đoán --- */}
          {stats.diagnosisStats && stats.diagnosisStats.length > 0 && (
            <div className="patient-statistics-chart-card">
              <h2 className="patient-statistics-chart-title">Phân bố theo Chẩn đoán</h2>
              <div style={{ width: '100%', height: 350 }}> {/* Tăng chiều cao để chứa Legend */}
                <ResponsiveContainer>
                  <PieChart>
                    <Pie
                      data={stats.diagnosisStats}
                      cx="50%"
                      cy="45%" // Đẩy biểu đồ lên một chút để nhường chỗ cho Legend
                      labelLine={true} // Bật đường kẻ chỉ dẫn ra ngoài
                      label={({ name, percentage }) => `${percentage}%`} // Chỉ hiện % trên biểu đồ cho gọn
                      outerRadius={100} // Tăng kích thước biểu đồ
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {stats.diagnosisStats.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip 
                      formatter={(value, name, props) => [
                        `${value} ca (${props.payload.percentage}%)`, 
                        name
                      ]} 
                    />
                    <Legend 
                      layout="horizontal" 
                      verticalAlign="bottom" 
                      align="center"
                      wrapperStyle={{ fontSize: '12px', paddingTop: '20px' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Bar Chart - Triệu chứng */}
          {stats.symptomStats && stats.symptomStats.length > 0 && (
            <div className="patient-statistics-chart-card">
              <h2 className="patient-statistics-chart-title">Top Triệu chứng phổ biến</h2>
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={stats.symptomStats} margin={{ bottom: 40 }}> {/* Thêm margin bottom cho text nghiêng */}
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="name"
                    angle={-45}
                    textAnchor="end"
                    interval={0}
                    height={80}
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis allowDecimals={false} />
                  <Tooltip cursor={{ fill: '#f3f4f6' }} />
                  <Bar dataKey="value" name="Số lượng" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Bar Chart - Độ tuổi */}
          {stats.ageStats && stats.ageStats.length > 0 && (
            <div className="patient-statistics-chart-card">
              <h2 className="patient-statistics-chart-title">Phân bố theo Độ tuổi</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={stats.ageStats}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="value" name="Số lượng" fill="#10b981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Pie Chart - Giới tính (Giữ nguyên style gọn gàng) */}
          {stats.genderStats && stats.genderStats.length > 0 && (
            <div className="patient-statistics-chart-card">
              <h2 className="patient-statistics-chart-title">Phân bố theo Giới tính</h2>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={stats.genderStats}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percentage }) => `${name} (${percentage}%)`}
                    outerRadius={90}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {stats.genderStats.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend verticalAlign="bottom" height={36}/>
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Line Chart - Xu hướng */}
          {stats.trends && stats.trends.length > 0 && (
            <div className="patient-statistics-chart-card">
              <h2 className="patient-statistics-chart-title">Xu hướng theo thời gian</h2>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={stats.trends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="value"
                    name="Số ca khám"
                    stroke="#8b5cf6"
                    strokeWidth={3}
                    dot={{ r: 4 }}
                    activeDot={{ r: 8 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Bar Chart - Mức độ nghiêm trọng */}
          {stats.severityStats && stats.severityStats.length > 0 && (
            <div className="patient-statistics-chart-card">
              <h2 className="patient-statistics-chart-title">Mức độ nghiêm trọng</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={stats.severityStats}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="value" name="Số lượng" fill="#ef4444" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* AI Insights */}
        <div className="patient-statistics-insights-card">
          <div className="patient-statistics-insights-header">
            <Brain className="patient-statistics-insights-icon" />
            <h2 className="patient-statistics-insights-title">Phân tích AI</h2>
          </div>
          <div className="patient-statistics-insights-content">
            <p>
              <strong>Dự đoán xu hướng bệnh:</strong> {stats.prediction || "Chưa có dữ liệu"}
            </p>
            {stats.diagnosisStats && stats.diagnosisStats.length > 0 && (
              <p>
                <strong>Chẩn đoán phổ biến nhất:</strong>{" "}
                {stats.diagnosisStats[0]?.name} (chiếm {stats.diagnosisStats[0]?.percentage}%)
              </p>
            )}
            {stats.symptomStats && stats.symptomStats.length > 0 && (
              <p>
                <strong>Triệu chứng thường gặp:</strong>{" "}
                {stats.symptomStats[0]?.name} (xuất hiện {stats.symptomStats[0]?.value} lần)
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PatientStatistics;