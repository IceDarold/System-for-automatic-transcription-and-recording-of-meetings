import { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
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

      <div className="sidebar-block-items">
        <div
          className="sidebar-item"
          id="sidebar-item-allMeetings"
          onClick={() => {
            handleClick("sidebar-item-allMeetings", "/allMeetings");
          }}
        >
          1
        </div>
        <div
          className="sidebar-item"
          id="sidebar-item-myMeetings"
          onClick={() => {
            handleClick("sidebar-item-myMeetings", "/myMeetings");
          }}
        >
          2
        </div>
        <div
          className="sidebar-item"
          id="sidebar-item-teams"
          onClick={() => {
            handleClick("sidebar-item-teams", "/teams");
          }}
        >
          3
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
      <div className="mainContent">{children}</div>
    </div>
  );
};

export default Page;
