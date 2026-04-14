from pydantic import BaseModel


class User(BaseModel):
    email: str
    nombre: str
    roles: list[str]
