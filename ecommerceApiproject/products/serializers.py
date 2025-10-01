from rest_framework import serializers
from .models import Product, Category, Cart, CartItem, Review
from django.contrib.auth import get_user_model


"""
Restructured serializers:
- Use ListSerializer for list endpoints
- Use DetailSerializer for retrieve/create/update/delete
"""


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "slug", "image", "price"]


class ProductDetailSerializer(serializers.ModelSerializer):
    # Read: nested minimal category; Write: category_id
    from typing import Optional  # noqa: F401 (type hints only)
    # Import here to avoid circular import ordering issues in some IDEs
    # but since it's same module, it's fine either way.
    category = serializers.SerializerMethodField(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True, allow_null=True, required=False
    )

    class Meta:
        model = Product
        fields = [
            "id", "name", "description", "slug", "image", "price",
            "category", "category_id"
        ]

    def get_category(self, obj):
        # Minimal shape for nested category in detail responses
        if obj.category_id:
            return {
                "id": obj.category_id,
                "name": obj.category.name,
                "slug": obj.category.slug,
                "image": obj.category.image.url if obj.category.image else None,
            }
        return None


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "image"]


class CategoryDetailSerializer(serializers.ModelSerializer):
    # Include minimal product info on detail using the list serializer
    products = ProductListSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "image", "products"]
        read_only_fields = ["id", "slug", "products"]


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    line_total = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CartItem
        fields = [
            "id", "product", "product_id", "quantity", "line_total",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "line_total", "created_at", "updated_at", "product"]

    def get_line_total(self, obj):
        return obj.line_total


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "cart_code", "items", "total", "created_at", "updated_at"]
        read_only_fields = ["id", "cart_code", "items", "total", "created_at", "updated_at"]
    def get_total(self, obj):
        return sum(item.line_total for item in obj.items.all())
  
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'first_name', 'last_name']
        read_only_fields = ['id']
class ReviewSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)   