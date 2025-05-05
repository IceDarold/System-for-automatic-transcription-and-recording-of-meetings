interface CardProps {
  key: string;
  main: string;
  date: string;
  badges: string[];
  speakers: string[];
  description: string;
  status: string;
}
export default function CardMyProject(props: CardProps) {
  return (
    <div className="card">
      <div className="CardContent">
        <p className="card-main">{props.main}</p>
      </div>
    </div>
  );
}
