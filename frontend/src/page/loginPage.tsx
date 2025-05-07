import React from "react";
import { useNavigate } from "react-router-dom";
export default function Login() {
  const navigate = useNavigate();
  const [auth, setAuth] = React.useState("active-tabLogReg");
  const [reg, setReg] = React.useState("passive-tabLogReg");
  const root = "http://127.0.0.1:8000";
  const loginEndpoint = "/api/v1/auth/login";
  const registerEndpoint = "/api/v1/auth/register";
  const clickOnAuth = () => {
    setAuth("active-tabLogReg");
    setReg("passive-tabLogReg");
    const regForm = document.getElementById("regForm");
    const authForm = document.getElementById("authForm");
    const HeaderRegLogText = document.getElementById("HeaderRegLogText");
    if (regForm) {
      regForm.style.display = "none";
    }
    if (authForm) {
      authForm.style.display = "flex";
    }
    if (HeaderRegLogText) {
      HeaderRegLogText.textContent = "Вход в личный кабинет";
    }
  };
  const clickOnReg = () => {
    setReg("active-tabLogReg");
    setAuth("passive-tabLogReg");
    const regForm = document.getElementById("regForm");
    const authForm = document.getElementById("authForm");
    const HeaderRegLogText = document.getElementById("HeaderRegLogText");
    if (regForm) {
      regForm.style.display = "flex";
    }
    if (authForm) {
      authForm.style.display = "none";
    }
    if (HeaderRegLogText) {
      HeaderRegLogText.textContent = "Новый пользователь";
    }
  };
  async function handleSubmit(
    e: React.FormEvent<HTMLFormElement>,
    formType: string
  ) {
    e.preventDefault();
    const form = e.currentTarget;
    const formData = new FormData(form);
    let urlSend = root;
    if (formType === "login") {
      urlSend += loginEndpoint;
    } else if (formType === "register") {
      urlSend += registerEndpoint;
    }
    
    // Скрываем ошибки перед отправкой формы
    const errEl = document.getElementById("error-login-text-" + formType);
    if (errEl) {
      errEl.style.display = "none";
    }
    
    try {
      const response = await fetch(urlSend, {
        method: "POST",
        body: new URLSearchParams(formData as any).toString(), // преобразуем в x-www-form-urlencoded
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error("Ошибка сервера:", errorData);
        
        if (errEl) {
          // Показываем сообщение об ошибке из ответа сервера
          errEl.textContent = errorData.detail || "Произошла ошибка при авторизации";
          errEl.style.display = "flex";
        }
        return;
      }

      const data = await response.json(); // получаем JSON-ответ

      console.log("Успех:", data);

      // Сохраняем токен
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);

      // Перенаправляем
      navigate("/");
      window.location.reload();
    } catch (error) {
      console.error("Ошибка при входе:", error);
      if (errEl) {
        errEl.textContent = "Произошла ошибка при соединении с сервером";
        errEl.style.display = "flex";
      }
    }
    console.log(urlSend);
  }
  return (
    <div className="divContentView" id="loginPage">
      <div className="LoginPage">
        <div className="contentReg">
          <div className="RegLogMenu">
            <div className="blockRegLog">
              <div className="HeaderRegLog">
                <p className="HeaderRegLogText" id="HeaderRegLogText">
                  Вход в личный кабинет
                </p>
              </div>
              <div className="tabRegLog">
                <div className={auth} id="Authorise" onClick={clickOnAuth}>
                  <p>Авторизация</p>
                </div>
                <div className={reg} id="Registration" onClick={clickOnReg}>
                  <p>Регистрация</p>
                </div>
              </div>
              <div className="FormRegLog">
                <form
                  onSubmit={(e) => {
                    handleSubmit(e, "login");
                  }}
                  id="FormAuth"
                >
                  <div className="authForm" id="authForm">
                    <div className="input-container">
                      <input
                        className="inputForm"
                        type="email"
                        name="username"
                        id="login-ath"
                        required
                      />
                      <label htmlFor="username">Логин</label>
                    </div>
                    <div className="input-container">
                      <input
                        className="inputForm"
                        type="password"
                        name="password"
                        id="password-ath"
                        required
                      />
                      <label htmlFor="password">Пароль</label>
                    </div>
                    <p id="error-login-text-login" className="error-message">
                      Некорректный логин или пароль
                    </p>
                    <button className="sendFormButton" type="submit">
                      Войти
                    </button>
                  </div>
                </form>
                <form
                  onSubmit={(e) => {
                    handleSubmit(e, "register");
                  }}
                  id="FormReg"
                >
                  <div className="regForm" id="regForm">
                    <div className="input-container">
                      <input
                        className="inputForm"
                        type="text"
                        name="last_name"
                        id="last-name-reg"
                        required
                      />
                      <label htmlFor="last_name">Фамилия</label>
                    </div>
                    <div className="input-container">
                      <input
                        className="inputForm"
                        type="text"
                        name="first_name"
                        id="first-name-reg"
                        required
                      />
                      <label htmlFor="first_name">Имя</label>
                    </div>
                    <div className="input-container">
                      <input
                        className="inputForm"
                        type="text"
                        name="middle_name"
                        id="middle-name-reg"
                        required
                      />
                      <label htmlFor="middle_name">Отчество</label>
                    </div>
                    <div className="input-container">
                      <input
                        className="inputForm"
                        type="email"
                        name="email"
                        id="login-reg"
                        required
                      />
                      <label htmlFor="email">Логин</label>
                    </div>
                    <div className="input-container">
                      <input
                        className="inputForm"
                        id="password-reg"
                        type="password"
                        name="password"
                        required
                      />
                      <label htmlFor="password">Пароль</label>
                    </div>
                    <p id="error-login-text-register" className="error-message">
                      Некорректный логин или пароль
                    </p>
                    <button className="sendFormButton" type="submit">
                      Войти
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
