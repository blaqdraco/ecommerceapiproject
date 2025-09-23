from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Product, Category
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    CategoryListSerializer,
    CategoryDetailSerializer,
    CartSerializer,
    CartItemSerializer,
)
from .models import Cart, CartItem, Product


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer  # default for retrieve/create/update
    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    # Use lightweight fields for list; detailed fields for retrieve.
    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        return super().get_serializer_class()


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializer  # default for retrieve/create/update
    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    def get_serializer_class(self):
        if self.action == "list":
            return CategoryListSerializer
        return super().get_serializer_class()


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.prefetch_related("items__product").all()
    serializer_class = CartSerializer
    lookup_field = "cart_code"
    lookup_url_kwarg = "cart_code"

    def create(self, request, *args, **kwargs):
        cart = Cart.objects.create()
        serializer = self.get_serializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="items")
    def add_or_set_item(self, request, cart_code=None):
        cart = self.get_object()
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data["product"]
        quantity = serializer.validated_data.get("quantity", 1)
        item, _created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={"quantity": quantity})
        if not _created:
            item.quantity = quantity
            item.save(update_fields=["quantity", "updated_at"])
        # Return the full cart
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"], url_path=r"items/(?P<item_id>[^/.]+)")
    def update_item(self, request, cart_code=None, item_id=None):
        cart = self.get_object()
        item = get_object_or_404(CartItem, pk=item_id, cart=cart)
        quantity = request.data.get("quantity")
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response({"detail": "quantity must be an integer"}, status=status.HTTP_400_BAD_REQUEST)
        if quantity <= 0:
            item.delete()
        else:
            item.quantity = quantity
            item.save(update_fields=["quantity", "updated_at"])
        return Response(CartSerializer(cart).data)

    @action(detail=True, methods=["delete"], url_path=r"items/(?P<item_id>[^/.]+)")
    def remove_item(self, request, cart_code=None, item_id=None):
        cart = self.get_object()
        item = get_object_or_404(CartItem, pk=item_id, cart=cart)
        item.delete()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["delete"], url_path="clear")
    def clear(self, request, cart_code=None):
        cart = self.get_object()
        cart.items.all().delete()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)
