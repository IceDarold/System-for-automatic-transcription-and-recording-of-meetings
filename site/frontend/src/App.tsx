import "./App.css";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { useEffect, useState } from "react";

import Login from "./pages/loginPage";
import MyProjectPage from "./pages/myProjectPage";

function App() {
  const [access_token, setAccess_token] = useState<string | null>(
    localStorage.getItem("access_token")
  );
  useEffect(() => {
    setAccess_token(localStorage.getItem("access_token"));
  });
  return (
    <Router>
      <Routes>
        <Route>
          <Route
            path="/"
            element={
              access_token ? (
                <Navigate to="/allMeetings" replace />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route path="/allMeetings" element={<MyProjectPage />} />
          <Route path="/login" element={<Login />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
