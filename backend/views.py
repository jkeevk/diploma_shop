from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView

from .models import Product, Shop, Category, User, Contact, Order, OrderItem
from .serializers import (
    ProductSerializer,
    ShopSerializer,
    CategorySerializer,
    UserRegistrationSerializer,
    ContactSerializer,
    OrderSendMailSerializer,
    FileUploadSerializer,
    OrderSerializer,
    OrderItemSerializer,
    UserSerializer,
)

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.core.management import call_command
import os

import uuid
from django.urls import reverse
from django.core.mail import send_mail
from orders.settings import EMAIL_HOST_USER, BACKEND_URL
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from drf_spectacular.utils import extend_schema, extend_schema_field, OpenApiExample


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

@extend_schema(
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'file': {
                    'type': 'string',
                    'format': 'binary',
                }
            }
        }
    },
    responses={
        200: {"description": "Data loaded successfully"},
        400: {"description": "Bad request (invalid file or no file uploaded)"},
        500: {"description": "Internal server error"},
    },
)
class PartnerUpdateView(APIView):
    serializer_class = FileUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        if "file" not in request.FILES:
            return Response(
                {"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST
            )

        uploaded_file = request.FILES["file"]
        file_path = os.path.join("data", uploaded_file.name)

        try:
            call_command("load_products", file_path)
            return Response(
                {"message": "Data loaded successfully"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = LimitOffsetPagination

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

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    serializer_class = UserRegistrationSerializer
    @extend_schema(
        examples=[
            OpenApiExample(
                "Пример регистрации покупателя",
                value={
                    "email": "customer1@example.com",
                    "password": "strongpassword123",
                    "name": "Иван",
                    "surname": "Иванов",
                    "is_customer": True,
                    "is_supplier": False,
                },
            ),
            OpenApiExample(
                "Пример регистрации поставщика",
                value={
                    "email": "supplier1@example.com",
                    "password": "strongpassword123",
                    "name": "Петр",
                    "surname": "Петров",
                    "is_customer": False,
                    "is_supplier": True,
                },
            ),
        ]
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            if User.objects.filter(email=email).exists():
                return Response(
                    {
                        "Status": "error",
                        "Message": "User with this email already exists.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = serializer.save()
            self.send_confirmation_email(user)
            return Response(
                {
                    "Status": "success",
                    "Message": "User created successfully. Please check your email to confirm registration.",
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_confirmation_email(self, user):
        token = uuid.uuid4().hex
        user.confirmation_token = token
        user.save()

        confirmation_url = reverse("user-register-confirm", kwargs={"token": token})
        full_url = f"{BACKEND_URL}{confirmation_url}"
        subject = "Confirm your registration"
        message = f"Please click the link to confirm your registration: {full_url}"
        send_mail(subject, message, EMAIL_HOST_USER, [user.email])

@extend_schema(exclude=True)
class ConfirmRegistrationView(APIView):
    def get(self, request, token, *args, **kwargs):
        user = get_object_or_404(User, confirmation_token=token)

        user.is_active = True
        user.confirmation_token = None
        user.save()

        return Response(
            {
                "Status": "success",
                "Message": "Your account has been successfully activated.",
            },
            status=status.HTTP_200_OK,
        )


class OrderSendMailView(APIView):
    pass
    # def post(self, request):
    #     serializer = OrderSendMailSerializer(data=request.data)
    #     if serializer.is_valid():
    #         user_email = serializer.validated_data["user_email"]
    #         user_name = serializer.validated_data["user_name"]
    #         order_details = serializer.validated_data["order_details"]

    #         print(
    #             f"Отправка письма на: {user_email} от {user_name} с деталями: {order_details}"
    #         )  # Для отладки

    #         try:
    #             send_mail(
    #                 "Subject here",
    #                 f"Here is the message from {user_name}. Details: {order_details}",
    #                 EMAIL_HOST_USER,
    #                 [user_email],
    #                 fail_silently=False,
    #             )
    #             return Response({"status": "Письмо отправлено"})
    #         except Exception as e:
    #             print(f"Ошибка при отправке письма: {e}")
    #             return Response({"error": str(e)}, status=400)

    #     return Response(serializer.errors, status=400)


class CategoryView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ShopView(ListAPIView):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer


class ContactViewSet(ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


