import Page from "./page";
import FileDrop from "../components/DragAndDrop";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
export default function CreatePage() {
  const navigate = useNavigate();
  const [uploadedFile, setUploadedFile] = useState<File[] | null>(null);
  const handleFile = (files: File[] | null) => {
    console.log("Полученные файлы:", files);
    if (files) {
      setUploadedFile(files);
      navigate("/meetings/1");
    }
  };
  return (
    <Page>
      <div className="Content">
        <FileDrop onFileAccepted={handleFile} claass="mini" />
      </div>
    </Page>
  );
}
