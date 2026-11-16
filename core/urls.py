from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ডিফল্ট জ্যাঙ্গো এডমিন (নিরাপত্তার জন্য নাম পরিবর্তন করা হলো)
    path('django-admin/', admin.site.urls), 
    
    # গ্রাহকদের রাউট (ডোমেইনের মূল ঠিকানায় থাকবে)
    path('', include('payments.urls')), 
    
    # আপনার কাস্টম এডমিন রাউট (সবগুলো admin-panel/ দিয়ে শুরু হবে)
    path('admin-panel/', include('admin_dashboard.urls')),
]

# প্রোডাকশন এবং ডেভেলপমেন্টে মিডিয়া ফাইলগুলো সঠিকভাবে দেখানোর জন্য
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)