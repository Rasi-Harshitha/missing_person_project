from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('user/login/', views.user_login, name='user_login'),  # User login
    path('user/report/', views.report_missing_person, name='report_missing_person'),  # Report missing
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
