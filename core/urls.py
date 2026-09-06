from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/', include('apps.teachers.urls')),
    path('api/', include('apps.students.urls')),
    path('api/', include('apps.homeworks.urls')),    
    path('api/', include('apps.attendance.urls')),    
    path('api/', include('apps.payments.urls')),    
]
