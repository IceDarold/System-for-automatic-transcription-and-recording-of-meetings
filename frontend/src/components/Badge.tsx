interface BadgeProps {
  text: string;
  color: string;
}

export default function Badge(props: BadgeProps) {
  return (
    <div className="badge" data-color-badge={props.color}>
      <p>{props.text}</p>
    </div>
  );
}
