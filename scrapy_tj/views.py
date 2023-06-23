import json
from django.http import JsonResponse
from .service_tjam import consulta_tjam
from django.contrib.auth.decorators import login_required


@login_required
def consultar_processo_tjam(request):
    if request.method == 'POST':
        requisicao = json.loads(request.body)      # converte json para python
        numero_do_processo = requisicao['numeroDoProcesso']

        return JsonResponse(consulta_tjam(numero_do_processo), safe=False)
    else:
        return 'index'
