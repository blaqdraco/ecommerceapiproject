from django.contrib import admin
from .models import Product, Category, Cart, CartItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "price", "category", "created_at")
    search_fields = ("name",)
    list_filter = ("created_at", "category")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "cart_code", "created_at", "updated_at")
    search_fields = ("cart_code",)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "product", "quantity", "created_at")
    list_select_related = ("cart", "product")
    list_filter = ("created_at", "updated_at")
