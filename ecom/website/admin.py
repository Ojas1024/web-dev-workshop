from django.contrib import admin
from .models import Category, Product, Order, Cart, SavedAddress

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'rate', 'quantity', 'featured', 'category')
    list_filter = ('featured', 'category')
    search_fields = ('title', 'description')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'ordered_at')
    list_filter = ('ordered_at', 'user')
    search_fields = ('user__username', 'product__title')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    list_filter = ('added_at', 'user')
    search_fields = ('user__username', 'product__title')

@admin.register(SavedAddress)
class SavedAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address')
    search_fields = ('user__username', 'address')
