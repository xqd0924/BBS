"""BBS_2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from blog import views
from django.views.static import serve
from BBS_2 import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^register/', views.register),
    url(r'^login/', views.user_login),
    url(r'^get_code/', views.get_code),
    url(r'^index/', views.index),
    url(r'^$', views.index),
    url(r'^logout/', views.logout_s),
    url(r'^media/(?P<path>.*)', serve,{'document_root':settings.MEDIA_ROOT}),
    url(r'^diggit/', views.diggit),
    url(r'^commit/', views.commit),
    url(r'^backend/', views.backend),
    url(r'^add_article/', views.add_article),
    url(r'^upload_file/', views.upload_file),
    # 修改头像
    url(r'^update_head/', views.update_head),
    # 修改文章
    url(r'^update_article/(?P<pk>\d+)', views.update_article),
    # 获取文章
    url(r'^get_article/(?P<pk>\d+)', views.get_article),
    url(r'^(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<param>.*)', views.sitehome),
    url(r'^(?P<username>\w+)/articles/(?P<pk>\d+)', views.article_detail),
    url(r'^(?P<username>\w+)', views.sitehome),

]

