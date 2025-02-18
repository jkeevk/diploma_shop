from rest_framework import permissions

class IsAdminOrSupplier(permissions.BasePermission):
    """
    Разрешение, которое позволяет доступ только администраторам или пользователям с правами is_supplier.
    """

    def has_permission(self, request, view):
        # Разрешить доступ для всех пользователей на GET запросы
        if request.method == 'GET':
            return True
        
        # Запретить анонимным пользователям доступ к другим методам
        if request.user.is_anonymous:
            return False
        
        # Разрешить доступ для администраторов и поставщиков на другие методы
        return request.user.is_staff or getattr(request.user, 'is_supplier', False)