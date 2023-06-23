from django.conf.urls import url
from .views import consultar_processo_tjam

urlpatterns = [
    url('consultar_tjam/', consultar_processo_tjam, name='consultar_tjam'),
]
