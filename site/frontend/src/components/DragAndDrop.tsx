import React, { useState, useRef, useEffect } from "react";

interface FileDropProps {
  onFileAccepted: (file: File | null) => void;
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

  async function setLoading(file: File) {
    console.log("loadfile");
    const inputPage = document.getElementById("firstStep");
    const loadingPage = document.getElementById("loadingPage");
    const secondPage = document.getElementById("secondStep");
    const logrep = document.getElementById("LogReport");
    const txt = document.getElementById("noShowText");
    const panel = document.getElementById("panel");

    if (inputPage) {
      inputPage.style.display = "none";
    }
    if (secondPage) {
      secondPage.style.display = "none";
    }
    if (loadingPage) {
      loadingPage.style.display = "flex";
    }
    if (logrep) {
      logrep.style.display = "flex";
    }
    if (panel) {
      panel.style.display = "none";
    }
    const formData = new FormData();
    formData.append("video", file);
    var status = "ok";
    try {
      const response = await fetch(root + "/loadvideo", {
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
      if (panel) {
        panel.style.display = "flex";
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
    const files = e.target.files;
    if (files && files.length > 0) {
      onFileAccepted(files[0]);
      setLoading(files[0]);
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
      onFileAccepted(files[0]);
      setLoading(files[0]);
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
          isDragging || isHover ? "2px dashed #6366f1" : "2px dashed #ccc",
        borderRadius: "8px",
        padding: "30px",
        textAlign: "center",
        color: isDragging || isHover ? "#6366f1" : "#6d7885",
        backgroundColor: "#fff",
        transition: "all 0.2s ease",
        cursor: "pointer",
      }}
    >
      {isDragging ? "Отпустите файлы здесь..." : textDrag}
      <input
        ref={fileInputRef}
        type="file"
        accept="audio/*,video/*"
        onChange={handleFileInputChange}
        style={{ display: "none" }}
      />
    </div>
  );
};

export default FileDrop;
