"""bbs URL Configuration

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
from django.views.static import serve

from app01 import views
from bbs import settings

urlpatterns = [
    url(r'^$',views.home),
    url(r'^admin/', admin.site.urls),
    # Signup
    url(r'^register/', views.register, name='register'),
    # Login
    url(r'^login/', views.login, name='login'),
    # Logout
    url(r'^logout/', views.logout, name='logout'),
    # Interface for get auth code:
    url(r'^get_auth_code/', views.get_auth_code, name='auth_code'),
    # Homepage
    url(r'^home/', views.home, name='home'),
    # Media Folder exposure
    url(r'^media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}),
    # comment
    url(r'^comment/',views.comment),
    # delete comment
    url(r'^del/comment/',views.del_comment),
    # Like
    url(r'^like/', views.like),
    # Individual Users Blog Site
    url(r'^blog/(?P<username>((?!/)[\w\W])+)/$', views.blog),
    # Refresh Site by using different filter and reuse the previous view function
    url(r'^blog/(?P<username>([\w\W])+)/(?P<filterby>tag|category|archive)/(?P<param>.*)/', views.blog),
    # Article Display
    url(r'^blog/(?P<username>([\w\W])+)/article/(?P<article_pk>\d+)/', views.article)
]
