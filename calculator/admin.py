from django.contrib import admin
<<<<<<< HEAD
from .models import Warehouse, PostalOffice, FullIndex


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('warehouse_name', 'city_name', 'region_name', 'index')
    search_fields = ('warehouse_name', 'city_name', 'region_name')


@admin.register(FullIndex)
class FullIndexAdmin(admin.ModelAdmin):
    list_display = ('index', 'region', 'comments')
    search_fields = ("index", 'comments')


@admin.register(PostalOffice)
class PostalOfficeAdmin(admin.ModelAdmin):
    list_display = ('index', 'name_uz', 'region', 'city', 'working_days')
    search_fields = ('name_uz', 'region', 'city')
=======
from .models import OrderCart

#admin.site.register(OrderCart)


@admin.register(OrderCart)
class OrderCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'barcode', 'price')
    search_fields = ('id', 'user__first_name', 'barcode')
>>>>>>> 2d32d04 (full complated uzpost backend)
