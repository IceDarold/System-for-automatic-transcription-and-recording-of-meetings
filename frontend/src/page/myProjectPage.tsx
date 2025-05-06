import React from "react";
import Page from "./page";
function MyProjectPage() {
  const navigate = useNavigate();
  return (
    <Page>
      <div className="Content">
        <div className="panelFilters">
          <Searcher />
          <button
            className="primaryButton"
            onClick={() => {
              navigate("/create");
            }}
          >
            Создать проект
          </button>
        </div>
        <div className="myProjectsContent">
          {fakeData.map((item: CardData) => (
            <CardMyProject
              key={item.id}
              main={item.main}
              date={item.date}
              badges={item.badges}
              speakers={item.speakers}
              description={item.description}
              status={item.status}
            />
          ))}
        </div>
      </div>
    </Page>
  );
}

export default MyProjectPage;
