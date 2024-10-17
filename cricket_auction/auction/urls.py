from django.urls import path
from .views import team_dashboard, main_dashboard
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('team/<str:url_name>/', team_dashboard, name='team_dashboard'),
    path('', main_dashboard, name='main_dashboard'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)