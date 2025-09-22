from rest_framework import viewsets
from .models import Product, Category
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    CategoryListSerializer,
    CategoryDetailSerializer,
)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer  # default for retrieve/create/update

    # Use lightweight fields for list; detailed fields for retrieve.
    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        return super().get_serializer_class()


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializer  # default for retrieve/create/update

    def get_serializer_class(self):
        if self.action == "list":
            return CategoryListSerializer
        return super().get_serializer_class()
