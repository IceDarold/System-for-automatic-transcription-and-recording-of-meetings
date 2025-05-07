import { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import CardMyProject from "../components/CardMyProject";
import Page from "./page";
import Badge from "../components/Badge";
import Icon from "../Icons/Icon";
import { root } from "../config";

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

export function RightSidebar(props: any) {
  const email = "fake@email.ru";
  if (props.visble) {
    return (
      <div className="rightSidebar">
        <CardMyProject main={props.title} description={email} />
        <CardMyProject main={props.title} description={email} />
        <CardMyProject main={props.title} description={email} />
        <CardMyProject main={props.title} description={email} />
        <CardMyProject main={props.title} description={email} />
      </div>
    );
  } else {
    return <></>;
  }
}

export default function ProfleTeam() {
  const location = useLocation();
  const [data, setData] = useState<teamData | null>(null);
  const [visible, setVisible] = useState<boolean>(false);
  const { id } = useParams();
  async function fetchTeamId() {
    const response = await fetch(root + `/api/v1/teams/${id}`, {
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
                      <p>Постов пока нет</p>
                    </div>
                  )}
                </div>
              </div>
              <div className="thirdBlockOfBoardPosts">
                <RightSidebar title={data.title} visble={visible} />
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
