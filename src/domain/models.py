from pydantic import BaseModel


class User(BaseModel):
    email: str
    nombre: str
    rol: str


class NuevoUsuarioRequest(BaseModel):
    email: str
    rol: str = 'Sin Rol'


class UsuarioResponse(BaseModel):
    username: str
    email: str
    status: str
    enabled: bool


class ActualizarRolRequest(BaseModel):
    rol_antiguo: str
    rol_nuevo: str
