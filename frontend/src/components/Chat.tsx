import { useRef, useState } from "react";
import { ApiLink, root } from "../config";
import Icon from "../Icons/Icon";

interface chatProps {
  sendLink: string;
  idPage: string;
}

interface chatMes {
  type: "bot" | "user";
  text: string;
}

const fake: chatMes[] = [
  // Приветствие
  {
    type: "bot",
    text: "Здравствуйте! Я могу рассказать всё о новых маркетинговых стратегиях компании. Спрашивайте!",
  },

  // Вопросы и ответы
  { type: "user", text: "Что за новая кампания?" },
  {
    type: "bot",
    text: "Новая кампания называется «Тренд 360». Основная цель — увеличение охвата в соцсетях и удержание клиентов через персонализированные предложения.",
  },

  { type: "user", text: "На каких платформах будем работать?" },
  {
    type: "bot",
    text: "Основной фокус на TikTok и Instagram Reels. Также тестируем AR-фильтры для продвижения.",
  },

  {
    type: "user",
    text: "А что насчёт аналитики? Как будем измерять эффективность?",
  },
  {
    type: "bot",
    text: "Добавляем A/B-тестирование и UTM-трекеры. Тестируем новый инструмент аналитики от Google для поведенческих метрик.",
  },

  { type: "user", text: "Какие цели по подписчикам?" },
  { type: "bot", text: "Цель — рост подписчиков на 20% к концу месяца." },

  { type: "user", text: "А CTR какой планируем?" },
  {
    type: "bot",
    text: "Планируемый CTR — не ниже 4%. Конверсия из рекламы — от 2%.",
  },

  { type: "user", text: "Когда запускаете новые фильтры?" },
  {
    type: "bot",
    text: "AR-фильтры запускаются на тестовой аудитории уже на следующей неделе.",
  },

  { type: "user", text: "Бюджет на рекламу будет расти?" },
  {
    type: "bot",
    text: "Расширение бюджета возможно, если улучшится качество лидов. Первые результаты через 2 недели.",
  },

  { type: "user", text: "Кто отвечает за аналитику?" },
  {
    type: "bot",
    text: "Ответственный — Екатерина. Она внедряет A/B-тестирование и новые инструменты аналитики.",
  },

  { type: "user", text: "Когда ждать первых результатов?" },
  {
    type: "bot",
    text: "Первые данные будут через две недели. Отчет нужно подготовить до 24 сентября.",
  },

  { type: "user", text: "Есть ли партнёрская программа?" },
  {
    type: "bot",
    text: "Да, её тоже планируем запустить в рамках кампании «Тренд 360».",
  },

  { type: "user", text: "Кто был на встрече?" },
  {
    type: "bot",
    text: "На встрече были: Дмитрий (СЕО), Анна и Иван (маркетологи), Сергей (продажи), Екатерина (product manager).",
  },

  { type: "user", text: "Что с бюджетом?" },
  {
    type: "bot",
    text: "Пока бюджет не меняется. Но при росте качества лидов возможны корректировки после отчёта.",
  },

  { type: "user", text: "Хорошо, спасибо!" },
  {
    type: "bot",
    text: "Всегда рад помочь! Следите за обновлениями и участвуйте в следующих встречах 😊",
  },
];

export default function Chat(props: chatProps) {
  const [session, setSession] = useState<chatMes[]>(fake);
  const [value, setValue] = useState<string>("");
  const chatContainerRef = useRef<HTMLDivElement>(null);
  async function sendRequest(link: string) {
    try {
      const response = await fetch(
        root + ApiLink + `/meetings/${props.idPage}/chat`
      );
      const resp_js = await response.json();
      const newText = resp_js.response;
      setSession((prev) => [...prev, { type: "user" as const, text: value }]);
      setSession((prev) => [...prev, { type: "bot" as const, text: newText }]);
      setTimeout(scrollToBottom, 0);
      setValue("");
    } catch (e) {
      console.log(e);
    }
  }
  const scrollToBottom = () => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop =
        chatContainerRef.current.scrollHeight;
    }
  };
  return (
    <div className="chat">
      <div className="contentSessionChat" ref={chatContainerRef}>
        {session.map((item: chatMes) => (
          <div className={"message-type-" + item.type}>{item.text}</div>
        ))}
      </div>
      <div className="inputMessageChat">
        <textarea
          placeholder="Чем я могу помочь вам сегодня?"
          value={value}
          onChange={(e) => {
            setValue(e.target.value);
          }}
        ></textarea>
        <button
          className="primaryButton"
          onClick={() => {
            sendRequest(props.sendLink);
          }}
        >
          <Icon type="send" color="#fff" />
        </button>
      </div>
    </div>
  );
}
