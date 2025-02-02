from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from .models import Product, Shop, Category, User, Contact
from .serializers import (
    ProductSerializer,
    ShopSerializer,
    CategorySerializer,
    UserSerializer,
    ContactSerializer,
    RegisterAccountSerializer,
)
from rest_framework.parsers import JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework import status


class RegisterAccount(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegisterAccountSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"Status": "success", "Message": "User created successfully."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [JSONParser]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
    ]
    filterset_fields = [
        "name",
        "category",
    ]
    search_fields = [
        "name",
        "category__name",
        "model",
    ]
    pagination_class = LimitOffsetPagination

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
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


class ShopViewSet(ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class UserDetailViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ContactViewSet(ModelViewSet):
    serializer_class = ContactSerializer

    def get_queryset(self):
        user_id = self.kwargs["user_pk"]
        return Contact.objects.filter(user_id=user_id)

    def perform_create(self, serializer):
        serializer.save(user_id=self.kwargs["user_pk"])

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
