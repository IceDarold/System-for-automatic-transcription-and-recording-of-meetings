from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    department: str
    login: str
    password: str
    

class LoginFormModel(BaseModel):
    login: str
    password: str


class RegistrationFormModel(BaseModel):
    name: str
    department: str
    login: str
    password: str