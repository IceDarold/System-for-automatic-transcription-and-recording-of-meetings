import { data } from "react-router-dom";
import Badge from "./Badge";

interface CardProps {
  key: number;
  main: string;
  date: string;
  badges: string[];
  speakers: string[];
  description: string;
  status: string;
}
export default function CardMyProject(props: CardProps) {
  let dataCard = [];
  let colors = ["yellow", "green"];
  for (let i = 0; i < Math.min(props.speakers.length, 3); i++) {
    dataCard.push({
      color: colors[i % colors.length],
      data: props.speakers[i],
    });
  }

  return (
    <div className="card">
      <div className="CardContent">
        <p className="card-main">{props.main}</p>
        <p className="card-date">{props.date}</p>
        <div className="card-badges">
          {props.badges.map((item) => (
            <Badge color="default" text={item} />
          ))}
        </div>
        <div className="card-speakers">
          {dataCard.map((item) => (
            <Badge color={item.color} text={item.data} />
          ))}
        </div>
        <p className="card-description">{props.description}</p>
        <div className="card-status">
          <Badge
            color={props.status === "Опубликовано" ? "green" : "yellow"}
            text={props.status}
          />
        </div>
      </div>
    </div>
  );
}
