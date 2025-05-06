import { data } from "react-router-dom";
import Badge from "./Badge";
import { useNavigate } from "react-router-dom";
import { hover } from "@testing-library/user-event/dist/hover";

interface CardProps {
  key?: string | number;
  main?: string;
  date?: string;
  badges?: string[];
  speakers?: string[];
  description?: string;
  status?: string;
  onClick?: () => void;
  hover?: "true" | "false";
  usekeyasid?: "true" | "false";
}
export default function CardMyProject(props: CardProps) {
  const navigate = useNavigate();
  let dataCard = [];
  let colors = ["yellow", "green"];
  if (props.speakers) {
    for (let i = 0; i < Math.min(props.speakers.length, 3); i++) {
      dataCard.push({
        color: colors[i % colors.length],
        data: props.speakers[i],
      });
    }
  }

  return (
    <div className="card">
      <div
        className="CardContent"
        onClick={props.onClick ?? undefined}
        data-hover-access={props.hover}
      >
        {props.main ? <p className="card-main">{props.main}</p> : <></>}
        {props.date ? <p className="card-date">{props.date}</p> : <></>}
        {props.badges ? (
          <div className="card-badges">
            {props.badges.map((item) => (
              <Badge color="default" text={item} />
            ))}
          </div>
        ) : (
          <></>
        )}
        {props.speakers ? (
          <div className="card-speakers">
            {dataCard.map((item) => (
              <Badge color={item.color} text={item.data} />
            ))}
          </div>
        ) : (
          <></>
        )}
        {props.description ? (
          <p className="card-description">{props.description}</p>
        ) : (
          <></>
        )}
        {props.status ? (
          <div className="card-status">
            <Badge
              color={props.status === "Опубликовано" ? "green" : "yellow"}
              text={props.status}
            />
          </div>
        ) : (
          <></>
        )}
      </div>
    </div>
  );
}
