import React from "react";
export default function Login() {
  const [auth, setAuth] = React.useState("active-tabLogReg");
  const [reg, setReg] = React.useState("passive-tabLogReg");
  const root = "http://127.0.0.1:8000";
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
                <form action={root + "/api/v1/auth/login"} method="post">
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
                    <input
                      className="sendFormButton"
                      type="submit"
                      value="Войти"
                    />
                  </div>
                </form>
                <form action={root + "/api/v1/auth/register"} method="post">
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
                    <input
                      className="sendFormButton"
                      type="submit"
                      value="Войти"
                    />
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
