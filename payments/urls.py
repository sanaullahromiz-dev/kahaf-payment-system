from django.urls import path
from . import views

urlpatterns = [
    # শুধুমাত্র গ্রাহকের লিঙ্কসমূহ
    path('', views.customer_login, name='login'),
    path('register/', views.customer_register, name='register'),
    path('logout/', views.customer_logout, name='logout'),
    path('dashboard/', views.profile_dashboard, name='dashboard'),
    path('payment/', views.make_payment, name='make_payment'),
]