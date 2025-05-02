import { useState } from "react";
import React from "react";
import "./App.css";
import FileDrop from "./components/DragAndDrop";
import placeholder from "./images/placeholder.jpg";
import info from "./images/info.svg";

function App() {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [source, setSource] = useState(".");
  const [thumbnail, setThumbnail] = useState<string | null>(null);
  const [videoSrc, setVideoSrc] = useState<string | null>(null);
  const [textForVideo, setTextForVideo] = useState<string | null>("");
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
    <div className="App">
      <div className="header"></div>
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
                  <img src={thumbnail} alt="" className="imgsrc" />
                ) : null}
                <div className="upload">
                  <FileDrop onFileAccepted={handleFile} claass="mini" />
                </div>
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
              <div className="panel" data-status="active">
                Чат
              </div>
              <div className="panel" data-status="passive">
                Спикеры
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
