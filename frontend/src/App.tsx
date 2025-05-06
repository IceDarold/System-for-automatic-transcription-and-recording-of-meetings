import "./App.css";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { useEffect, useState } from "react";
import Login from "./page/loginPage";
import MyProjectPage from "./page/myProjectPage";
import DevMode from "./page/DevPage";
import MyTeamsPage from "./page/myTeamsPage";
import AllMeetingsPage from "./page/allMeetingsPage";
import ProfleTeam from "./page/ProfileTeam";

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
          <Route path="/allMeetings" element={<AllMeetingsPage />} />
          <Route path="/teams" element={<MyTeamsPage />} />
          <Route path="/myMeetings" element={<MyProjectPage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/dev" element={<DevMode />} />
          <Route path="/teams/:id" element={<ProfleTeam />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
