from django.conf.urls import patterns, url

from main import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^upload/', views.upload, name='upload'),
#   url(r'^gen/', views.gen, name='gen'),
)
