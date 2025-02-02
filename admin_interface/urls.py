from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'admin_interface'

urlpatterns = [
    path('admin_login/', views.admin_login, name='admin_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register_person/', views.register_person, name='register_person'),
    path('matched_cases/', views.matched_cases, name='matched_cases'),
    path('registered_cases/', views.registered_cases, name='registered_cases'),
    path('reported_cases/', views.reported_cases, name='reported_cases'),
    path('success/', views.success, name='success'),
    path('view_case/<int:case_id>/', views.view_case, name='view_case'),  
    path('delete_case/<int:case_id>/', views.delete_case, name='delete_case'),  
    path('delete_case/<int:case_id>/<str:case_type>/', views.delete_case, name='delete_case'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
