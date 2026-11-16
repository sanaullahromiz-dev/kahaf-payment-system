from django.db import models
from django.contrib.auth.models import User
from datetime import date

# ১. প্রোডাক্ট বা সার্ভিস মডেল
class Product(models.Model):
    BILLING_CHOICES = (
        ('one_time', 'এককালীন (One-time)'),
        ('monthly', 'মাসিক (Monthly)'),
        ('yearly', 'বাৎসরিক (Yearly)'),
    )
    name = models.CharField(max_length=200, verbose_name="প্রোডাক্ট/সার্ভিসের নাম")
    billing_type = models.CharField(max_length=20, choices=BILLING_CHOICES, verbose_name="পেমেন্ট টাইপ")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="মূল্য (টাকা)")

    def __str__(self):
        return f"{self.name} ({self.get_billing_type_display()})"


# ২. গ্রাহক নিবন্ধন মডেল
class CustomerRegistration(models.Model):
    MONTH_CHOICES = (
        ('January', 'জানুয়ারি'), ('February', 'ফেব্রুয়ারি'), ('March', 'মার্চ'),
        ('April', 'এপ্রিল'), ('May', 'মে'), ('June', 'জুন'),
        ('July', 'জুলাই'), ('August', 'আগস্ট'), ('September', 'সেপ্টেম্বর'),
        ('October', 'অক্টোবর'), ('November', 'নভেম্বর'), ('December', 'ডিসেম্বর'),
    )
    PAYMENT_TYPES = (('One-time', 'এককালীন'), ('Monthly', 'মাসিক'), ('Yearly', 'বাৎসরিক'))

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="customer_profile", verbose_name="সংযুক্ত অ্যাকাউন্ট")
    registration_id = models.CharField(max_length=50, unique=True, verbose_name="নিবন্ধন ফরম আইডি")
    name = models.CharField(max_length=150, verbose_name="গ্রাহকের নাম")
    address = models.TextField(verbose_name="ঠিকানা")
    mobile_number = models.CharField(max_length=15, unique=True, verbose_name="মোবাইল নাম্বার")
    
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="প্রোডাক্ট নাম")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="টাকার পরিমাণ")
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, verbose_name="পরিশোধের ধরন")
    
    registration_month = models.CharField(max_length=20, choices=MONTH_CHOICES, verbose_name="নিবন্ধন মাস")
    registration_year = models.IntegerField(verbose_name="নিবন্ধন বছর (যেমন: 2026)")
    payment_month = models.CharField(max_length=20, choices=MONTH_CHOICES, verbose_name="পরিশোধের মাস")
    payment_year = models.IntegerField(verbose_name="পরিশোধের বছর (যেমন: 2026)")
    
    photo = models.ImageField(upload_to='customer_photos/', blank=True, null=True, verbose_name="গ্রাহকের ছবি")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="নিবন্ধনের সময়")

    def __str__(self):
        return f"{self.name} ({self.registration_id})"


# 🌟 নতুন: ৩. এডমিন কর্তৃক বিক্রি রশিদ মডেল
class SalesReceipt(models.Model):
    PAYMENT_TYPES = (('One-time', 'এককালীন'), ('Monthly', 'মাসিক'), ('Yearly', 'বাৎসরিক'))
    
    receipt_no = models.CharField(max_length=50, unique=True, verbose_name="সেলার রশিদ নং")
    customer = models.ForeignKey(CustomerRegistration, on_delete=models.CASCADE, related_name='receipts', verbose_name="গ্রাহক")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name="প্রোডাক্ট/সার্ভিস")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="মোট মূল্য")
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, verbose_name="পরিশোধের ধরন")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="রশিদ তৈরির তারিখ")
    next_billing_date = models.DateField(null=True, blank=True, verbose_name="পরবর্তী বিলের তারিখ (মাসিক/বাৎসরিক এর জন্য)")

    def __str__(self):
        return f"রশিদ: {self.receipt_no} | গ্রাহক: {self.customer.name}"


# ৪. গ্রাহকের সরাসরি পেমেন্ট সাবমিশন মডেল (আপডেট করা হয়েছে)
class DirectPayment(models.Model):
    METHOD_CHOICES = (('bKash', 'বিকাশ'), ('Nagad', 'নগদ'))
    BILLING_CHOICES = (('One-time', 'এককালীন'), ('Monthly', 'মাসিক'), ('Yearly', 'বাৎসরিক'))

    customer = models.ForeignKey(CustomerRegistration, on_delete=models.CASCADE, related_name='payments', verbose_name="গ্রাহক")
    receipt_no = models.CharField(max_length=50, blank=True, null=True, verbose_name="সেলার রশিদ নং") # নতুন যুক্ত করা হলো
    product_name = models.CharField(max_length=200, verbose_name="প্রোডাক্ট/সার্ভিসের নাম")
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES, verbose_name="পেমেন্ট টাইপ")
    transaction_id = models.CharField(max_length=100, verbose_name="ট্রানজেকশন আইডি")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="মোট মূল্য")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="পরিশোধিত টাকা")
    payment_type = models.CharField(max_length=20, choices=BILLING_CHOICES, verbose_name="পরিশোধের ধরন")
    is_verified = models.BooleanField(default=False, verbose_name="এডমিন ভেরিফাইড?")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} - {self.transaction_id}"


# ৫. ফাইল/প্রজেক্ট আদান-প্রদান মডেল
class ProjectFile(models.Model):
    SENDER_CHOICES = (('customer', 'গ্রাহক হতে প্রেরিত'), ('admin', 'এডমিন হতে প্রেরিত'))
    
    customer = models.ForeignKey(CustomerRegistration, on_delete=models.CASCADE, related_name='files', verbose_name="গ্রাহক")
    title = models.CharField(max_length=200, verbose_name="ফাইলের শিরোনাম/বিবরণ")
    file = models.FileField(upload_to='project_files/', verbose_name="ফাইল/প্রজেক্ট")
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES, verbose_name="প্রেরক")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_sender_display()})"


        # 🔔 ৬. গ্রাহকের নোটিফিকেশন মডেল
class Notification(models.Model):
    customer = models.ForeignKey(CustomerRegistration, on_delete=models.CASCADE, related_name='notifications', verbose_name="গ্রাহক")
    message = models.TextField(verbose_name="মেসেজ")
    is_read = models.BooleanField(default=False, verbose_name="পড়া হয়েছে?")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.customer.name}"


# 🛒 ৭. নতুন প্রোডাক্ট অর্ডার অনুরোধ মডেল (নতুন যুক্ত)
class ProductOrderRequest(models.Model):
    customer = models.ForeignKey(CustomerRegistration, on_delete=models.CASCADE, related_name='order_requests', verbose_name="গ্রাহক")
    product_name = models.CharField(max_length=250, verbose_name="নির্বাচিত প্রোডাক্ট/সার্ভিস")
    is_contacted = models.BooleanField(default=False, verbose_name="যোগাযোগ সম্পন্ন?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="অনুরোধের সময়")

    def __str__(self):
        return f"{self.customer.name} - {self.product_name}"