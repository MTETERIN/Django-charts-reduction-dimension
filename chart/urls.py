from django.conf.urls import url
 
from . import views
 
app_name = 'chart'
urlpatterns = [
    url(r'^contact/$', views.feedback_form, name='feedback_form'),
]