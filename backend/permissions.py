from rest_framework import permissions

class IsSupplier(permissions.BasePermission):
    """
    Разрешение, позволяющее доступ только поставщикам.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'supplier'

class IsCustomer(permissions.BasePermission):
    """
    Разрешение, позволяющее доступ только покупателям.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'customer'

class IsAdminUser(permissions.BasePermission):
    """
    Разрешение, позволяющее доступ только администраторам.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser