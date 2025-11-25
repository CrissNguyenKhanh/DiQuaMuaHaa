import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import "./App.css";

import PatientStatistics from "./admin/PatientStatistics";
import Login from "./Login/Login";
import MedicalDiagnosisAI from "./User/khanhku";
import MedicalRecordConfirmation from "./User/vippoint";
import EnhancedPatientStatistics from "./User/endhaintstatics";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        {/* Trang thống kê */}
        <Route path="/admin" element={<PatientStatistics />} />
        {/* Trang Spam Detector */}
        <Route path="/spam" element={<MedicalDiagnosisAI />} />

        <Route path="/test1" element={<MedicalRecordConfirmation />} />
        {/* Trang Spam Detector */}
        <Route path="/test2" element={<EnhancedPatientStatistics />} />
      </Routes>
    </Router>
  );
}

export default App;
