import { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import CardMyProject from "../components/CardMyProject";
import Page from "./page";
import Badge from "../components/Badge";
import Icon from "../Icons/Icon";
import { ApiLink, root } from "../config";

interface PostData {
  link: string;
}

interface participant {
  name: string;
  id: string;
  role: string;
}

interface teamData {
  title: string;
  description: string;
  participants: participant[];
  posts: PostData[] | null;
}

interface Member {
  email: string;
  name: string;
  id: string;
}

interface usersId {
  ids: string[];
}

export default function ProfleTeam() {
  const location = useLocation();
  const [data, setData] = useState<teamData | null>(null);
  const [dataUsers, setDataUsers] = useState<Member[]>([]);
  const [dataMembers, setDataMembers] = useState<Member[]>([]);
  const [visible, setVisible] = useState<boolean>(false);
  const { id } = useParams();
  async function fetchUsers(id: string) {
    const response = await fetch(root + ApiLink + `/users/${id}`);
    const resp = await response.json();
    // console.log(resp);
    const dat: Member = {
      email: resp.email,
      name: resp.first_name + " " + resp.last_name,
      id: resp.id,
    };
    setDataUsers((prev) => [...prev, dat]);
  }
  async function fetchTeamMembers() {
    try {
      const response = await fetch(root + ApiLink + `/teams/${id}/members`);
      const data_resoponse_user = await response.json();
      setDataUsers([]);
      data_resoponse_user.ids.map((item: string) => {
        fetchUsers(item);
      });
      console.log(dataUsers, "datausers");
      setDataMembers(dataUsers);
      // console.log(dataMembers);
    } catch (e) {
      console.log(e);
    }
  }
  async function fetchTeamId() {
    const response = await fetch(root + ApiLink + `/teams/${id}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });
    if (!response.ok) {
      console.log("error");
    }
    const data_resp = await response.json();
    const data_form: teamData = {
      title: data_resp.title,
      description: data_resp.description,
      participants: data_resp.participants,
      posts: null,
    };
    setData(data_form);
  }
  const acceptRightPaddings = (visible: boolean) => {
    const arr = ["rightSideOfTeam", "mainContent"];
    for (let i = 0; i < arr.length; i += 1) {
      const el = document.getElementById(arr[i]);
      if (el) {
        if (!visible) {
          if (el.hasAttribute("data-right-padding")) {
            el.removeAttribute("data-right-padding");
          }
        } else {
          el.setAttribute("data-right-padding", "accept");
        }
      }
    }
  };
  useEffect(() => {
    fetchTeamId();
    fetchTeamMembers();
  }, []);
  useEffect(() => {
    acceptRightPaddings(visible);
  });
  if (data) {
    return (
      <Page>
        <div className="Content">
          <div className="divSidesOfTeams">
            <div className="leftSideOfTeam">
              <div className="contentInfoTeam">
                <CardMyProject
                  main={data.title}
                  description={data.description}
                  hover="false"
                  usekeyasid="false"
                />
                <CardMyProject
                  key="checkMembersOfThisTeam"
                  main="Посмотреть участников команды"
                  onClick={() => {
                    setVisible(!visible);
                    fetchTeamMembers();
                  }}
                  hover="true"
                />
              </div>
            </div>
            <div className="rightSideOfTeam" id="rightSideOfTeam">
              <div className="mainPartOfboardPosts">
                <div className="top-post-panel">
                  <Badge text="Все посты" color="gray" />
                </div>
                <div className="posts">
                  {data.posts ? (
                    data.posts.map((item: any) => <div>data.post.link</div>)
                  ) : (
                    <div className="emptyPosts">
                      <div>
                        <Icon color="#fff" type="milestone" />
                      </div>
                      <p>Встреч пока нет</p>
                    </div>
                  )}
                </div>
              </div>
              <div className="thirdBlockOfBoardPosts">
                {visible ? (
                  <div className="rightSidebar">
                    {dataMembers.map((item: Member) => (
                      <CardMyProject
                        main={item.name}
                        description={item.email}
                      />
                    ))}
                  </div>
                ) : (
                  <></>
                )}
              </div>
            </div>
          </div>
        </div>
      </Page>
    );
  } else {
    return (
      <Page>
        <div className="Content">404</div>
      </Page>
    );
  }
}
