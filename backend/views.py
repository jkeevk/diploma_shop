from rest_framework.viewsets import ModelViewSet
from .models import Product, Shop, Category, User, Contact
from .serializers import (
    ProductSerializer,
    ShopSerializer,
    CategorySerializer,
    UserSerializer,
    ContactSerializer,
    OrderSendMailSerializer,
    FileUploadSerializer
)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from rest_framework.views import APIView
from orders.settings import EMAIL_HOST_USER
from django.core.management import call_command
import os


class PartnerUpdate(APIView):
    def post(self, request, *args, **kwargs):
        serializer = FileUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if 'file' not in request.FILES:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = request.FILES['file']
        file_path = os.path.join('data', uploaded_file.name)

        try:
            # Вызываем management command
            call_command('load_products', file_path)
            return Response({'message': 'Data loaded successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ContactViewSet(ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def get_queryset(self):
        user_id = self.kwargs["user_pk"]
        return Contact.objects.filter(user_id=user_id)

    def perform_create(self, serializer):
        try:
            serializer.save(user_id=self.kwargs["user_pk"])
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


class ShopViewSet(ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data.get("name")
            if Shop.objects.filter(name=name).exists():
                return Response(
                    {
                        "Status": "error",
                        "Message": "Shop with this name already exists.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            self.perform_create(serializer)
            return Response(
                {"Status": "success", "Message": "Shop created successfully."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
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
            self.perform_create(serializer)
            return Response(
                {"Status": "success", "Message": "User created successfully."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderSendMailView(APIView):
    def post(self, request):
        serializer = OrderSendMailSerializer(data=request.data)
        if serializer.is_valid():
            user_email = serializer.validated_data['user_email']
            user_name = serializer.validated_data['user_name']
            order_details = serializer.validated_data['order_details']

            print(f"Отправка письма на: {user_email} от {user_name} с деталями: {order_details}")  # Для отладки

            try:
                send_mail(
                    "Subject here",
                    f"Here is the message from {user_name}. Details: {order_details}",
                    EMAIL_HOST_USER,
                    [user_email],
                    fail_silently=False,
                )
                return Response({'status': 'Письмо отправлено'})
            except Exception as e:
                print(f"Ошибка при отправке письма: {e}")
                return Response({'error': str(e)}, status=400)

        return Response(serializer.errors, status=400)