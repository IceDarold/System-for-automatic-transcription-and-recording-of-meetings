import Page from "./page";
import FileDrop from "../components/DragAndDrop";
import { useState } from "react";
export default function CreatePage() {
  const [uploadedFile, setUploadedFile] = useState<File[] | null>(null);
  const handleFile = (files: File[] | null) => {
    console.log("Полученные файлы:", files);
    if (files) {
      setUploadedFile(files);
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
