import { useEffect, useState } from "react";

export default function DevMode() {
  function clearStorage() {
    localStorage.clear();
  }
  const [sizeStorage, setSizeStorage] = useState(0);
  const [accept_token, setaccept_token] = useState<string | null>("");
  const [refresh_token, setrefresh_token] = useState<string | null>("");
  return (
    <>
      <button
        onClick={() => {
          setSizeStorage(localStorage.length);
          setaccept_token(localStorage.getItem("access_token"));
          setrefresh_token(localStorage.getItem("refresh_token"));
        }}
      >
        Обновить
      </button>
      <button onClick={clearStorage}>Очистить locale.storage</button>
      <p>Размер locale storage: {sizeStorage}</p>
      <p>Access token : {accept_token}</p>
      <p>Refresh token: {refresh_token}</p>
    </>
  );
}
//console.log(localStorage.length)
