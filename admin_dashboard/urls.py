from django.urls import path
from . import views

urlpatterns = [
    # এডমিন প্যানেলের লিঙ্কসমূহ
    path('login/', views.admin_dashboard_login, name='admin_login'),
    path('', views.custom_admin_dashboard, name='custom_admin_dashboard'),
    path('sell-product/', views.create_sales_receipt, name='create_sales_receipt'),
    path('verify-payment/<int:payment_id>/', views.verify_payment, name='verify_payment'),
    path('add-customer/', views.admin_add_customer, name='admin_add_customer'),
    path('customers/', views.admin_customer_list, name='admin_customer_list'),
    path('customer/<int:customer_id>/', views.admin_customer_profile, name='admin_customer_profile'),
    
    # API লিঙ্কসমূহ
    path('api/receipt/<str:receipt_no>/', views.get_receipt_data, name='get_receipt_data'),
    path('api/customer/<int:customer_id>/', views.get_customer_data, name='get_customer_data'),

    path('receipts/', views.receipt_list, name='receipt_list'),
    path('receipt/<int:receipt_id>/', views.receipt_detail, name='receipt_detail'),

    path('send-file/', views.admin_send_file, name='admin_send_file'),
]