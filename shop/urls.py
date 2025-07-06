from django.urls import path
from . import views

urlpatterns = [    
    path('', views.home, name='home'),
    path('about/',views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),

    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    path('favorites/', views.favorites_view, name='favorites'),
    path('favorites/add/<int:pk>/', views.add_to_favorites, name='add_to_favorites'),
    path('favorites/remove/<int:pk>/', views.remove_from_favorites, name='remove_from_favorites'),
    path('favorite/<int:pk>/', views.toggle_favorite, name='toggle_favorite'),

    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),

    path('review/<int:pk>/', views.add_review, name='add_review'),
    
    path('checkout/', views.checkout_view, name='checkout'),

    path('orders/history/', views.order_history, name='order_history'),
    path('confirm-order/', views.confirm_order, name='confirm_order'),
    path('my-orders/', views.my_orders, name='my_orders'),
]
