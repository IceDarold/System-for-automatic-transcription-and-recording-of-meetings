import Page from "./page";
import Searcher from "../components/Searcher";
import { useNavigate } from "react-router-dom";
import CardMyProject from "../components/CardMyProject";

interface CardData {
  id: string;
  main: string;
  date: string;
  badges: string[];
  speakers: string[];
  description: string;
  status: string;
}
const fakeData: CardData[] = [
  {
    id: "1",
    main: "Запись конференции по улучшению финансовой системы",
    date: "19.11.2024",
    badges: ["Разработка систем по обеспечению полевых условий", "Посев полей"],
    speakers: ["Speaker_01", "Speaker_02"],
    description:
      "Задача засеивания полей решает огромную задачу по использованию пространства",
    status: "Опубликовано",
  },
  {
    id: "2",
    main: "Запись конференции по улучшению финансовой системы",
    date: "19.11.2024",
    badges: ["Разработка систем по обеспечению полевых условий", "Посев полей"],
    speakers: ["Speaker_01", "Speaker_02"],
    description:
      "Задача засеивания полей решает огромную задачу по использованию пространства",
    status: "Опубликовано",
  },
];
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
