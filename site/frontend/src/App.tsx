import "./App.css";
import LoadPage from "./pages/loadPage";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Outlet,
} from "react-router-dom";

import Sidebar from "./components/Sidebar";
import Login from "./pages/loginPage";

const Layout = () => (
  <div>
    <Sidebar />
    <div>
      <Outlet />
    </div>
  </div>
);

function App() {
  return (
    <Router>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<LoadPage />} />
          <Route path="/login" element={<Login />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
