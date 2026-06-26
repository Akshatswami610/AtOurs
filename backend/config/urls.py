from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import home

urlpatterns = [
    path('admin/', admin.site.urls),

    #frontend pages
    path('', home, name='home'),
    path('home', home, name='home'),

]
