import React, { useState, useRef, useEffect } from "react";
import { ApiLink } from "../config";

interface FileDropProps {
  onFileAccepted: (files: File[] | null) => void;
  claass: string;
}

const FileDrop: React.FC<FileDropProps> = ({ onFileAccepted, claass }) => {
  const root = "http://127.0.0.1:8000";
  const [isDragging, setIsDragging] = useState(false);
  const [isHover, setHover] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [textDrag, setTextDrag] = useState("Перетащите файлы сюда");

  const handleMouseEnter = () => {
    setHover(true);
  };

  const handleMouseLeave = () => {
    setHover(false);
  };

  async function setLoading(files: File[]) {
    console.log("loadfile");
    const inputPage = document.getElementById("firstStep");
    const loadingPage = document.getElementById("loadingPage");
    const secondPage = document.getElementById("secondStep");
    const logrep = document.getElementById("LogReport");
    const txt = document.getElementById("noShowText");
    if (inputPage) {
      inputPage.style.display = "none";
    }
    if (secondPage) {
      secondPage.style.display = "none";
    }
    if (loadingPage) {
      loadingPage.style.display = "flex";
    }
    const formData = new FormData();
    for (let i = 0; i < files.length; i += 1) {
      formData.append("audio", files[i]);
    }
    var status = "ok";
    try {
      const response = await fetch(root + ApiLink + "/loadvideo", {
        method: "POST",
        body: formData,
      });

      const result = await response.text();
      console.log("Response from server:", result);
    } catch (error) {
      console.error("Ошибка при отправке файла:", error);
      status = "no_ok";
    }
    if (status === "ok") {
      if (loadingPage) {
        loadingPage.style.display = "none";
      }
      if (secondPage) {
        secondPage.style.display = "flex";
      }
      if (logrep) {
        logrep.style.display = "none";
      }
      if (txt) {
        txt.style.display = "none";
      }
    }
  }
  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const files = Array.from(e.target.files);
      onFileAccepted(files);
      setLoading(files);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    // Необходимо, чтобы сработал drop
    e.dataTransfer.dropEffect = "copy";
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length) {
      onFileAccepted(files);
      setLoading(files);
    }
  };

  const openFileDialog = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <div
      className={claass}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={openFileDialog}
      onDragEnter={handleDragEnter}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      style={{
        border:
          isDragging || isHover ? "2px dashed #6366f1" : "2px dashed #373737",
        borderRadius: "8px",
        padding: "30px",
        textAlign: "center",
        color: isDragging || isHover ? "#6366f1" : "#a4a4a5",
        backgroundColor: "#1c1c1e",
        transition: "all 0.2s ease",
        cursor: "pointer",
      }}
    >
      {isDragging ? "Отпустите файлы здесь..." : textDrag}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        onChange={handleFileInputChange}
        style={{ display: "none" }}
        accept="video/*,audio/*"
      />
    </div>
  );
};

export default FileDrop;
