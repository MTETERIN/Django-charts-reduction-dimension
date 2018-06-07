"""charts URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from django.contrib.auth import views as authviews

from .views import (BarChartView, Boosting, BoostingGradientView, ChartData,
                    HomeView, StatCharView, get_data,main,manual)

urlpatterns = [
    url(r'^$', main, ),
    url(r'^tsne/$', get_data, name='tsne'),
    url(r'^api/chart/$', HomeView.as_view(), name='api-data'),
    url(r'^api/chart/data/$', ChartData.as_view()),
    url(r'^api/boosting/data$', Boosting.as_view()),
    url(r'^boosting$', BoostingGradientView.as_view(), name='boosting'),
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', authviews.login,
        {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', authviews.logout,
        {'template_name': 'logged_out.html'}, name='logout'),
    url(r'^stat/$', StatCharView.as_view(), name='stat'),
    url(r'^bar/$', BarChartView.as_view(), name='bar'),
    url(r'^manual/$', manual, name='manual'),
    url(r'^', include('chart.urls')),


]
