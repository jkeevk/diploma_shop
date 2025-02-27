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
    Также проверяет, может ли пользователь изменять конкретный объект.
    """
    def __init__(self, *required_roles: str) -> None:
        """
        Инициализация разрешения с ролями, которые требуются для доступа.
        """
        self.required_roles = required_roles

    def has_permission(self, request: Request, view: View) -> bool:
        """
        Глобальная проверка:
        - Пользователь должен быть аутентифицирован.
        - Пользователь должен иметь одну из требуемых ролей.
        """
        if not request.user.is_authenticated:
            raise PermissionDenied("Вы не авторизованы. Пожалуйста, войдите в систему.")

        if request.user.role not in self.required_roles:
            raise PermissionDenied("У вас недостаточно прав для выполнения этого действия.")

        return True

    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        """
        Объектная проверка:
        - Пользователь может изменять только свои заказы, если он не админ.
        - Только админ может изменять роль пользователя.
        """
        if request.user.role == 'admin':
            return True

        if obj.user == request.user:
            return True

        if 'role' in request.data and request.data['role'] != obj.role:
            raise PermissionDenied("Только администратор может изменять роль пользователя.")

        return False

    def check_user_active(self, user: Any) -> None:
        """
        Проверяет, активен ли пользователь.
        """
        if not user.is_active:
            raise PermissionDenied("Пользователь неактивен и не может быть изменен.")

def check_role_permission(*required_roles: str) -> Any:
    """
    Функция для создания экземпляра CheckRole с нужными ролями.
    """
    return lambda: CheckRole(*required_roles)
