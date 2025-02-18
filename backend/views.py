import os
from django.core.management import call_command
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
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
from rest_framework.decorators import action

from .filters import ProductFilter
from .permissions import IsAdminOrSupplier

from .models import Category, Contact, Order, Product, Shop, User
from .serializers import (
    CategorySerializer,
    ContactSerializer,
    FileUploadSerializer,
    OrderSerializer,
    ProductSerializer,
    ShopSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    LoginSerializer
)
from .swagger_configs import SWAGGER_CONFIGS


class LoginView(APIView):
    @SWAGGER_CONFIGS["login_schema"]
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

@SWAGGER_CONFIGS["password_reset_schema"]
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

@SWAGGER_CONFIGS["password_reset_confirm_schema"]
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

@SWAGGER_CONFIGS["partner_update_schema"]
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


@SWAGGER_CONFIGS["product_viewset_schema"]
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = ProductFilter
    search_fields = ["name", "model", "category__name"]
    permission_classes = [IsAdminOrSupplier]


@SWAGGER_CONFIGS["register_schema"]
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


@SWAGGER_CONFIGS["confirm_registration_schema"]
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


@SWAGGER_CONFIGS["category_schema"]
class CategoryView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


@SWAGGER_CONFIGS["shop_schema"]
class ShopView(ListAPIView):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer


@SWAGGER_CONFIGS["contact_viewset_schema"]
class ContactViewSet(ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]


@SWAGGER_CONFIGS["user_viewset_schema"]
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'delete']


@SWAGGER_CONFIGS["order_viewset_schema"]
class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminOrSupplier]

@SWAGGER_CONFIGS["basket_viewset_schema"]
class BasketViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, status="new")

    def perform_create(self, serializer):
        order = Order.objects.filter(user=self.request.user, status="new").first()

        if not order:
            order = Order.objects.create(user=self.request.user, status="new")

        serializer.save(user=self.request.user, status="new", id=order.id)

class PartnerOrders(APIView):
    permission_classes = [IsAdminOrSupplier]

    def get(self, request):
        shop = Shop.objects.filter(user=request.user).first()
        if not shop:
            return Response({"detail": "Вы не связаны с магазином."}, status=status.HTTP_400_BAD_REQUEST)
        orders = Order.objects.filter(order_items__shop=shop).distinct()
        order_serializer = OrderSerializer(orders, many=True)
        return Response(order_serializer.data)

