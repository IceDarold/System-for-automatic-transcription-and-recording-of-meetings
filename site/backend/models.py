from pydantic import BaseModel


class LoginFormModel(BaseModel):
    login: str
    password: str


class RegistrationFormModel(BaseModel):
    name: str
    region: str
    login: str
    password: str
    repeat_password: str