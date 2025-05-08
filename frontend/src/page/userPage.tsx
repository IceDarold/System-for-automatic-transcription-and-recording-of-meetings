import { useParams } from "react-router-dom";
import Page from "./page";
import Card from "../components/Card";
import { useEffect, useState } from "react";
import { ApiLink, root } from "../config";

interface userData {
  first_name: string;
  last_name: string;
  middle_name: string;
  email: string;
}

export default function UserPage() {
  const { id } = useParams();
  const [dataUser, setDataUser] = useState<userData>();
  async function getUser() {
    const response = await fetch(root + ApiLink + `/users/${id}`);
    const respjs = await response.json();
    const data: userData = {
      first_name: respjs.first_name,
      last_name: respjs.last_name,
      middle_name: respjs.middle_name,
      email: respjs.email,
    };
    setDataUser(data);
    console.log(data);
  }
  useEffect(() => {
    getUser();
  }, []);
  return (
    <Page>
      <div className="Content">
        <div className="lk">
          <p className="h1-of-list">Мой профиль</p>
          <p className="stats">
            {dataUser ? dataUser.last_name : ""}{" "}
            {dataUser ? dataUser.first_name : ""}{" "}
            {dataUser ? dataUser.middle_name : ""}
          </p>
          <p className="stats">{dataUser ? dataUser.email : ""}</p>
        </div>
      </div>
    </Page>
  );
}
