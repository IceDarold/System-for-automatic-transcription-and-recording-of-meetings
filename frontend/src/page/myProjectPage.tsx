import Page from "./page";
import Searcher from "../components/Searcher";
import { useNavigate } from "react-router-dom";
import CardMyProject from "../components/CardMyProject";
import { useEffect, useState } from "react";

interface CardData {
  id: number;
  main: string;
  date: string;
  badges: string[];
  speakers: string[];
  description: string;
  status: string;
}

function formater(data: { items: any[] }): CardData[] {
  return data.items.map((item) => ({
    id: item.id,
    main: item.title,
    date: new Date(item.date).toLocaleDateString(), // формат даты по-человечески
    badges: item.tags.map((tag: any) => tag.label),
    speakers: item.participants.map((participant: any) => participant.name),
    description: item.description,
    status: item.is_ready ? "Опубликовано" : "В работе",
  }));
}

const root = "http://127.0.0.1:8000";
function MyProjectPage() {
  const [CardDataLoad, setCardDataLoad] = useState<CardData[]>([]);
  const navigate = useNavigate();
  async function fetchMeetings() {
    try {
      const response = await fetch(root + "/api/v1/meetings", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Ошибка HTTP: ${response.status}`);
      }

      const data = await response.json(); // парсим JSON
      console.log("Данные с бэка:", data);
      setCardDataLoad(formater(data));
    } catch (error) {
      console.error("Ошибка при запросе:", error);
    }
  }
  useEffect(() => {
    fetchMeetings();
  });
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
          {CardDataLoad.map((item: CardData) => (
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
