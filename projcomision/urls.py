
"""projcomision URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from perfiles.views import SignUpView, BienvenidaView, SignInView, SignOutView
from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
   # url(r'^charcha-serviceworker(.*.js)$', views.charcha_serviceworker, name='charcha_serviceworker'),
    path('', include('sellingsapp.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^$', BienvenidaView.as_view(), name='bienvenida'),
    url(r'^registrarse/$', SignUpView.as_view(), name='sign_up'),
    url(r'^iniciar-sesion/$', SignInView.as_view(), name='sign_in'),
    url(r'^cerrar-sesion/$', SignOutView.as_view(), name='sign_out'),
]
