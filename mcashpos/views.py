import json
from django.shortcuts import render_to_response
from mcashpos.models import Product
from mcashpos.models import ProductSale
from mcashpos.models import Sale
from django.template import RequestContext
from django.conf import settings
from django.http import HttpResponseNotAllowed
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import pusher

def main(request):
    products = Product.objects.all()
    return render_to_response(
        'main.html',
        RequestContext(
            request,
            {
                'products': products,
                'MCASH_SERVER': settings.MCASH_SERVER,
                'SHORTLINK_ID': settings.SHORTLINK_ID,
            }
        )
    )


@csrf_exempt
def qr_scan(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    data = json.loads(request.body)
    p = pusher.Pusher()
    p[data['argstring']].trigger('qr-scan', {'token': data['id']})
    return HttpResponse(json.dumps({'text':'OK'}))


