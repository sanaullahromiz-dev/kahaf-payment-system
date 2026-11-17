from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import CustomerRegistration, DirectPayment, ProjectFile, SalesReceipt, Product, Notification, ProductOrderRequest

# 👤 গ্রাহক লগইন সিস্টেম
def customer_login(request):
    if request.user.is_authenticated: 
        if request.user.is_superuser or request.user.is_staff:
            return redirect('custom_admin_dashboard')
        return redirect('dashboard')
        
    if request.method == 'POST':
        mobile = request.POST.get('mobile_number')
        password = request.POST.get('password')
        
        user = authenticate(request, username=mobile, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser or user.is_staff:
                return redirect('custom_admin_dashboard')
            return redirect('dashboard')
        else:
            messages.error(request, "মোবাইল নাম্বার অথবা পাসওয়ার্ড ভুল হয়েছে!")
            
    return render(request, 'login.html')

# 👤 গ্রাহক রেজিস্ট্রেশন
def customer_register(request):
    if request.method == 'POST':
        reg_id = request.POST.get('registration_id')
        mobile = request.POST.get('mobile_number')
        password = request.POST.get('password')
        
        if password != request.POST.get('confirm_password'):
            messages.error(request, "পাসওয়ার্ড মিলেনি!")
            return redirect('register')
            
        profile = CustomerRegistration.objects.filter(registration_id=reg_id, mobile_number=mobile).first()
        if not profile:
            messages.error(request, "নিবন্ধন তথ্য পাওয়া যায়নি!")
            return redirect('register')
            
        if profile.user:
            messages.warning(request, "একাউন্ট আগেই তৈরি করা আছে!")
            return redirect('login')
            
        user = User.objects.create_user(username=mobile, password=password)
        profile.user = user
        profile.save()
        messages.success(request, "একাউন্ট সফলভাবে তৈরি হয়েছে!")
        return redirect('login')
        
    return render(request, 'register.html')

# 🚪 গ্রাহক লগআউট
def customer_logout(request):
    is_admin = request.user.is_superuser or request.user.is_staff
    logout(request)
    messages.info(request, "আপনি সফলভাবে লগআউট হয়েছেন।")
    if is_admin:
        return redirect('admin_login')
    return redirect('login')

# 👤 গ্রাহকের ড্যাশবোর্ড
@login_required(login_url='login')
def profile_dashboard(request):
    if request.user.is_superuser or request.user.is_staff:
        return redirect('custom_admin_dashboard')
        
    profile = CustomerRegistration.objects.filter(user=request.user).first()
    if not profile:
        messages.error(request, "প্রোফাইল তথ্য পাওয়া যায়নি।")
        return redirect('logout')
    
    # 🛒 ১. নতুন প্রোডাক্ট অর্ডার অনুরোধ সাবমিট
    if request.method == 'POST' and request.POST.get('place_order'):
        selected_product = request.POST.get('selected_product')
        if selected_product:
            ProductOrderRequest.objects.create(
                customer=profile,
                product_name=selected_product
            )
            messages.success(request, f"আপনার '{selected_product}' অর্ডারের অনুরোধ সফলভাবে এডমিনের কাছে পাঠানো হয়েছে! শীঘ্রই আপনার সাথে যোগাযোগ করা হবে।")
            return redirect('dashboard')

    # 📁 ২. ফাইল আপলোড সাবমিট
    if request.method == 'POST' and request.POST.get('upload_file'):
        title = request.POST.get('title')
        file = request.FILES.get('file')
        if title and file:
            ProjectFile.objects.create(
                customer=profile,
                title=title,
                file=file,
                sender='customer'
            )
            messages.success(request, "আপনার ফাইলটি সফলভাবে এডমিনের কাছে পাঠানো হয়েছে!")
            return redirect('dashboard')
    
    receipts = SalesReceipt.objects.filter(customer=profile).order_by('-created_at')
    dues = []
    has_new_receipt = False
    
    for receipt in receipts:
        paid = DirectPayment.objects.filter(receipt_no=receipt.receipt_no, is_verified=True).aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0
        due_amount = receipt.total_amount - paid
        if due_amount > 0:
            dues.append({
                'product': receipt.product.name if receipt.product else 'সার্ভিস',
                'type': receipt.payment_type,
                'due': due_amount
            })
            has_new_receipt = True

    customer_files = ProjectFile.objects.filter(customer=profile).order_by('-created_at')
    notifications = Notification.objects.filter(customer=profile).order_by('-created_at')[:10]

    context = {
        'profile': profile,
        'receipts': receipts,
        'dues': dues,
        'has_new_receipt': has_new_receipt or any(not n.is_read for n in notifications),
        'notifications': notifications,
        'customer_files': customer_files,
    }
    return render(request, 'profile.html', context)

# 👤 গ্রাহকের পেমেন্ট পেজ
@login_required(login_url='login')
def make_payment(request):
    if request.user.is_superuser or request.user.is_staff:
        return redirect('custom_admin_dashboard')
        
    profile = CustomerRegistration.objects.filter(user=request.user).first()
    if request.method == 'POST':
        DirectPayment.objects.create(
            customer=profile,
            receipt_no=request.POST.get('receipt_no'),
            product_name=request.POST.get('product_name'),
            payment_method=request.POST.get('payment_method'),
            transaction_id=request.POST.get('transaction_id'),
            total_amount=request.POST.get('total_amount'),
            paid_amount=request.POST.get('paid_amount'),
            payment_type=request.POST.get('payment_type')
        )
        messages.success(request, "পেমেন্ট সফলভাবে জমা হয়েছে!")
        return redirect('dashboard')
    return render(request, 'payment.html', {'profile': profile})