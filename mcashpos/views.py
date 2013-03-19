import base64
import json
import pusher
import uuid
from django.shortcuts import render_to_response
from mcashpos.models import Product
from mcashpos.models import ProductSale
from mcashpos.models import Sale
from django.template import RequestContext
from django.conf import settings
from django.http import HttpResponseNotAllowed
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from mcashpos.pos import POS

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
                'cart_id': base64.urlsafe_b64encode(uuid.uuid4().bytes).replace('=', ''),
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

    pos = POS()
    pos.put_payment_request(
        data['argstring'],
        data['token'],
        '10.0',
        'Hello world',
    )
    return HttpResponse(json.dumps({'text':'OK'}))


