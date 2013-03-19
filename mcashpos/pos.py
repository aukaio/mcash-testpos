import urllib2
import json
from datetime import datetime


class Request(urllib2.Request):
    def __init__(self, url, data=None, method=None, headers={}, origin_req_host=None, unverifiable=False):
        self.method = method
        urllib2.Request.__init__(self, url, data, headers, origin_req_host, unverifiable)

    def get_method(self):
        if self.method is None:
            return super(Request, self).get_method()
        return self.method


class POS(object):
    api_url = None
    pos_id = None
    merchant_id = None
    secret = None

    def __init__(self):
        super(POS, self).__init__()
        self.request_opener = urllib2.build_opener(urllib2.HTTPSHandler)

    def get_pos_url(self):
        return self.api_url.rstrip('/') + '/merchant/%s/pos/%s/' % (self.merchant_id, self.pos_id)

    def get_headers(self):
        return {
            'X-Mcash-Secret': self.secret,
            'Content-Type': 'application/json',
        }

    def do_request(self, url, data=None, method=None, extra_headers={}):
        headers = self.get_headers()
        headers.update(extra_headers)
        request = Request(self.get_pos_url() + url, data, method, headers)
        res = self.request_opener.open(request)
        return json.load(res)

    def put_payment_request(
            self,
            pos_tid,
            customer,
            amount,
            text,
            additional_amount='0.00',
            currency='NOK',
            additional_edit=False,
            allow_credit=True,
    ):
        data = self.build_payment_request_data(
            customer,
            amount,
            text,
            additional_amount,
            currency,
            additional_edit,
            allow_credit,
        )
        print data
        url = 'sale_request/%s/' % pos_tid
        return self.do_request(url, data, 'PUT')

    def build_payment_request_data(
            self,
            customer,
            amount,
            text,
            additional_amount='0.00',
            currency='NOK',
            additional_edit=False,
            allow_credit=True,
    ):
        pr = {
            'customer': customer,
            'amount': amount,
            'text': text,
            'additionalAmount': additional_amount,
            'currency': currency,
            'additionalEdit': additional_edit,
            'allowCredit': allow_credit,
            'posTimestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        }
        return json.dumps(pr)





