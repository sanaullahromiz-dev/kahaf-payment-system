from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

# পেমেন্ট অ্যাপ থেকে সব মডেল ইমপোর্ট করা হলো
from payments.models import CustomerRegistration, DirectPayment, ProjectFile, SalesReceipt, Product, Notification, ProductOrderRequest

# 👑 এডমিন ড্যাশবোর্ড লগইন ভিউ
def admin_dashboard_login(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_staff:
            return redirect('custom_admin_dashboard')
        else:
            logout(request)
            
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_superuser or user.is_staff:
                login(request, user)
                messages.success(request, "এডমিন প্যানেলে স্বাগতম!")
                return redirect('custom_admin_dashboard')
            else:
                messages.error(request, "আপনার এডমিন এক্সেস নেই!")
        else:
            messages.error(request, "ইউজারনেম অথবা পাসওয়ার্ড ভুল হয়েছে!")
            
    return render(request, 'admin_login.html')

# 👑 কাস্টম এডমিন ড্যাশবোর্ড
@login_required(login_url='admin_login')
def custom_admin_dashboard(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('admin_login')
    
    # 🛒 অর্ডার অনুরোধ সম্পন্ন/মার্ক করার অ্যাকশন
    if request.method == 'POST' and request.POST.get('resolve_order_id'):
        order_id = request.POST.get('resolve_order_id')
        order_obj = get_object_or_404(ProductOrderRequest, id=order_id)
        order_obj.is_contacted = True
        order_obj.save()
        messages.success(request, f"{order_obj.customer.name} এর অর্ডার অনুরোধটি সম্পন্ন হিসেবে চিহ্নিত করা হয়েছে!")
        return redirect('custom_admin_dashboard')

    total_customers = CustomerRegistration.objects.count()
    pending_payments = DirectPayment.objects.filter(is_verified=False).order_by('-created_at')
    total_sales = SalesReceipt.objects.count()
    received_files = ProjectFile.objects.filter(sender='customer').order_by('-created_at')
    order_requests = ProductOrderRequest.objects.filter(is_contacted=False).order_by('-created_at')
    
    context = {
        'total_customers': total_customers,
        'pending_payments': pending_payments,
        'total_sales': total_sales,
        'received_files': received_files,
        'order_requests': order_requests,
    }
    return render(request, 'admin_dashboard.html', context)

# 👑 বিক্রি রশিদ তৈরি (এডমিন)
@login_required(login_url='admin_login')
def create_sales_receipt(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('admin_login')
        
    customers = CustomerRegistration.objects.all()
    products = Product.objects.all()
    
    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        customer = get_object_or_404(CustomerRegistration, id=customer_id)
        product_id = request.POST.get('product')
        product = get_object_or_404(Product, id=product_id)
        
        SalesReceipt.objects.create(
            receipt_no=request.POST.get('receipt_no'),
            customer=customer,
            product=product,
            total_amount=request.POST.get('total_amount'),
            payment_type=request.POST.get('payment_type')
        )
        messages.success(request, "রশিদ সফলভাবে গ্রাহকের প্রোফাইলে পাঠানো হয়েছে!")
        return redirect('create_sales_receipt')
        
    return render(request, 'sales_form.html', {'customers': customers, 'products': products})

# 👑 মাস ও বছর ভিত্তিক সকল রশিদের তালিকা
@login_required(login_url='admin_login')
def receipt_list(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('admin_login')
    
    receipts = SalesReceipt.objects.all().order_by('-created_at')
    return render(request, 'receipt_list.html', {'receipts': receipts})

# 👑 নির্দিষ্ট রশিদের বিস্তারিত তথ্য দেখা
@login_required(login_url='admin_login')
def receipt_detail(request, receipt_id):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('admin_login')
        
    receipt = get_object_or_404(SalesReceipt, id=receipt_id)
    return render(request, 'receipt_detail.html', {'receipt': receipt})

# 👑 পেমেন্ট ভেরিফাই
@login_required(login_url='admin_login')
def verify_payment(request, payment_id):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('admin_login')
        
    payment = get_object_or_404(DirectPayment, id=payment_id)
    payment.is_verified = True
    payment.save()
    
    product_name = payment.product_name if payment.product_name else "প্রোডাক্ট"
    paid_amount = payment.paid_amount if payment.paid_amount else "0"
    
    notification_msg = (
        f"👉 আসসালামু আলাইকুম ওয়া রাহমাতুল্লাহ!\n"
        f"সুসংবাদ 💸 \n"
        f"আপনার {product_name} বাবদ {paid_amount}৳ টাকা পেমেন্ট আমরা রিসিভ করেছি ।\n\n"
        f"ধন্যবাদ 💝"
    )
    
    Notification.objects.create(
        customer=payment.customer, 
        message=notification_msg,
        is_read=False
    )

    messages.success(request, f"{payment.customer.name} এর পেমেন্ট ভেরিফাই সম্পন্ন হয়েছে এবং গ্রাহকের ড্যাশবোর্ডে নোটিফিকেশন পাঠানো হয়েছে!")
    return redirect('custom_admin_dashboard')

# 👑 নতুন গ্রাহক যোগ করা (এডমিন)
@login_required(login_url='admin_login')
def admin_add_customer(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('admin_login')
        
    if request.method == 'POST':
        reg_id = request.POST.get('registration_id')
        mobile = request.POST.get('mobile_number')
        
        if CustomerRegistration.objects.filter(registration_id=reg_id).exists() or CustomerRegistration.objects.filter(mobile_number=mobile).exists():
            messages.error(request, "এই আইডি বা মোবাইল নাম্বার দিয়ে আগে থেকেই একজন গ্রাহক আছেন!")
            return redirect('admin_add_customer')
            
        product_id = request.POST.get('product')
        product = Product.objects.get(id=product_id) if product_id else None
        
        CustomerRegistration.objects.create(
            registration_id=reg_id,
            name=request.POST.get('name'),
            address=request.POST.get('address'),
            mobile_number=mobile,
            product=product,
            amount=request.POST.get('amount'),
            payment_type=request.POST.get('payment_type'),
            registration_month=request.POST.get('registration_month'),
            registration_year=request.POST.get('registration_year'),
            payment_month=request.POST.get('payment_month'),
            payment_year=request.POST.get('payment_year'),
            photo=request.FILES.get('photo')
        )
        messages.success(request, "নতুন গ্রাহক সফলভাবে নিবন্ধন করা হয়েছে!")
        return redirect('custom_admin_dashboard')
        
    products = Product.objects.all()
    return render(request, 'admin_add_customer.html', {'products': products})

# 👑 গ্রাহক তালিকা (এডমিন)
@login_required(login_url='admin_login')
def admin_customer_list(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('admin_login')
    
    customers = CustomerRegistration.objects.all().order_by('-created_at')
    return render(request, 'admin_customer_list.html', {'customers': customers})

# 👑 নির্দিষ্ট গ্রাহকের প্রোফাইল (এডমিন)
@login_required(login_url='admin_login')
def admin_customer_profile(request, customer_id):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('admin_login')
        
    customer = get_object_or_404(CustomerRegistration, id=customer_id)
    receipts = SalesReceipt.objects.filter(customer=customer).order_by('-created_at')
    payments = DirectPayment.objects.filter(customer=customer).order_by('-created_at')
    files = ProjectFile.objects.filter(customer=customer).order_by('-created_at')
    
    context = {
        'customer': customer,
        'receipts': receipts,
        'payments': payments,
        'files': files,
    }
    return render(request, 'admin_customer_profile.html', context)

# 🔄 AJAX APIs
def get_receipt_data(request, receipt_no):
    try:
        receipt = SalesReceipt.objects.get(receipt_no=receipt_no)
        data = {
            'success': True,
            'customer_name': receipt.customer.name,
            'customer_id': receipt.customer.registration_id,
            'product_name': receipt.product.name if receipt.product else '',
            'total_amount': receipt.total_amount,
            'payment_type': receipt.payment_type,
        }
    except SalesReceipt.DoesNotExist:
        data = {'success': False}
    return JsonResponse(data)

def get_customer_data(request, customer_id):
    try:
        customer = CustomerRegistration.objects.get(id=customer_id)
        data = {'success': True, 'mobile': customer.mobile_number, 'reg_id': customer.registration_id}
    except:
        data = {'success': False}
    return JsonResponse(data)

# 👑 এডমিন থেকে গ্রাহককে ফাইল প্রজেক্ট পাঠানো
@login_required(login_url='admin_login')
def admin_send_file(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('admin_login')
    
    customers = CustomerRegistration.objects.all().order_by('-id')
    
    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        customer = get_object_or_404(CustomerRegistration, id=customer_id)
        title = request.POST.get('title')
        file = request.FILES.get('file')
        
        if title and file:
            ProjectFile.objects.create(
                customer=customer,
                title=title,
                file=file,
                sender='admin'
            )
            messages.success(request, f"{customer.name} এর ড্যাশবোর্ডে সফলভাবে ফাইল প্রজেক্ট পাঠানো হয়েছে!")
            return redirect('custom_admin_dashboard')
        else:
            messages.error(request, "দয়া করে ফাইলের নাম এবং ফাইল সঠিকভাবে যুক্ত করুন।")
            
    return render(request, 'admin_send_file.html', {'customers': customers})