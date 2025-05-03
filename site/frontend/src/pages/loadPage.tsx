import { useState, useEffect } from "react";
import placeholder from "../images/placeholder.jpg";
import FileDrop from "../components/DragAndDrop";
import info from "../images/info.svg";
import Header from "../components/Header";

export default function LoadPage() {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [source, setSource] = useState(".");
  const [thumbnail, setThumbnail] = useState<string | null>(null);
  const [videoSrc, setVideoSrc] = useState<string | null>(null);
  const [textForVideo, setTextForVideo] = useState<string | null>("");
  const [side, setSide] = useState<string | null>("left");
  useEffect(() => {
    const left = document.getElementById("left-panel");
    const right = document.getElementById("right-panel");
    if (side === "left") {
      if (left) {
        left.setAttribute("data-status", "active");
      }
      if (right) {
        right.setAttribute("data-status", "passive");
      }
    } else {
      if (left) {
        left.setAttribute("data-status", "passive");
      }
      if (right) {
        right.setAttribute("data-status", "active");
      }
    }
  });
  function setActiveSide(actSide: string) {
    setSide(actSide);
  }
  function setPreview(file: File | null) {
    if (file && file.type.startsWith("video/")) {
      const videoURL = URL.createObjectURL(file);
      setVideoSrc(videoURL);
      const videoElement = document.createElement("video");
      videoElement.src = videoURL;
      videoElement.crossOrigin = "anonymous"; // требуется для некоторых браузеров
      videoElement.currentTime = 1; // первый кадр (можно изменить)

      videoElement.addEventListener("loadeddata", () => {
        const canvas = document.createElement("canvas");
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;

        const ctx = canvas.getContext("2d");
        if (ctx) {
          ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
        }
        const thumbDataURL = canvas.toDataURL("image/png");
        setThumbnail(thumbDataURL);
      });
    } else if (file) {
      setThumbnail(placeholder);
    }
  }

  const handleFile = (file: File | null) => {
    console.log("Полученные файлы:", file);
    if (file) {
      setUploadedFile(file);
      setPreview(file);
      setTextForVideo(file.name);
    }
  };
  return (
    <div className="divContentView">
      <Header />
      <div className="mainContent">
        <div className="leftSide">
          <div className="step" id="firstStep">
            <p className="miniTitle">Видео</p>
            <div className="loadVideo">
              <div className="dropdown">
                <FileDrop onFileAccepted={handleFile} claass="maxi" />
              </div>
            </div>
          </div>
          <div id="loadingPage">
            <span className="loader"></span>
          </div>
          <div className="step" id="secondStep">
            <p className="bigTitle">Загруженное видео</p>
            <div className="videoPreview">
              <div className="photoView">
                {thumbnail ? (
                  <div>
                    <img src={thumbnail} alt="" className="imgsrc" />{" "}
                  </div>
                ) : null}
                <FileDrop onFileAccepted={handleFile} claass="mini" />
              </div>
              <p className="textUnderLine">{textForVideo}</p>
            </div>
          </div>
        </div>
        <div className="rightSide">
          <p className="bigTitle" id="noShowText">
            Предпросмотр
          </p>
          <div className="LogReport" id="LogReport">
            <img src={info} alt="" />
            <p>Предпросмотр добавится после загрузки</p>
          </div>
          <div className="panel" id="panel">
            <div className="panelHeader">
              <div
                id="left-panel"
                className="panelItem"
                data-status="active"
                onClick={() => {
                  setActiveSide("left");
                }}
              >
                <p>Чат</p>
              </div>
              <div
                id="right-panel"
                className="panelItem"
                data-status="passive"
                onClick={() => {
                  setActiveSide("right");
                }}
              >
                <p>Спикеры</p>
              </div>
            </div>
            <div className="contentRightSide"></div>
          </div>
        </div>
      </div>
    </div>
  );
}
