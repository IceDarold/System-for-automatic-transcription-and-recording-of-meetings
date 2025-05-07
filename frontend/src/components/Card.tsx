import React from "react";
interface PageProps {
  children: React.ReactNode;
  flexDirection?: React.CSSProperties["flexDirection"];
}
export default function Card(props: PageProps) {
  return (
    <div
      className="Card"
      style={{ flexDirection: props.flexDirection ?? "column" }}
    >
      {props.children}
    </div>
  );
}
