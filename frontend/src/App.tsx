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
import CreatePage from "./page/createPage";
import Meeting from "./page/Meeting";
import UserPage from "./page/userPage";
import { ProtectedRoute } from "./components/Protected";

function App() {
  return (
    <Router>
      <Routes>
        <Route>
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Navigate to="/allMeetings" replace />
              </ProtectedRoute>
            }
          />
          {/* -------Login----- */}
          <Route path="/login" element={<Login />} />
          <Route path="/user/:id" element={<UserPage />} />
          {/* ------AllMeetengs----- */}
          <Route path="/allMeetings" element={<AllMeetingsPage />} />
          <Route path="/meetings/:id" element={<Meeting />} />
          {/*----------My projects */}
          <Route path="/myMeetings" element={<MyProjectPage />} />
          <Route path="/create" element={<CreatePage />} />
          {/* -----Teams----- */}
          <Route path="/teams" element={<MyTeamsPage />} />
          <Route path="/teams/:id" element={<ProfleTeam />} />
          {/* --------DEV----- */}
          <Route path="/dev" element={<DevMode />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
