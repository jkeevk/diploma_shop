import os

# Django
from django.contrib.auth.tokens import default_token_generator
from django.core.management import call_command
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django_filters.rest_framework import DjangoFilterBackend

# Rest Framework
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

# Local imports
from .filters import ProductFilter
from .models import Category, Contact, Order, Product, Shop, User
from .permissions import IsAdminUser, IsCustomer, IsSupplier
from .serializers import (
    CategorySerializer,
    ContactSerializer,
    FileUploadSerializer,
    LoginSerializer,
    OrderSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    ProductSerializer,
    ShopSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)
from .swagger_configs import SWAGGER_CONFIGS

class LoginView(APIView):
    """
    Представление для аутентификации пользователя и получения JWT-токенов.
    При успешной аутентификации возвращает access и refresh токены.
    """
    @SWAGGER_CONFIGS["login_schema"]
    def post(self, request, *args, **kwargs):
        """
        Аутентифицирует пользователя и возвращает JWT-токены.
        """
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


@SWAGGER_CONFIGS["password_reset_schema"]
class PasswordResetView(GenericAPIView):
    """
    Представление для сброса пароля. Отправляет ссылку для сброса на email пользователя.
    """
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
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


@SWAGGER_CONFIGS["password_reset_confirm_schema"]
class PasswordResetConfirmView(GenericAPIView):
    """
    Представление для подтверждения сброса пароля. Позволяет установить новый пароль.
    """
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        """
        Подтверждает сброс пароля и устанавливает новый пароль.
        """
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


@SWAGGER_CONFIGS["partner_update_schema"]
class PartnerUpdateView(APIView):
    """
    Представление для обновления данных поставщика через загрузку файла.
    """
    serializer_class = FileUploadSerializer
    permission_classes = [IsSupplier | IsAdminUser]

    def post(self, request, *args, **kwargs):
        """
        Загружает файл с данными и обновляет информацию о товарах.
        """
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
    permission_classes = [IsSupplier | IsAdminUser]


@SWAGGER_CONFIGS["register_schema"]
class RegisterView(APIView):
    """
    Представление для регистрации нового пользователя.
    """
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
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


@SWAGGER_CONFIGS["confirm_registration_schema"]
class ConfirmRegistrationView(APIView):
    """
    Представление для подтверждения регистрации пользователя по токену.
    """
    serializer_class = None

    def get(self, request, token, *args, **kwargs):
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


@SWAGGER_CONFIGS["category_schema"]
class CategoryView(ListAPIView):
    """
    Представление для получения списка категорий товаров.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


@SWAGGER_CONFIGS["shop_schema"]
class ShopView(ListAPIView):
    """
    Представление для получения списка магазинов.
    """
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer


@SWAGGER_CONFIGS["contact_viewset_schema"]
class ContactViewSet(ModelViewSet):
    """
    Сет представлений для управления контактами пользователя.
    """
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsCustomer | IsSupplier | IsAdminUser]


@SWAGGER_CONFIGS["user_viewset_schema"]
class UserViewSet(ModelViewSet):
    """
    Сет представлений для управления данными пользователя.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsCustomer | IsSupplier | IsAdminUser]
    http_method_names = ['get', 'put', 'patch', 'delete']


@SWAGGER_CONFIGS["order_viewset_schema"]
class OrderViewSet(ModelViewSet):
    """
    Сет представлений для управления заказами. Доступен только для администраторов и поставщиков.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser | IsSupplier]


@SWAGGER_CONFIGS["basket_viewset_schema"]
class BasketViewSet(ModelViewSet):
    """
    Сет представлений для управления корзиной пользователя.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsCustomer]

    def get_queryset(self):
        """
        Возвращает только заказы текущего пользователя со статусом "new".
        """
        return Order.objects.filter(user=self.request.user, status="new")

    def perform_create(self, serializer):
        """
        Создает новый заказ или использует существующий заказ со статусом "new".
        """
        order = Order.objects.filter(user=self.request.user, status="new").first()

        if not order:
            order = Order.objects.create(user=self.request.user, status="new")

        serializer.save(user=self.request.user, status="new", id=order.id)


@SWAGGER_CONFIGS["partner_orders_schema"]
class PartnerOrders(APIView):
    """
    Представление для получения заказов, связанных с магазином поставщика.
    """
    permission_classes = [IsSupplier]

    def get(self, request):
        """
        Возвращает список заказов, связанных с магазином поставщика.
        """
        if request.user.is_anonymous:
            return Response({"detail": "Пожалуйста, войдите в систему."}, status=status.HTTP_401_UNAUTHORIZED)
        
        shop = Shop.objects.filter(user=request.user).first()

        if not shop:
            return Response({"detail": "Вы не связаны с магазином."}, status=status.HTTP_400_BAD_REQUEST)

        orders = Order.objects.filter(order_items__shop=shop, status="confirmed").distinct()
        order_serializer = OrderSerializer(orders, many=True)
        return Response(order_serializer.data)


@SWAGGER_CONFIGS["confirm_basket_schema"]
class ConfirmBasketView(APIView):
    """
    Представление для подтверждения корзины и создания заказа.
    """
    permission_classes = [IsCustomer]

    def post(self, request):
        """
        Подтверждает корзину, создает заказ и связывает его с контактом пользователя.
        """
        order = Order.objects.filter(user=request.user, status="new").first()

        if not order:
            return Response({"detail": "Корзина пуста."}, status=status.HTTP_400_BAD_REQUEST)

        contact_id = request.data.get('contact_id')
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
