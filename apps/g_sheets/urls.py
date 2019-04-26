from django.conf.urls import url
from . import views		   
                 
urlpatterns = [
    url(r'^oauth2callback', views.oauth2_landing),
    url(r'^auth_g_sheets$', views.auth_g_sheets)
]

