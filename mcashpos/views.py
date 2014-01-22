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
from mcashpos.models import Product
from mcashpos.serializers import Serializer


def _gen_tid(n):
    import string
    from Crypto.Random.random import choice
    cs = string.ascii_letters + string.digits
    return ''.join(choice(cs) for _ in range(n))

def main(request):
    products = Product.objects.all()
    resp = render_to_response(
        'main.html',
        RequestContext(
            request,
            {
                'products': products,
                'pos_settings': settings.POS_SETTINGS,
                'cart_id': _gen_tid(10),
            }
        )
    )
    resp['Access-Control-Allow-Headers'] = '*'
    return resp


@csrf_exempt
def qr_scan(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    data = json.loads(request.body)
    p = pusher.Pusher()
    data = data['object']
    p[data['argstring']].trigger('qr-scan', {'token': data['id']})

    return HttpResponse(json.dumps({'text':'OK'}))


@csrf_exempt
def ad_order_scan(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    data = json.loads(request.body)['object']
    text = 'Nintendo Wii U Premium'
    pos = POS()
    pos.put_payment_request(
        'ao-%s' % base64.urlsafe_b64encode(uuid.uuid4().get_bytes()).replace('=',''),
        data['id'],
        '299.00',
        text,
        additional_edit=False
    )
    return HttpResponse(json.dumps({'text':'OK'}))


def list_products(request):
    return HttpResponse(Serializer().serialize(Product.objects.all()), content_type='application/json')


@csrf_exempt
def sale_request(request, tid):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    data = json.loads(request.body)
    data['tid'] = tid
    pos = POS()
    return HttpResponse(
        json.dumps(pos.put_payment_request(
            tid,
            data['customer'],
            data['amount'],
            data.get('text', ''),
            additional_edit=data.get('additionalEdit', False)
        ))
    )


@csrf_exempt
def capture(request, tid):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    pos = POS()
    pos.capture_payment_request(tid)
    return HttpResponse(status=204)


def get_outcome(request, tid):
    pos = POS()
    return HttpResponse(json.dumps(pos.get_outcome(tid)), content_type='application/json')
