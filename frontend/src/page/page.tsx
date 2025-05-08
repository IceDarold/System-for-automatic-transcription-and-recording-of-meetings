import { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import Icon from "../Icons/Icon";
function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  useEffect(() => {
    const els = document.querySelectorAll(".sidebar-item");
    for (let i = 0; i < els.length; i += 1) {
      if (
        els[i] &&
        els[i].id !== "sidebar-item-" + location.pathname.substring(1)
      ) {
        els[i].setAttribute("data-status-sidebar-item", "passive");
      }
    }
    const el = document.getElementById(
      "sidebar-item-" + location.pathname.substring(1)
    );
    if (el) {
      el.setAttribute("data-status-sidebar-item", "active");
    }
  });

  function handleClick(id: string, link: string) {
    if (location.pathname !== link) {
      navigate(link);
    }
  }
  return (
    <div className="sidebar">
      <div className="sidebar-logo">
        <p>L</p>
      </div>

      <div className="sidebar-items">
        <div className="sidebar-block-items">
          <div
            className="sidebar-item"
            id="sidebar-item-allMeetings"
            onClick={() => {
              handleClick("sidebar-item-allMeetings", "/allMeetings");
            }}
          >
            <Icon
              type="database"
              color={location.pathname === "/allMeetings" ? "#fff" : "#6366f1"}
            />
          </div>
          <div
            className="sidebar-item"
            id="sidebar-item-myMeetings"
            onClick={() => {
              handleClick("sidebar-item-myMeetings", "/myMeetings");
            }}
          >
            <Icon
              type="file-text"
              color={location.pathname === "/myMeetings" ? "#fff" : "#6366f1"}
            />
          </div>
          <div
            className="sidebar-item"
            id="sidebar-item-teams"
            onClick={() => {
              handleClick("sidebar-item-teams", "/teams");
            }}
          >
            <Icon
              type="briefcase"
              color={location.pathname === "/teams" ? "#fff" : "#6366f1"}
            />
          </div>
        </div>
        <div
          className="sidebar-item"
          onClick={() => {
            localStorage.clear();
            navigate("/");
          }}
        >
          <Icon type="logout" color={"#6366f1"} />
        </div>
      </div>
    </div>
  );
}

interface PageProps {
  children: React.ReactNode;
}

const Page: React.FC<PageProps> = ({ children }) => {
  return (
    <div className="page">
      <Sidebar />
      <div className="mainContent" id="mainContent">
        {children}
      </div>
    </div>
  );
};

export default Page;
