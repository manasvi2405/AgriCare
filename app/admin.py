from django.contrib import admin
from .models import Contact
from .models import Article
from .models import Category
from .models import Brand
from .models import Product
from .models import ProductCategory,PlantDisease

# Register your models here.
admin.site.register(Contact)
admin.site.register(Article)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(ProductCategory)
admin.site.register(PlantDisease)
