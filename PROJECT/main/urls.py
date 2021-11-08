from django.urls import path, include
from django.contrib.auth import views as auth_views
from main import views

urlpatterns = [
    path('', views.index),
    path('register/', views.register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/profile/', views.profile, name='profile'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('logout/', views.logoutUser, name='logout'),
    path('about/', views.about, name='about'),
    path('products/', views.product_page, name='products'),
    path('products/<str:slug>', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name="checkout"),
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
]
