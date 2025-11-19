"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from config import settings
from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve

from django.conf.urls.static import static
from movies.views import movies_list, movie_detail, check_subscription_view, send_movie

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('check-subscription/', check_subscription_view, name='check-subscription'),
    # path('send-movie/', send_movie, name='send-movie'),
    # path('<slug:slug>/', movie_detail, name='movie-detail'),
    # path("", movies_list, name='movies-list'),
    
    re_path(r"static/(?P<path>.*)", serve, {"document_root": settings.STATIC_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)