from django.contrib import admin
from django.urls import path, include
from website import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
urlpatterns = [

    path('', views.index),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path('product/<int:product_id>', views.see_product), 
    path('buy/<int:product_id>', views.buy_product), 
    path('category/<int:cat_id>', views.browse_category),
    path('buy/<int:product_id>/', views.buy_product, name='buy_product'),
     path('capture_payment/', views.capture_payment, name='capture_payment'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('myorders', views.myorders)
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
