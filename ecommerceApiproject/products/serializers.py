from rest_framework import serializers
from .models import Product, Category


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
  