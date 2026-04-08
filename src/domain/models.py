from pydantic import BaseModel

class User(BaseModel):
    email: str
    nombre: str
    rol: str

class NuevoUsuarioRequest(BaseModel):
    email: str
    rol: str
    password_temporal: str = "Temporal123!"

class UsuarioResponse(BaseModel):
    username: str
    email: str
    status: str
    enabled: bool