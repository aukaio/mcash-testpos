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


def main(request):
    products = Product.objects.all()
    resp = render_to_response(
        'main.html',
        RequestContext(
            request,
            {
                'products': products,
                'pos_settings': settings.POS_SETTINGS,
                'cart_id': base64.urlsafe_b64encode(uuid.uuid4().bytes).replace('=', ''),
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
    p[data['argstring']].trigger('qr-scan', {'token': data['id']})

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


def get_outcome(request, tid):
    pos = POS()
    return HttpResponse(json.dumps(pos.get_outcome(tid)), content_type='application/json')
