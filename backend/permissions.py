from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class CheckRole(permissions.BasePermission):
    """
    Разрешение, которое проверяет, имеет ли пользователь хотя бы одну из указанных ролей.
    Также проверяет, может ли пользователь изменять конкретный объект.
    """
    def __init__(self, *required_roles):
        self.required_roles = required_roles

    def has_permission(self, request, view):
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

    def has_object_permission(self, request, view, obj):
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

def check_role_permission(*required_roles):
    """
    Функция для создания экземпляра CheckRole с нужными ролями.
    """
    return lambda: CheckRole(*required_roles)
