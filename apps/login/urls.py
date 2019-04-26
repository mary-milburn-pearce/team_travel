from django.conf.urls import url
from . import views		   
                 
urlpatterns = [
    url(r'^$', views.index),
    url(r'^register$', views.register),
    url(r'^login/google$', views.login_google),
    url(r'^signincallback$', views.signin_callback),
    url(r'^login$', views.login),
    url(r'^logout$', views.logout),
]