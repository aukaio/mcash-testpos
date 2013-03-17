from django.shortcuts import render_to_response
from mcashpos.models import Product
from mcashpos.models import ProductSale
from mcashpos.models import Sale
from django.template import RequestContext
from django.conf import settings

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