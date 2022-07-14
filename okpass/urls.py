"""okpass URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
# from django.contrib import admin
from django.urls import path
from api import captcha
from api import user
from api import password

urlpatterns = [
    #    path('admin/', admin.site.urls),
    path('api/register-captcha', captcha.RegisterCaptchaAPIView.as_view()),
    path('api/register', user.RegisterAPIView.as_view()),
    path('api/captcha', captcha.CaptchaAPIView.as_view()),
    path('api/login', user.LoginAPIView.as_view()),
    path('api/passwd', user.PasswdAPIView.as_view()),
    path('api/password', password.PasswordAPIView.as_view()),
    path('api/allpassword', password.AllPasswordAPIView.as_view()),
]
