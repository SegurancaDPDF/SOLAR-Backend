from django.conf.urls import url, include, re_path
# definindo as URLs (rotas) para um aplicativo Django
urlpatterns = [
    re_path(r'v1/', include(('api.api_v1.urls', 'api_v1'), namespace='v1')),
    re_path(r'v2/', include(('api.api_v2.urls', 'api_v2'), namespace='v2')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
