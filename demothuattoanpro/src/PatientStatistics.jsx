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
import {
  Users,
  Activity,
  TrendingUp,
  Brain,
  AlertCircle,
} from "lucide-react";
import "./PatientStatistics.css";

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"];

const PatientStatistics = () => {
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Gọi API Python backend
    fetch('http://localhost:5000/api/statistics')
      .then(response => {
        if (!response.ok) {
          throw new Error('Lỗi kết nối đến server');
        }
        return response.json();
      })
      .then(data => {
        setStats(data);
        setIsLoading(false);
        setError(null);
      })
      .catch(err => {
        setError('Không thể kết nối đến server Python. Vui lòng đảm bảo server đang chạy tại http://localhost:5000');
        setIsLoading(false);
        console.error('Error:', err);
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
        <button 
          onClick={() => window.location.reload()} 
          className="patient-statistics-retry-button"
        >
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
              <h3 className="patient-statistics-summary-value">{stats.prediction || "N/A"}</h3>
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
          {/* Pie Chart - Chẩn đoán */}
          {stats.diagnosisStats && stats.diagnosisStats.length > 0 && (
            <div className="patient-statistics-chart-card">
              <h2 className="patient-statistics-chart-title">Phân bố theo Chẩn đoán</h2>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={stats.diagnosisStats}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percentage }) => `${name}: ${percentage}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {stats.diagnosisStats.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={COLORS[index % COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Bar Chart - Triệu chứng */}
          {stats.symptomStats && stats.symptomStats.length > 0 && (
            <div className="patient-statistics-chart-card">
              <h2 className="patient-statistics-chart-title">Top Triệu chứng phổ biến</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={stats.symptomStats}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="value" fill="#3b82f6" />
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
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="value" fill="#10b981" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Pie Chart - Giới tính */}
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
                    label={({ name, percentage }) => `${name}: ${percentage}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {stats.genderStats.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={COLORS[index % COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip />
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
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke="#8b5cf6"
                    strokeWidth={2}
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
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="value" fill="#ef4444" />
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
              <strong>Xu hướng:</strong> {stats.prediction || "N/A"}
            </p>
            {stats.diagnosisStats && stats.diagnosisStats.length > 0 && (
              <p>
                <strong>Chẩn đoán phổ biến nhất:</strong>{" "}
                {stats.diagnosisStats[0]?.name} (
                {stats.diagnosisStats[0]?.percentage}%)
              </p>
            )}
            {stats.symptomStats && stats.symptomStats.length > 0 && (
              <p>
                <strong>Triệu chứng phổ biến nhất:</strong>{" "}
                {stats.symptomStats[0]?.name} ({stats.symptomStats[0]?.value}{" "}
                lần xuất hiện)
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PatientStatistics;
