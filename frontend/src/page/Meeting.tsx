import { useParams } from "react-router-dom";
import { root } from "../config";
import Page from "./page";
import { ApiLink } from "../config";
import Chat from "../components/Chat";
import AudioPlayer from "../components/AudioPlayer";
import { useEffect, useState } from "react";
import Badge from "../components/Badge";
interface DataFormat {
  title: string;
  tags: string[];
  description: string;
}

function formattedData(data: any) {
  const dataF: DataFormat = {
    title: data.title,
    tags: data.tags,
    description: data.description,
  };
  return dataF;
}

const fakeTxt = `SPEAKER_1 00.00.00: Добрый день, коллеги! Начинаем встречу по проекту «Альфа». Присутствуют все?
SPEAKER_2 00.00.06: Да, я здесь.
SPEAKER_3 00.00.08: Здесь.
SPEAKER_4 00.00.10: Подключаюсь.
SPEAKER_5 00.00.12: Я тоже на месте.
SPEAKER_1 00.00.15: Отлично. Первое — статус по разработке.
SPEAKER_2 00.00.19: Бэкенд почти готов. API почти протестирован.
SPEAKER_5 00.00.23: А фронтенд? Там всё так же зависло?
SPEAKER_3 00.00.27: Не совсем. Мы переделали главную страницу, но есть проблемы с адаптивом.
SPEAKER_1 00.00.32: Хорошо. Какие блокеры?
SPEAKER_3 00.00.35: Ожидаем дизайн от UX-отдела.
SPEAKER_4 00.00.38: Мы выложили макеты сегодня утром. Проверьте Slack.
SPEAKER_3 00.00.42: Увидели, спасибо. Будем дорабатывать.
SPEAKER_1 00.00.46: Хорошо. Сергей, ты по тестированию?
SPEAKER_5 00.00.49: QA начнётся завтра. Подготовили чек-листы.
SPEAKER_2 00.00.53: А окружение уже готово?
SPEAKER_5 00.00.56: Вроде да, но пока не запускали полный сценарий.
SPEAKER_1 00.01.00: Ладно. Анна, как маркетинг?
SPEAKER_4 00.01.03: Кампания запущена, но охват меньше прогноза.
SPEAKER_1 00.01.07: Что с бюджетом?
SPEAKER_4 00.01.10: В пределах лимита. Но можно добавить немного на таргет.
SPEAKER_1 00.01.14: Одобрю. Теперь финансы.
SPEAKER_5 00.01.17: Сергей, доложи.
SPEAKER_6 00.01.20: Расходы в норме. Никаких перерасходов нет.
SPEAKER_1 00.01.24: Значит, продолжаем в том же темпе.
SPEAKER_2 00.01.27: А что насчёт дедлайна? Его сдвигают?
SPEAKER_1 00.01.30: На данный момент держим планку — 25 число.
SPEAKER_3 00.01.34: Нужно ли продлить время на тестирование?
SPEAKER_5 00.01.37: Возможно. Если найдём баги, то да.
SPEAKER_1 00.01.41: Решение примем после QA-отчёта.
SPEAKER_4 00.01.44: И ещё: клиент просил добавить функцию экспорта.
SPEAKER_2 00.01.49: Экспорт чего именно?
SPEAKER_4 00.01.52: Отчётов в Excel и PDF.
SPEAKER_2 00.01.55: Это входит в текущую фичу?
SPEAKER_4 00.01.58: Нет, но они считают, что должно быть.
SPEAKER_1 00.02.02: Нужно обсудить с product owner'ом.
SPEAKER_3 00.02.06: Могу подготовить ТЗ для этой задачи.
SPEAKER_1 00.02.09: Хорошо. Вынесем в отдельную тему.
SPEAKER_5 00.02.12: А по нагрузке у команды хватает ресурсов?
SPEAKER_2 00.02.16: В целом да, но дизайнеров не хватает.
SPEAKER_4 00.02.19: Сейчас освободится один, он закончил задачу.
SPEAKER_1 00.02.23: Хорошо. Ещё вопросы по текущему этапу?
SPEAKER_3 00.02.26: Нет.
SPEAKER_4 00.02.28: У меня нет.
SPEAKER_5 00.02.30: И у меня.
SPEAKER_1 00.02.33: Тогда переходим к следующей части — интеграция с внешними системами.
SPEAKER_2 00.02.37: Мы договорились с платформой PayPro. API получили.
SPEAKER_5 00.02.41: Есть документация?
SPEAKER_2 00.02.43: Да, она в общем доступе. Но часть методов не покрыта примерами.
SPEAKER_3 00.02.47: Может, стоит запросить техподдержку?
SPEAKER_2 00.02.50: Уже написали. Ждём ответа.
SPEAKER_1 00.02.54: Хорошо. Когда планируется подключение?
SPEAKER_2 00.02.57: Через неделю. После внутреннего тестирования.
SPEAKER_1 00.03.01: Принято. Что ещё?
SPEAKER_4 00.03.04: Хотела спросить про презентацию для инвесторов.
SPEAKER_1 00.03.07: Она почти готова. Нужно только обновить метрики.
SPEAKER_4 00.03.10: Хорошо, я внесу правки.
SPEAKER_1 00.03.13: Отправь версию до пятницы.
SPEAKER_4 00.03.15: Сделаю.
SPEAKER_5 00.03.18: А будет ли демо-версия приложения?
SPEAKER_2 00.03.21: Да, её можно будет показать через две недели.
SPEAKER_5 00.03.24: Хорошо. Нужно зафиксировать это в презентации.
SPEAKER_1 00.03.28: Добавим слайд. Что ещё?
SPEAKER_3 00.03.31: Нужно ли провести ещё одно демо внутри команды?
SPEAKER_1 00.03.34: Да, давайте сделаем в четверг.
SPEAKER_3 00.03.37: Запланирую встречу.
SPEAKER_1 00.03.40: Отлично. Еще комментарии?
SPEAKER_4 00.03.43: Нет.
SPEAKER_5 00.03.45: У меня тоже нет.
SPEAKER_1 00.03.48: Тогда заканчиваем. Спасибо всем!
SPEAKER_2 00.03.51: До связи!
SPEAKER_3 00.03.53: Увидимся!
SPEAKER_4 00.03.55: Хорошего дня!
SPEAKER_5 00.03.57: И вам тоже!`;

export default function Meeting() {
  const { id } = useParams();
  const [audio, setAudio] = useState("");
  const [activePanel, setActivePanel] = useState("chat");
  const [data, setData] = useState<DataFormat>();
  async function fetchAudio() {
    try {
      const response = await fetch(root + ApiLink + `/meetings/${id}/audio`);
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      setAudio(url);
    } catch (e) {
      console.log(e);
    }
  }
  async function fetchData() {
    try {
      const response = await fetch(root + ApiLink + `/meetings/${id}`);
      const data_resp = await response.json();
      setData(formattedData(data_resp));
      console.log(data_resp);
    } catch (e) {
      console.log(e);
    }
  }
  useEffect(() => {
    fetchAudio();
    fetchData();
  }, []);
  const linkMesWithChat = `/meetings/${id}/chat`;
  return (
    <Page>
      <div className="Content">
        <div className="sidesOnMeetings">
          <div className="leftSideOnMeetings">
            <p className="h1-of-list">{data ? data.title : "Без названия"}</p>
            <div className="audio">
              <AudioPlayer src={audio} />
            </div>
            <div className="BagdesArea">
              {data ? (
                data.tags.map((item: string) => (
                  <Badge color="gray" text={item} />
                ))
              ) : (
                <></>
              )}
            </div>
            <p className="description-card">{data ? data.description : ""}</p>
          </div>
          <div className="rightSideOnMeetings">
            <div className="panel-tabs">
              <div
                className="panelSelect"
                data-panel-selected={activePanel === "chat" ? "true" : "false"}
                onClick={() => {
                  setActivePanel("chat");
                }}
              >
                <p>AI Chat</p>
              </div>
              <div
                className="panelSelect"
                data-panel-selected={
                  activePanel === "diarization" ? "true" : "false"
                }
                onClick={() => {
                  setActivePanel("diarization");
                }}
              >
                <p>Транскрибация</p>
              </div>
            </div>
            <div className="contentInPanelView">
              <div
                style={{ display: activePanel === "chat" ? "flex" : "none" }}
              >
                <Chat sendLink={linkMesWithChat} idPage={id ?? "404"} />
              </div>
              <div
                style={{
                  display: activePanel === "diarization" ? "flex" : "none",
                }}
              >
                <div className="contentTranscription">
                  {fakeTxt
                    .trim()
                    .split("\n")
                    .map((line, index) => (
                      <div key={index}>{line}</div>
                    ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Page>
  );
}
