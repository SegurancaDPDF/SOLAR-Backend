from django.conf.urls import url

from . import views

app_name = 'gestordocs'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'buscar/', views.buscar_documentos, name='buscar_documentos'),
    url(r'buscar_documento/', views.buscar_documento, name='buscar_documento'),
]
