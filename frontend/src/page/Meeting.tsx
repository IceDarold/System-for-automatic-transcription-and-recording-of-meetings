import { useParams } from "react-router-dom";
import { root } from "../config";
import Page from "./page";
import { ApiLink } from "../config";
import Chat from "../components/Chat";
import AudioPlayer from "../components/AudioPlayer";
import { useEffect, useState } from "react";
import Badge from "../components/Badge";
interface DataFormat {
  title: string;
  tags: string[];
  description: string;
}

function formattedData(data: any) {
  const dataF: DataFormat = {
    title: data.title,
    tags: data.tags,
    description: data.description,
  };
  return dataF;
}

export default function Meeting() {
  const { id } = useParams();
  const [audio, setAudio] = useState("");
  const [activePanel, setActivePanel] = useState("chat");
  const [data, setData] = useState<DataFormat>();
  async function fetchAudio() {
    try {
      const response = await fetch(root + ApiLink + `/meetings/${id}/audio`);
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      setAudio(url);
    } catch (e) {
      console.log(e);
    }
  }
  async function fetchData() {
    try {
      const response = await fetch(root + ApiLink + `/meetings/${id}`);
      const data_resp = await response.json();
      setData(formattedData(data_resp));
      console.log(data_resp);
    } catch (e) {
      console.log(e);
    }
  }
  useEffect(() => {
    fetchAudio();
    fetchData();
  }, []);
  const linkMesWithChat = `/meetings/${id}/chat`;
  return (
    <Page>
      <div className="Content">
        <div className="sidesOnMeetings">
          <div className="leftSideOnMeetings">
            <p className="h1-of-list">{data ? data.title : "Без названия"}</p>
            <div className="audio">
              <AudioPlayer src={audio} />
            </div>
            <div className="BagdesArea">
              {data ? (
                data.tags.map((item: string) => (
                  <Badge color="gray" text={item} />
                ))
              ) : (
                <></>
              )}
            </div>
            <p className="description-card">{data ? data.description : ""}</p>
          </div>
          <div className="rightSideOnMeetings">
            <div className="panel-tabs">
              <div
                className="panelSelect"
                data-panel-selected={activePanel === "chat" ? "true" : "false"}
                onClick={() => {
                  setActivePanel("chat");
                }}
              >
                <p>AI Chat</p>
              </div>
              <div
                className="panelSelect"
                data-panel-selected={
                  activePanel === "diarization" ? "true" : "false"
                }
                onClick={() => {
                  setActivePanel("diarization");
                }}
              >
                <p>Транскрибация</p>
              </div>
            </div>
            <div className="contentInPanelView">
              <div
                style={{ display: activePanel === "chat" ? "flex" : "none" }}
              >
                <Chat sendLink={linkMesWithChat} />
              </div>
              <div
                style={{
                  display: activePanel === "diarization" ? "flex" : "none",
                }}
              >
                <div>Тут пока ничего нет</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Page>
  );
}
