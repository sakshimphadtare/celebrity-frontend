from django.contrib import admin
from django.urls import path
from core.views import home, detect_celebrity

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('detect/', detect_celebrity),
]