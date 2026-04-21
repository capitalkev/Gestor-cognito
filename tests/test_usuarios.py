from unittest.mock import MagicMock

from capitalexpress_auth import User
from fastapi.testclient import TestClient

from src.interface.dependencias.usuarios import (
    delete_usuarios_service,
    get_usuarios_service,
    require_roles,
    update_rol_service,
)
from src.main import app

client = TestClient(
    app,
    headers={
        "X-API-KEY": "default_api_key",
        "Authorization": "Bearer test-token",
    },
)


# Mock de dependencias
def override_require_roles(roles: list[str]):
    def _override() -> User:
        return User(username="testuser", groups=roles)

    return _override


def mock_get_usuarios_service() -> MagicMock:
    mock = MagicMock()
    mock.execute.return_value = [{"username": "test1", "email": "test1@example.com"}]
    return mock


def mock_update_rol_service() -> MagicMock:
    mock = MagicMock()
    mock.asignar.return_value = None
    mock.remover.return_value = None
    return mock


def mock_delete_usuarios_service() -> MagicMock:
    mock = MagicMock()
    mock.execute.return_value = None
    return mock


# Aplicar mocks
app.dependency_overrides[require_roles] = override_require_roles
app.dependency_overrides[get_usuarios_service] = mock_get_usuarios_service
app.dependency_overrides[update_rol_service] = mock_update_rol_service
app.dependency_overrides[delete_usuarios_service] = mock_delete_usuarios_service


def test_listar_empleados() -> None:
    response = client.get("/api/admin/usuarios/")
    assert response.status_code == 200
    assert response.json() == [{"username": "test1", "email": "test1@example.com"}]


def test_agregar_rol() -> None:
    response = client.post("/api/admin/usuarios/testuser/roles/new_role")
    assert response.status_code == 200
    assert response.json() is None


def test_quitar_rol() -> None:
    response = client.delete("/api/admin/usuarios/testuser/roles/old_role")
    assert response.status_code == 200
    assert response.json() is None


def test_eliminar_usuario() -> None:
    response = client.delete("/api/admin/usuarios/test@example.com")
    assert response.status_code == 200
    assert response.json() is None
