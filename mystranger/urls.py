"""mystranger URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.contrib import admin
from django.conf.urls import include
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from mystranger_app.views import *
from account.views import (
    register_view,
    login_view,
    logout_view,
    account_search_view,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home' ),
    path('new_chat/', new_chat_view , name='new-chat' ),
    path('new_chat_text/', new_chat_text_view , name='new-chat-text' ),
    path('search/', account_search_view, name="search"),
    
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),

    path('account/', include('account.urls', namespace='account')),

    # Friend System
    path('friend/', include('friend.urls', namespace='friend')),

    # Public Chat App
    path('chat/', include('chat.urls', namespace='chat')),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)