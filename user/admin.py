from django.contrib import admin
from .models import UserProfile
from .models import Cart
from .models import CartItem,Address,Order,OrderItem,Wishlist

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Wishlist)

