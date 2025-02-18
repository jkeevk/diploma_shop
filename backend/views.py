import os
from django.core.management import call_command
from django.shortcuts import get_object_or_404, render
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiExample,
    OpenApiResponse,
)
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView, GenericAPIView

from .models import Category, Contact, Order, OrderItem, Product, Shop, User
from .serializers import (
    CategorySerializer,
    ContactSerializer,
    FileUploadSerializer,
    OrderItemSerializer,
    OrderSerializer,
    ProductSerializer,
    ShopSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    PasswordResetSerializer,
)

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .filters import ProductFilter


def index(request):
    urls = [
        {"url": "/admin/", "description": "Админ-панель"},
        {"url": "/accounts/login/", "description": "Вход в систему"},
        {"url": "user/register/", "description": "Регистрация нового пользователя"},
        {"url": "password_reset/", "description": "Сброс пароля"},
        {"url": "products", "description": "Список товаров"},
        {"url": "orders", "description": "Список заказов"},
        {"url": "users", "description": "Пользователи"},
        {"url": "partner/update/", "description": "Обновление партнера"},
        {"url": "categories/", "description": "Список категорий"},
        {"url": "shops/", "description": "Список магазинов"},
    ]
    return render(request, "index.html", {"urls": urls})


# Эндпоинт для получения токена
@extend_schema(
    summary="Получить токен JWT",
    description="Используйте этот эндпоинт для получения JWT токена, отправив логин и пароль.",
    responses={
        200: OpenApiResponse(
            description="Успех",
            examples=[
                OpenApiExample(
                    "Пример ответа",
                    value={"access": "token_value", "refresh": "refresh_token_value"},
                ),
            ],
        ),
    },
)
class CustomTokenObtainPairView(TokenObtainPairView):
    pass


# Эндпоинт для обновления токена
@extend_schema(
    summary="Обновить токен JWT",
    description="Используйте этот эндпоинт для обновления JWT токена, отправив refresh токен.",
    responses={
        200: OpenApiResponse(
            description="Успех",
            examples=[
                OpenApiExample("Пример ответа", value={"access": "new_token_value"}),
            ],
        ),
    },
)
class CustomTokenRefreshView(TokenRefreshView):
    pass


@extend_schema(
    summary="Сброс пароля", description="Эндпоинт для получения ссылки на сброс пароля."
)
class PasswordResetView(GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Ссылка для сброса пароля отправлена на email."},
            status=status.HTTP_200_OK,
        )


@extend_schema(
    summary="Обновление каталога поставщика",
    description="Эндпоинт для обновления каталога поставщика. Требует multipart/form-data в теле запроса. Файл должен быть в формате JSON.",
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "format": "binary",
                }
            },
        }
    },
    responses={
        200: {"description": "Данные успешно загружены"},
        400: {"description": "Неверный запрос (неверный файл или файл не загружен)"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
class PartnerUpdateView(APIView):
    serializer_class = FileUploadSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not request.user.is_supplier and not request.user.is_staff:
            return Response(
                {"error": "У вас нет прав на загрузку данных"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if "file" not in request.FILES:
            return Response(
                {"error": "Файл не загружен"}, status=status.HTTP_400_BAD_REQUEST
            )

        uploaded_file = request.FILES["file"]
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

            call_command("load_products", file_path)
            return Response(
                {"message": "Данные успешно загружены"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    list=extend_schema(
        description="Получить список продуктов.",
        summary="Список продуктов",
        responses={200: ProductSerializer(many=True)},
    ),
    create=extend_schema(
        description="Создать новый продукт.",
        summary="Создание продукта",
        request=ProductSerializer,
        responses={201: ProductSerializer},
    ),
    retrieve=extend_schema(
        description="Получить продукт по ID.",
        summary="Получение продукта",
        responses={200: ProductSerializer},
    ),
    update=extend_schema(
        description="Обновить продукт по ID.",
        summary="Обновление продукта",
        request=ProductSerializer,
        responses={200: ProductSerializer},
    ),
    partial_update=extend_schema(
        description="Частичное обновление продукта по ID.",
        summary="Частичное обновление продукта",
        request=ProductSerializer,
        responses={200: ProductSerializer},
    ),
    destroy=extend_schema(
        description="Удалить продукт по ID.",
        summary="Удаление продукта",
        responses={200: None},
    ),
)
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = ProductFilter
    search_fields = ["name", "model", "category__name"]

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            product_id = instance.id
            self.perform_destroy(instance)
            return Response(
                {
                    "id": product_id,
                    "status": "success",
                    "message": f"Товар с ID {product_id} успешно удален.",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        user_pk = self.kwargs.get("user_pk")
        if user_pk:
            return Product.objects.filter(user_id=user_pk)
        return Product.objects.all()

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
@extend_schema(
    summary="Регистрация аккаунта",
    description="Регистрация аккаунта с помощью электронной почты и пароля.",
)
class RegisterView(APIView):
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
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


@extend_schema(
    summary="Активация аккаунта",
    description="Активация аккаунта покупателя или поставщика с помощью токена.",
)
class ConfirmRegistrationView(APIView):
    serializer_class = None

    def get(self, request, token, *args, **kwargs):
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


@extend_schema(
    summary="Список всех категорий",
    description="Возвращает список всех категорий.",
)
class CategoryView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


@extend_schema(
    summary="Список всех магазинов",
    description="Возвращает список всех магазинов.",
)
class ShopView(ListAPIView):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer


@extend_schema_view(
    list=extend_schema(
        description="Получить список контактов.",
        summary="Список контактов",
        responses={200: ContactSerializer(many=True)},
    ),
    create=extend_schema(
        description="Создать новый контакт.",
        summary="Создание контакта",
        request=ContactSerializer,
        responses={201: ContactSerializer},
    ),
    retrieve=extend_schema(
        description="Получить контакт по ID.",
        summary="Получение контакта",
        responses={200: ContactSerializer},
    ),
    update=extend_schema(
        description="Обновить контакт по ID.",
        summary="Обновление контакта",
        request=ContactSerializer,
        responses={200: ContactSerializer},
    ),
    partial_update=extend_schema(
        description="Частичное обновление контакта по ID.",
        summary="Частичное обновление контакта",
        request=ContactSerializer,
        responses={200: ContactSerializer},
    ),
    destroy=extend_schema(
        description="Удалить контакт по ID.",
        summary="Удаление контакта",
        responses={204: None},
    ),
)
class ContactViewSet(ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    

@extend_schema_view(
    list=extend_schema(
        description="Получить список пользователей.",
        summary="Список пользователей",
        responses={200: UserSerializer(many=True)},
    ),
    create=extend_schema(
        description="Создать нового пользователя.",
        summary="Создание пользователя",
        request=UserSerializer,
        responses={201: UserSerializer},
    ),
    retrieve=extend_schema(
        description="Получить пользователя по ID.",
        summary="Получение пользователя",
        responses={200: UserSerializer},
    ),
    update=extend_schema(
        description="Обновить пользователя по ID.",
        summary="Обновление пользователя",
        request=UserSerializer,
        responses={200: UserSerializer},
    ),
    partial_update=extend_schema(
        description="Частичное обновление пользователя по ID.",
        summary="Частичное обновление пользователя",
        request=UserSerializer,
        responses={200: UserSerializer},
    ),
    destroy=extend_schema(
        description="Удалить пользователя по ID.",
        summary="Удаление пользователя",
        responses={204: None},
    ),
)
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'delete']

@extend_schema_view(
    list=extend_schema(
        description="Получить список заказов.",
        summary="Список заказов",
        responses={200: OrderSerializer(many=True)},
    ),
    create=extend_schema(
        description="Создать новый заказ.",
        summary="Создание заказа",
        request=OrderSerializer,
        responses={201: OrderSerializer},
    ),
    retrieve=extend_schema(
        description="Получить заказ по ID.",
        summary="Получение заказа",
        responses={200: OrderSerializer},
    ),
    update=extend_schema(
        description="Обновить заказ по ID.",
        summary="Обновление заказа",
        request=OrderSerializer,
        responses={200: OrderSerializer},
    ),
    partial_update=extend_schema(
        description="Частичное обновление заказа по ID.",
        summary="Частичное обновление заказа",
        request=OrderSerializer,
        responses={200: OrderSerializer},
    ),
    destroy=extend_schema(
        description="Удалить заказ по ID.",
        summary="Удаление заказа",
        responses={204: None},
    ),
)
class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]