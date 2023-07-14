from django.utils.deprecation import MiddlewareMixin
class ComarcaMiddleware(MiddlewareMixin):
    """
    Middleware que adiciona comarca a sessao, se nao houver valor
    """

    # def __init__(self, get_response):
    #     self.get_response = get_response
        
    # def __call__(self, request):
    #     return self.get_response(request)
    
    def process_request(self, request):
        if request.user.is_authenticated:
            if not request.session.get('comarca', False):
                request.session['comarca'] = request.user.servidor.comarca.id
