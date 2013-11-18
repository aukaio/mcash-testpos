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
    user_id = None

    def __init__(self):
        super(POS, self).__init__()
        self.request_opener = urllib2.build_opener(urllib2.HTTPSHandler)

    def get_pos_url(self):
        return self.api_url

    def get_headers(self):
        return {
            'Authorization': 'SECRET ' + self.secret,
            'Accept': 'application/vnd.mcash.api.merchant.v1+json',
            'X-Mcash-Merchant': self.merchant_id,
            'X-Mcash-User': self.user_id,
            'Content-Type': 'application/json',
        }

    def do_request(self, url, data=None, method='GET', extra_headers={}):
        headers = self.get_headers()
        headers.update(extra_headers)
        request = Request(self.api_url + url, data, method, headers)
        res = self.request_opener.open(request)
        try:
            return json.load(res)
        except ValueError:
            return None

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
            pos_tid,
            amount,
            text,
            additional_amount,
            currency,
            additional_edit,
            allow_credit,
        )
        print data
        url = '/payment_request/'
        return self.do_request(url, data, 'POST')

    def get_outcome(self, pos_tid):
        url = '/payment_request/%s/outcome/' % pos_tid
        return self.do_request(url)

    def build_payment_request_data(
            self,
            customer,
            pos_tid,
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
            'additional_amount': additional_amount,
            'currency': currency,
            'additional_edit': additional_edit,
            'allow_credit': allow_credit,
            'pos_tid': pos_tid,
            'pos_id': self.pos_id,
            'action': 'sale',
            'callback_uri': 'pusher:m-%s-pr-%s' % (self.merchant_id, pos_tid)
        }
        return json.dumps(pr)

    def capture_payment_request(self, tid):
        data = {'action': 'capture'}
        url = '/payment_request/{}/'.format(tid)
        return self.do_request(url, json.dumps(data), 'PUT')





