import { Routes, Route } from "react-router-dom";
import LandingPage from "@/features/landing/LandingPage";
import AnalysisPage from "@/features/analysis/AnalysisPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/analyze" element={<AnalysisPage />} />
    </Routes>
  );
}