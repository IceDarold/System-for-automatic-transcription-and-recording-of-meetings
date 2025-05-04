import React, { useEffect } from "react";
export default function Login() {
  const [auth, setAuth] = React.useState("active-tabLogReg");
  const [reg, setReg] = React.useState("passive-tabLogReg");
  const [step, setStep] = React.useState("first");
  const root = "http://127.0.0.1:8000";

  const [loginData, setLoginData] = React.useState({
    login: "",
    password: "",
  });

  // Состояние для формы "Регистрация"
  const [registrationData, setRegistrationData] = React.useState({
    name: "",
    region: "",
    login: "",
    password: "",
  });
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

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement>,
    form: "login" | "registration"
  ) => {
    const { name, value } = e.target;

    if (form === "login") {
      setLoginData((prev) => ({
        ...prev,
        [name]: value,
      }));
    } else {
      setRegistrationData((prev) => ({
        ...prev,
        [name]: value,
      }));
    }
  };

  const sendData = async (type: "login" | "registration") => {
    const url = root + (type === "login" ? "/sendLogin" : "/sendRegistration");
    console.log(url);
    const body = JSON.stringify(
      type === "login" ? loginData : registrationData
    );

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body,
      });

      const result = await response.json();

      if (response.ok) {
        console.log("Успех:", result);
      } else {
        console.error("Ошибка:", result);
      }
    } catch (error) {
      console.error("Ошибка сети:", error);
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
    <div className="divContentView">
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
                {/* <form action={root + "/sendLogin"} method="post"> */}
                <div className="authForm" id="authForm">
                  <div className="input-container">
                    <input
                      className="inputForm"
                      type="text"
                      name="login"
                      id="login-ath"
                      value={loginData.login}
                      onChange={(e) => handleChange(e, "login")}
                      required
                    />
                    <label htmlFor="login">Логин</label>
                  </div>
                  <div className="input-container">
                    <input
                      className="inputForm"
                      type="password"
                      name="password"
                      id="password-ath"
                      value={loginData.password}
                      onChange={(e) => handleChange(e, "login")}
                      required
                    />
                    <label htmlFor="password">Пароль</label>
                  </div>
                  <input
                    className="sendFormButton"
                    type="submit"
                    value="Войти"
                    onClick={() => {
                      sendData("login");
                    }}
                  />
                </div>
                {/* </form> */}
                {/* <form action={root + "/login/sendRegistration"} method="post"> */}
                <div className="regForm" id="regForm">
                  <div className="input-container">
                    <input
                      className="inputForm"
                      type="text"
                      name="name"
                      id="name-reg"
                      value={registrationData.name}
                      onChange={(e) => handleChange(e, "registration")}
                      required
                    />
                    <label htmlFor="name">ФИО</label>
                  </div>
                  <div className="input-container">
                    <input
                      className="inputForm"
                      type="text"
                      name="region"
                      id="region-reg"
                      value={registrationData.region}
                      onChange={(e) => handleChange(e, "registration")}
                      required
                    />
                    <label htmlFor="region">Департамент</label>
                  </div>
                  <div className="input-container">
                    <input
                      className="inputForm"
                      type="text"
                      name="login"
                      id="login-reg"
                      value={registrationData.login}
                      onChange={(e) => handleChange(e, "registration")}
                      required
                    />
                    <label htmlFor="login">Логин</label>
                  </div>
                  <div className="input-container">
                    <input
                      className="inputForm"
                      id="password-reg"
                      type="password"
                      name="password"
                      value={registrationData.password}
                      onChange={(e) => handleChange(e, "registration")}
                      required
                    />
                    <label htmlFor="password">Пароль</label>
                  </div>
                  <input
                    className="sendFormButton"
                    type="submit"
                    value="Войти"
                    onClick={() => {
                      sendData("registration");
                    }}
                  />
                </div>
                {/* </form> */}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
