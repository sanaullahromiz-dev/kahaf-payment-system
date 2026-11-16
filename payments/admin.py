from django.contrib import admin
from .models import Product, CustomerRegistration, DirectPayment, ProjectFile, SalesReceipt

# এডমিন প্যানেলের হেডার ও টাইটেল কাস্টমাইজেশন (Kahaf Computer)
admin.site.site_header = "Kahaf Computer এডমিন ড্যাশবোর্ড"
admin.site.site_title = "Kahaf Computer Admin"
admin.site.index_title = "পেমেন্ট, বিক্রি ও ফাইল ব্যবস্থাপনা"


# ১. প্রোডাক্ট এডমিন
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'billing_type', 'price')
    list_filter = ('billing_type',)
    search_fields = ('name',)
    list_editable = ('price',)  # তালিকা থেকেই সরাসরি দাম পরিবর্তন করার সুবিধা
    ordering = ('-id',)


# ২. গ্রাহক নিবন্ধন এডমিন
@admin.register(CustomerRegistration)
class CustomerRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        'registration_id', 
        'name', 
        'mobile_number', 
        'product', 
        'amount', 
        'payment_type', 
        'user', 
        'created_at'
    )
    search_fields = ('registration_id', 'name', 'mobile_number')
    list_filter = ('payment_type', 'registration_month', 'registration_year', 'created_at')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


# ৩. বিক্রি রশিদ এডমিন (নতুন যুক্ত করা হলো)
@admin.register(SalesReceipt)
class SalesReceiptAdmin(admin.ModelAdmin):
    list_display = (
        'receipt_no', 
        'customer', 
        'product', 
        'total_amount', 
        'payment_type', 
        'created_at'
    )
    search_fields = ('receipt_no', 'customer__name', 'customer__registration_id')
    list_filter = ('payment_type', 'created_at')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


# ৪. সরাসরি পেমেন্ট এডমিন (রশিদ নম্বর সহ আপডেট করা হলো)
@admin.register(DirectPayment)
class DirectPaymentAdmin(admin.ModelAdmin):
    list_display = (
        'customer', 
        'receipt_no',
        'product_name', 
        'payment_method', 
        'transaction_id', 
        'total_amount', 
        'paid_amount', 
        'payment_type', 
        'is_verified', 
        'created_at'
    )
    list_filter = ('is_verified', 'payment_method', 'payment_type', 'created_at')
    search_fields = ('transaction_id', 'receipt_no', 'customer__name', 'customer__registration_id', 'product_name')
    list_editable = ('is_verified',)  # তালিকা থেকে এক ক্লিকে পেমেন্ট ভেরিফাই করার সুযোগ
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


# ৫. প্রজেক্ট ও ফাইল আদান-প্রদান এডমিন
@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'customer', 'sender', 'file', 'created_at')
    list_filter = ('sender', 'created_at')
    search_fields = ('title', 'customer__name', 'customer__registration_id')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)