import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import "./App.css";

import SpamDetector from "./User/khanhku";
import PatientStatistics from "./admin/PatientStatistics";
import Login from "./Login/Login";
import { LogIn } from "lucide-react";

function App() {
  return (
    <Router>
      <Routes>
       <Route path="/" element={<Login />} />
        {/* Trang thống kê */}
        <Route path="/admin" element={<PatientStatistics />} />
        {/* Trang Spam Detector */}
        <Route path="/spam" element={<SpamDetector />} />
      </Routes>
    </Router>
  );
}

export default App;
