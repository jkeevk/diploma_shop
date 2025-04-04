# Standard library imports
import os
from typing import Any, List

# Django
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import QuerySet
from django.http import Http404

# Rest Framework
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import GenericAPIView, ListCreateAPIView, UpdateAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action

# Local imports
from .filters import BasketFilter, CategoryFilter, ContactFilter, ProductFilter
from .models import (
    Category,
    Contact,
    Order,
    Parameter,
    Product,
    Shop,
    User,
    ProductInfo,
)
from .permissions import check_role_permission
from .serializers import (
    CategorySerializer,
    ContactSerializer,
    FileUploadSerializer,
    LoginSerializer,
    OrderSerializer,
    ParameterSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    ProductSerializer,
    ProductInfoSerializer,
    ShopSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    OrderWithContactSerializer,
)
from backend.swagger.config import SWAGGER_CONFIGS
from .tasks import export_products_task, import_products_task
from celery.result import AsyncResult


@SWAGGER_CONFIGS["basket_viewset_schema"]
class BasketViewSet(ModelViewSet):
    """
    Сет представлений для управления корзиной пользователя.
    Позволяет просматривать, создавать и изменять заказы со статусом "new".
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [check_role_permission("customer", "admin", "supplier")]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = BasketFilter
    search_fields = ["status"]

    def retrieve(self, request, *args, **kwargs):
        order = self.get_object()

        if order.status not in dict(Order.STATUS_CHOICES):
            raise ValidationError(
                f"Некорректный статус: {order.status}. Доступные статусы: {', '.join(dict(Order.STATUS_CHOICES).keys())}"
            )

        serializer = self.get_serializer(order)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        new_status = request.data.get("status")
        if new_status:
            if request.user.role == "customer" and new_status not in [
                "new",
                "canceled",
            ]:
                raise ValidationError(
                    "Недостаточно прав. Вы можете устанавливать только: new, canceled"
                )
            if new_status not in dict(Order.STATUS_CHOICES):
                raise ValidationError(
                    f"Некорректный статус: {new_status}. "
                    f"Доступные статусы: {', '.join(dict(Order.STATUS_CHOICES).keys())}"
                )

        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def get_queryset(self) -> List[Order]:
        if self.request.user.role in ["admin", "supplier"]:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound(detail="Корзина не найдена.", code="not_found")


@SWAGGER_CONFIGS["category_viewset_schema"]
class CategoryViewSet(ModelViewSet):
    """
    Сет представлений для управления категориями.
    Поддерживает все CRUD операции.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CategoryFilter
    search_fields = ["name"]

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound(detail="Категория не найдена")

    def get_permissions(self) -> List[Any]:
        """
        Настраивает права доступа в зависимости от действия.
        """
        permission_classes = []
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [check_role_permission("admin")]
        return [permission() for permission in permission_classes]


@SWAGGER_CONFIGS["confirm_basket_schema"]
class ConfirmBasketView(APIView):
    """
    Представление для подтверждения корзины и создания заказа.
    """

    permission_classes = [check_role_permission("customer", "admin")]

    def post(self, request: Any, contact_id: int) -> Response:
        """
        Подтверждает корзину, создает заказ и связывает его с контактом пользователя.
        """
        serializer = OrderWithContactSerializer(
            data={"contact_id": contact_id}, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Заказ успешно подтвержден."}, status=status.HTTP_200_OK
        )


@SWAGGER_CONFIGS["confirm_registration_schema"]
class ConfirmRegistrationView(APIView):
    """
    Представление для подтверждения регистрации пользователя по токену.
    """

    def get(self, request: Any, token: str, *args: Any, **kwargs: Any) -> Response:
        """
        Подтверждает регистрацию пользователя по токену.
        """
        user = get_object_or_404(User, confirmation_token=token)

        user.is_active = True
        user.confirmation_token = None
        user.save()

        return Response(
            {
                "Status": "success",
                "Message": "Ваш аккаунт успешно активирован.",
            },
            status=status.HTTP_200_OK,
        )


@SWAGGER_CONFIGS["contact_viewset_schema"]
class ContactViewSet(ModelViewSet):
    """
    Сет представлений для управления контактами пользователя.
    Поддерживает все CRUD операции.
    """

    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ContactFilter
    permission_classes = [check_role_permission("customer", "admin", "supplier")]

    def get_queryset(self) -> QuerySet[Contact]:
        """Возвращает только контакты текущего пользователя."""
        user = self.request.user
        if user.role == "admin":
            return Contact.objects.all()
        return Contact.objects.filter(user=user)

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound(detail="Контакт не найден")


@SWAGGER_CONFIGS["disable_toggle_user_activity_schema"]
class ToggleUserActivityView(APIView):
    """
    Представление для включения/отключения активности любого пользователя.
    Доступно только администраторам.
    """

    permission_classes = [check_role_permission("admin")]

    def post(self, request: Any, user_id: int) -> Response:
        """
        Переключает статус активности пользователя по его ID.
        """
        user = get_object_or_404(User, id=user_id)

        if user == request.user:
            return Response(
                {"error": "Вы не можете изменить активность своего аккаунта."},
                status=status.HTTP_403_FORBIDDEN,
            )

        user.is_active = not user.is_active
        user.save()

        return Response(
            {
                "message": f"Активность пользователя {user.email} (ID={user.id}) изменена на {user.is_active}",
                "user_id": user.id,
                "new_status": user.is_active,
            },
            status=status.HTTP_200_OK,
        )


@SWAGGER_CONFIGS["login_schema"]
class LoginView(APIView):
    """
    Представление для аутентификации пользователя и получения JWT-токенов.
    При успешной аутентификации возвращает access и refresh токены.
    """

    def post(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        """
        Аутентифицирует пользователя и возвращает JWT-токены.
        """
        serializer = LoginSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            user = serializer.validated_data["user"]

            user.last_login = timezone.now()
            user.save(update_fields=["last_login"])

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response(
                {
                    "user_id": user.id,
                    "email": user.email,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@SWAGGER_CONFIGS["parameter_viewset_schema"]
class ParameterViewSet(ModelViewSet):
    """
    Сет представлений для управления параметрами товаров.
    Поддерживает все CRUD операции.
    """

    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer
    permission_classes = [check_role_permission("admin", "supplier")]

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound(detail="Параметр не найден")


@SWAGGER_CONFIGS["partner_orders_schema"]
class PartnerOrders(APIView):
    """
    Представление для получения заказов, связанных с магазином поставщика.
    """

    permission_classes = [check_role_permission("supplier", "admin")]

    def get(self, request: Any) -> Response:
        """
        Возвращает список заказов, связанных с магазином поставщика.
        """

        shop = Shop.objects.filter(user=request.user).first()

        if not shop:
            return Response(
                {"detail": "Вы не связаны с магазином."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        orders = Order.objects.filter(
            order_items__shop=shop, status="confirmed"
        ).distinct()
        order_serializer = OrderSerializer(orders, many=True)
        return Response(order_serializer.data)


@SWAGGER_CONFIGS["partner_import_schema"]
class PartnerImportView(APIView):
    """
    Представление для создания задачи на импорт данных поставщика.
    """

    permission_classes = [check_role_permission("admin", "supplier")]

    def get(self, request) -> Response:
        try:
            task = import_products_task.delay()
            return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@SWAGGER_CONFIGS["check_partner_import_schema"]
class PartnerImportStatusView(APIView):
    """
    Представление для получения результата выполнения задачи на импорт данных поставщика.
    """

    permission_classes = [check_role_permission("admin", "supplier")]

    def get(self, request, task_id) -> Response:
        task_result = AsyncResult(task_id)
        response_data = {"status": task_result.status}

        if task_result.ready():
            if task_result.successful():
                result = task_result.result
                if result["status"] == "success":
                    response_data["data"] = result["data"]
                else:
                    response_data["error"] = result.get("message", "Unknown error")
            else:
                response_data["error"] = "Task failed"

        return Response(response_data, status=status.HTTP_200_OK)


@SWAGGER_CONFIGS["partner_update_schema"]
class PartnerUpdateView(APIView):
    """
    Представление для обновления данных поставщика через загрузку файла.
    """

    serializer_class = FileUploadSerializer
    permission_classes = [check_role_permission("admin", "supplier")]

    def post(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        """
        Загружает файл с данными и обновляет информацию о товарах.
        """
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = request.FILES.get("file")
        file_path = os.path.join("data", uploaded_file.name)

        try:
            with open(file_path, "wb") as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            if not uploaded_file.name.endswith(".json"):
                return Response(
                    {"error": "Неверный формат файла. Ожидается JSON."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            export_products_task.delay(file_path)

            return Response(
                {"message": "Задача на загрузку данных поставлена в очередь"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"Ошибка при загрузке файла: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@SWAGGER_CONFIGS["password_reset_confirm_schema"]
class PasswordResetConfirmView(GenericAPIView):
    """
    Представление для изменения пароля после сброса.
    Сохраняет новый пароль при валидном токене.
    """

    serializer_class = PasswordResetConfirmSerializer

    def post(self, request: Request, uidb64: str, token: str) -> Response:
        serializer = self.get_serializer(
            data=request.data, context={"uidb64": uidb64, "token": token}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Пароль успешно изменён."}, status=status.HTTP_200_OK
        )


@SWAGGER_CONFIGS["password_reset_schema"]
class PasswordResetView(GenericAPIView):
    """
    Представление для сброса пароля.
    Отправляет ссылку для сброса на email пользователя.
    """

    serializer_class = PasswordResetSerializer

    def post(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        """
        Обрабатывает запрос на сброс пароля и отправляет ссылку на email.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Ссылка для сброса пароля отправлена на email."},
            status=status.HTTP_200_OK,
        )


@SWAGGER_CONFIGS["product_viewset_schema"]
class ProductViewSet(ModelViewSet):
    """
    Сет представлений для управления товарами. Поддерживает фильтрацию и поиск.
    Доступ:
    - list/retrieve: все пользователи
    - create/update/delete: только поставщики и администраторы
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = ProductFilter
    search_fields = ["name", "model", "category__name"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_permissions(self) -> list:
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]

        return [check_role_permission("supplier", "admin")()]

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound(detail="Товар не найден.", code="not_found")


@SWAGGER_CONFIGS["register_schema"]
class RegisterView(APIView):
    """Представление для регистрации нового пользователя."""

    serializer_class = UserRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"status": "error", "errors": self._clean_errors(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()
        return Response(
            {
                "status": "success",
                "message": "Регистрация успешна. Проверьте email для активации",
            },
            status=status.HTTP_201_CREATED,
        )

    def _clean_errors(self, errors):
        """Очистка и форматирование ошибок"""
        clean_errors = {}
        for field, messages in errors.items():
            unique_messages = list(
                dict.fromkeys([msg for msg in messages if not isinstance(msg, dict)])
            )
            clean_errors[field] = unique_messages

        return clean_errors


@SWAGGER_CONFIGS["shop_schema"]
class ShopView(ListCreateAPIView):
    """
    Представление для получения списка магазинов и создания нового магазина.
    Любой пользователь может просматривать магазины. Создавать могут только администраторы и продавцы.
    """

    queryset = Shop.objects.all()
    serializer_class = ShopSerializer

    def get_permissions(self) -> list:
        if self.request.method == "GET":
            return [AllowAny()]
        return [check_role_permission("supplier", "admin")()]


@SWAGGER_CONFIGS["user_viewset_schema"]
class UserViewSet(ModelViewSet):
    """
    Сет представлений для управления данными пользователя.
    Поддерживает все CRUD операции.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [check_role_permission("admin", "supplier")]
    http_method_names = ["get", "put", "patch", "delete"]


@SWAGGER_CONFIGS["user_orders_schema"]
class UserOrdersView(APIView):
    """
    Представление для получения заказов для покупателя поступивших в обработку.
    """

    permission_classes = [check_role_permission("customer", "admin")]

    def get(self, request: Any) -> Response:
        """
        Возвращает список заказов со статусом "confirmed".
        """

        orders = Order.objects.filter(user=request.user, status="confirmed").distinct()
        order_serializer = OrderSerializer(orders, many=True)
        return Response(order_serializer.data)


@SWAGGER_CONFIGS["product_upload_image"]
class ProductImageView(UpdateAPIView):
    queryset = ProductInfo.objects.all()
    serializer_class = ProductInfoSerializer
    http_method_names = ["patch"]
    permission_classes = [check_role_permission("admin")]

    def perform_update(self, serializer):
        instance = serializer.save()
        if "image" in self.request.FILES:
            instance.image_thumbnail = None
            instance.save()


@SWAGGER_CONFIGS["user_upload_image"]
class UserAvatarUpdateView(UpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [check_role_permission("customer", "supplier", "admin")]
    http_method_names = ["patch"]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        instance = self.get_object()
        file = self.request.FILES.get("avatar")

        if file:
            if instance.avatar:
                instance.avatar.delete()

            instance.avatar = file
            instance.save()
