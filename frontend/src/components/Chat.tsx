import { useState } from "react";
import { root } from "../config";

interface chatProps {
  sendLink: string;
}

interface chatMes {
  type: "bot" | "user";
  text: string;
}

export default function Chat(props: chatProps) {
  const [session, setSession] = useState<chatMes[]>([]);
  const [value, setValue] = useState<string>("");
  return (
    <div className="chat">
      <div className="contentSessionChat">
        {session.map((item: chatMes) => (
          <div className={"message-type-" + item.type}>{item.text}</div>
        ))}
      </div>
      <div className="inputMessageChat">
        <textarea
          placeholder="Чем я могу помочь вам сегодня?"
          value={value}
          onChange={(e) => {
            setValue(e.target.value);
          }}
        ></textarea>
        <button className="primaryButton">➤</button>
      </div>
    </div>
  );
}
