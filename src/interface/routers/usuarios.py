from typing import Any

from capitalexpress_auth import User
from fastapi import APIRouter, Depends

from src.application.delete_usuario import DeleteUsuarios
from src.application.get_usuario import GetUsuarios
from src.application.update_rol import UpdateUsuarios
from src.interface.dependencias.usuarios import (
    delete_usuarios_service,
    get_usuarios_service,
    require_roles,
    update_rol_service,
)

router = APIRouter(prefix="/api/admin/usuarios", tags=["Gestión de Usuarios IAM"])


@router.get("/")
def listar_empleados(
    current_user: User = Depends(require_roles(["admin"])),
    service: GetUsuarios = Depends(get_usuarios_service),
) -> list[dict[str, Any]]:
    return service.execute()


@router.post("/{username}/roles/{rol}")
def agregar_rol(
    username: str,
    rol: str,
    admin_user: User = Depends(require_roles(["admin"])),
    service: UpdateUsuarios = Depends(update_rol_service),
) -> None:
    return service.asignar(username, rol)


@router.delete("/{username}/roles/{rol}")
def quitar_rol(
    username: str,
    rol: str,
    admin_user: User = Depends(require_roles(["admin"])),
    service: UpdateUsuarios = Depends(update_rol_service),
) -> None:
    return service.remover(username, rol)


@router.delete("/{email}")
def eliminar_usuario(
    email: str,
    admin_user: User = Depends(require_roles(["admin"])),
    service: DeleteUsuarios = Depends(delete_usuarios_service),
) -> None:
    return service.execute(email)
