from typing import Any

from fastapi import APIRouter, Depends

from src.application.delete_usuario import DeleteUsuarios
from src.application.get_usuario import GetUsuarios
from src.application.update_rol import UpdateUsuarios
from src.domain.models import User
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


@router.put("/{email}/rol")
def actualizar_rol(
    email: str,
    rol_antiguo: str,
    rol_nuevo: str,
    admin_user: User = Depends(require_roles(["admin"])),
    service: UpdateUsuarios = Depends(update_rol_service),
) -> None:
    return service.execute(email, rol_antiguo, rol_nuevo)


@router.delete("/{email}")
def eliminar_usuario(
    email: str,
    admin_user: User = Depends(require_roles(["admin"])),
    service: DeleteUsuarios = Depends(delete_usuarios_service),
) -> None:
    return service.execute(email)
