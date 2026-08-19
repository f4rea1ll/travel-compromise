import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import JoinPage from "./pages/JoinPage";
import ResultPage from "./pages/ResultPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/session/:sessionId/join/:participantNumber" element={<JoinPage />} />
        <Route path="/session/:sessionId/result" element={<ResultPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;