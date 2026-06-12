from django.urls import path
from . import views
urlpatterns = [
    path('',views.home,name='home'),
    path('about/',views.about,name='about'),
    path('privacy/',views.privacy,name='privacy'),
    path('terms/',views.terms,name='terms'),
    path('contact/',views.contact,name='contact'),
    path('blog/<cat>',views.blog,name='blog'),
    path('article/<id>/',views.article,name='article'),
    path('shop/<cat>',views.shop,name='shop'),
    path('product/<id>/',views.product,name='product'),
    path('shopbycategory/<cat>',views.shopbycategory,name='shopbycategory'),
    path('shopbybrand/<brand>',views.shopbybrand,name='shopbybrand'),
    path('news/',views.news,name='news'),
    path('cart/', views.view_cart, name='view_cart'),
   path('add_to_cart/<item_id>', views.add_to_cart, name='add_to_cart'),
   path('update_cart_quantity/<str:action>/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
   path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout_view/', views.checkout_view, name='checkout_view'),
    path('payment/verify/', views.payment_verify, name='payment_verify'),
    path('process_order/',views.process_order,name='process_order'),
    path('payment_page/<order_id>',views.payment_page,name='payment_page'),
    path('cancel_order/<order_id>',views.cancel_order,name='cancel_order'),
    path('croprecommendation',views.croprecommendation,name='croprecommendation'),
    path('predict_yield',views.predict_yield,name='predict_yield'),
    path('detectdisease',views.detectdisease,name='detectdisease')
]