# django
from django.conf.urls import url
from django.urls import path

# application
from . import views

urlpatterns = [
    path('<uuid:uuid_atendimento>/', views.chat_com_assistido, name='chat_com_assistido'),
    url(r'^webhook/$', views.webhook, name='webhook'),
]
