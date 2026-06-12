from django.urls import path,include
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    path('',views.EditAccount.as_view(),name='dashboard'),
    path('accounts/',include("django.contrib.auth.urls")),
    path('register/',views.SignUp.as_view(),name='register'),
    path('redirect/', views.role_redirect, name='role_redirect'),
    path('addaddress/',views.add_address.as_view(),name='addaddress'),
    path('listaddress/',views.list_address.as_view(),name='listaddress'),
    path('deleteaddress/<pk>',views.delete_address.as_view(),name='deleteaddress'),
    path('updateaddress/<pk>',views.update_address.as_view(),name='updateaddress'),
    path('editprofile/',views.EditProfile.as_view(),name='editprofile'),
    path('order_history/',views.order_history,name='order_history'),
    path('admin_dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('track/',views.track_order,name='track_order'),
    path('wishlist/',views.wishlist_view, name='wishlist'),
    path('add-to-wishlist/<int:product_id>/',views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:product_id>/',views.remove_from_wishlist, name='remove_from_wishlist'),
]