from django.contrib import admin
from mcashpos.models import Product
from mcashpos.models import ProductSale
from mcashpos.models import Sale


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'image_id')

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductSale)
admin.site.register(Sale)
