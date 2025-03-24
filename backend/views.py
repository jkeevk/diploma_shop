# Standard library imports
import os
from typing import Any, List

# Django
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import QuerySet
from django.views.generic import TemplateView
from django.conf import settings

# Rest Framework
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import GenericAPIView, ListCreateAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
# Local imports
from .filters import ProductFilter
from .models import Category, Contact, Order, Parameter, Product, Shop, User
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
    ShopSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)
from .swagger_configs import SWAGGER_CONFIGS
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
    permission_classes = [check_role_permission("customer", "admin")]

    def retrieve(self, request, *args, **kwargs):
        order = self.get_object()

        if order.status not in dict(Order.STATUS_CHOICES):
            raise ValidationError(f"Некорректный статус: {order.status}. Доступные статусы: {', '.join(dict(Order.STATUS_CHOICES).keys())}")

        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    def get_queryset(self) -> List[Order]:
        """
        Возвращает только заказы текущего пользователя.
        """
        return Order.objects.filter(user=self.request.user)


@SWAGGER_CONFIGS["category_viewset_schema"]
class CategoryViewSet(ModelViewSet):
    """
    Сет представлений для управления категориями.
    Поддерживает все CRUD операции.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = LimitOffsetPagination

    def get_permissions(self) -> List[Any]:
        """
        Настраивает права доступа в зависимости от действия.
        """
        if self.action in ["list", "retrieve"]:
            permission_classes = []
        elif self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [check_role_permission("admin")]
        return [permission() for permission in permission_classes]


@SWAGGER_CONFIGS["confirm_basket_schema"]
class ConfirmBasketView(APIView):
    """
    Представление для подтверждения корзины и создания заказа.
    """

    permission_classes = [check_role_permission("customer", "admin")]

    def post(self, request: Any) -> Response:
        """
        Подтверждает корзину, создает заказ и связывает его с контактом пользователя.
        """
        order = Order.objects.filter(user=request.user, status="new").first()

        if not order:
            return Response({"detail": "Корзина пуста."}, status=status.HTTP_400_BAD_REQUEST)

        contact_id = request.data.get("contact_id")
        if not contact_id:
            return Response({"detail": "ID контакта обязателен."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            contact = Contact.objects.get(id=contact_id, user=request.user)
        except Contact.DoesNotExist:
            return Response({"detail": "Контакт не найден."}, status=status.HTTP_400_BAD_REQUEST)

        order.status = "confirmed"
        order.contact = contact
        order.save()

        return Response({"detail": "Заказ успешно подтвержден."}, status=status.HTTP_200_OK)


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
    permission_classes = [check_role_permission("customer", "admin", "supplier")]
    
    def get_queryset(self) -> QuerySet[Contact]:
        """Возвращает только контакты текущего пользователя."""
        user = self.request.user
        if user.role == "admin":
            return Contact.objects.all()
        return Contact.objects.filter(user=user)

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
                "new_status": user.is_active
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


@SWAGGER_CONFIGS["order_viewset_schema"]
class OrderViewSet(ModelViewSet):
    """
    Сет представлений для управления заказами.
    Доступен только для администраторов и поставщиков.
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [check_role_permission("admin", "supplier")]


@SWAGGER_CONFIGS["parameter_viewset_schema"]
class ParameterViewSet(ModelViewSet):
    """
    Сет представлений для управления параметрами товаров.
    Поддерживает все CRUD операции.
    """

    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer
    permission_classes = [check_role_permission("admin", "supplier")]


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
        if request.user.is_anonymous:
            return Response(
                {"detail": "Пожалуйста, войдите в систему."}, status=status.HTTP_401_UNAUTHORIZED
            )

        shop = Shop.objects.filter(user=request.user).first()

        if not shop:
            return Response({"detail": "Вы не связаны с магазином."}, status=status.HTTP_400_BAD_REQUEST)

        orders = Order.objects.filter(order_items__shop=shop, status="confirmed").distinct()
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
            return Response(
                {"task_id": task.id}, 
                status=status.HTTP_202_ACCEPTED
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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

        if "file" not in request.FILES or not request.FILES["file"]:
            return Response({"error": "Файл не загружен"}, status=status.HTTP_400_BAD_REQUEST)

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
    Представление для подтверждения сброса пароля. Позволяет установить новый пароль.
    """

    serializer_class = PasswordResetConfirmSerializer

    def post(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        """
        Подтверждает сброс пароля и устанавливает новый пароль.
        """
        uid = force_str(urlsafe_base64_decode(kwargs["uidb64"]))
        token = kwargs["token"]

        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            return Response({"detail": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)

        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Недействительный токен."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response({"detail": "Пароль успешно изменён."}, status=status.HTTP_200_OK)


@SWAGGER_CONFIGS["password_reset_schema"]
class PasswordResetView(GenericAPIView):
    """
    Представление для сброса пароля. Отправляет ссылку для сброса на email пользователя.
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
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = ProductFilter
    search_fields = ["name", "model", "category__name"]
    permission_classes = [check_role_permission("supplier", "admin")]


@SWAGGER_CONFIGS["register_schema"]
class RegisterView(APIView):
    """
    Представление для регистрации нового пользователя.
    """

    serializer_class = UserRegistrationSerializer

    def post(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        """
        Регистрирует нового пользователя и отправляет подтверждение на email.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            if User.objects.filter(email=email).exists():
                return Response(
                    {
                        "Status": "error",
                        "Message": "Пользователь с таким email уже существует.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = serializer.save()
            return Response(
                {
                    "Status": "success",
                    "Message": "Пользователь успешно создан. Пожалуйста, проверьте вашу почту для подтверждения регистрации.",
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@SWAGGER_CONFIGS["shop_schema"]
class ShopView(ListCreateAPIView):
    """
    Представление для получения списка магазинов и создания нового магазина.
    Пользователи с ролью admin или supplier могут создавать магазины.
    """

    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [check_role_permission("admin", "supplier")]

    def perform_create(self, serializer: ShopSerializer) -> None:
        """
        При создании магазина автоматически связывает его с текущим пользователем.
        """
        serializer.save(user=self.request.user)


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
        if request.user.is_anonymous:
            return Response(
                {"detail": "Пожалуйста, войдите в систему."}, status=status.HTTP_401_UNAUTHORIZED
            )


        orders = Order.objects.filter(user=request.user, status="confirmed").distinct()
        order_serializer = OrderSerializer(orders, many=True)
        return Response(order_serializer.data)

class VKAuthView(TemplateView):
    template_name = 'vk_auth.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context.update({
            'VK_APP_ID': settings.VK_APP_ID,
            'VK_REDIRECT_URI': settings.VK_REDIRECT_URI
        })
        return context
