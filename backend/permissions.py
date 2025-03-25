# Rest Framework
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.views import View

# Standard library imports
from typing import Any


class CheckRole(permissions.BasePermission):
    """
    Разрешение, которое проверяет, имеет ли пользователь хотя бы одну из указанных ролей.
    """

    def __init__(
        self, *required_roles: str, allow_safe_methods_for_all: bool = False
    ) -> None:
        """
        Инициализация разрешения с ролями, которые требуются для доступа.
        """
        self.required_roles = required_roles
        self.allow_safe_methods_for_all = allow_safe_methods_for_all

    def has_permission(self, request: Request, view: View) -> bool:
        """
        Глобальная проверка:
        - Пользователь должен быть аутентифицирован.
        - Для небезопасных методов пользователь должен иметь одну из требуемых ролей.
        """
        if not request.user.is_authenticated:
            raise PermissionDenied("Вы не авторизованы. Пожалуйста, войдите в систему.")

        if (
            self.allow_safe_methods_for_all
            and request.method in permissions.SAFE_METHODS
        ):
            return True

        if request.user.role not in self.required_roles:
            raise PermissionDenied(
                "У вас недостаточно прав для выполнения этого действия."
            )

        return True

    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        """
        Объектная проверка:
        - По умолчанию разрешаем доступ к объекту, если пользователь имеет доступ на уровне представления.
        """
        return True


def check_role_permission(
    *required_roles: str, allow_safe_methods_for_all: bool = False
) -> Any:
    """
    Функция для создания экземпляра CheckRole с нужными ролями.
    """
    return lambda: CheckRole(
        *required_roles, allow_safe_methods_for_all=allow_safe_methods_for_all
    )
