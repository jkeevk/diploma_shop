import os
from django.core.management import call_command
from django.shortcuts import get_object_or_404
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
from rest_framework_simplejwt.tokens import RefreshToken

from .filters import ProductFilter
from .permissions import IsAdminOrSupplier

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
    PasswordResetConfirmSerializer,
    LoginSerializer
)
from django.contrib.auth.tokens import default_token_generator

from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str


# Эндпоинт для авторизации пользователя
class LoginView(APIView):
    @extend_schema(
        summary="Авторизация", 
        description="Эндпоинт для авторизации пользователя с помощью электронной почты и пароля.", 
        request=LoginSerializer,
        responses={
            200: {
                'description': 'Successful login',
                'examples': [
                    {
                        'application/json': {
                            'user_id': 1,
                            'email': 'user@example.com',
                            'access_token': 'string',
                            'refresh_token': 'string',
                        }
                    }
                ],
            },
            400: {
                'description': 'Bad request',
                'examples': [
                    {
                        'application/json': {
                            'non_field_errors': ['Invalid credentials.']
                        }
                    }
                ],
            },
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response({
                'user_id': user.id,
                'email': user.email,
                'access_token': access_token,
                'refresh_token': refresh_token
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    summary="Новый пароль", description="Эндпоинт для создания нового пароля."
)
class PasswordResetConfirmView(GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):

        uid = force_str(urlsafe_base64_decode(kwargs['uidb64']))
        token = kwargs['token']
        
        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            return Response({"detail": "Пользователь не найден."}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Недействительный токен."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({"detail": "Пароль успешно изменён."}, status=status.HTTP_200_OK)
    
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
    permission_classes = [IsAdminOrSupplier]

    def post(self, request, *args, **kwargs):
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
        description="Получить список товаров.",
        summary="Список товаров",
        responses={200: ProductSerializer(many=True)},
    ),
    create=extend_schema(
        description="Создать новый товар.",
        summary="Создание товара",
        request=ProductSerializer,
        responses={201: ProductSerializer},
    ),
    retrieve=extend_schema(
        description="Получить товар по ID.",
        summary="Получение товара",
        responses={200: ProductSerializer},
    ),
    update=extend_schema(
        description="Обновить товар по ID.",
        summary="Обновление товара",
        request=ProductSerializer,
        responses={200: ProductSerializer},
    ),
    partial_update=extend_schema(
        description="Частичное обновление товара по ID.",
        summary="Частичное обновление товара",
        request=ProductSerializer,
        responses={200: ProductSerializer},
    ),
    destroy=extend_schema(
        description="Удалить товар по ID.",
        summary="Удаление товара",
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
    permission_classes = [IsAdminOrSupplier]


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