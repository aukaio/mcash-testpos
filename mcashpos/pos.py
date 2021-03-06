import urllib2
import json
from datetime import datetime
import logging
import requests


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
    testbed_token = None

    def __init__(self, api_url):
        super(POS, self).__init__()
        if api_url is not None:
            self.api_url = api_url
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
            'X-Testbed-Token': self.testbed_token or ''
        }

    def do_request(self, url, data=None, method='GET', extra_headers={}):
        headers = self.get_headers()
        headers.update(extra_headers)
        logging.error('URL is {}{}'.format(self.api_url, url))
        res = requests.request(method, self.api_url + url, headers=headers, data=data)
        try:
            return res.json()
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

    def put_ticket(self, pos_tid, ticket_value):
        ticket = {
            "caption": "Please display this code at the register",
            "date_expires": "2020-10-10 12:30:34",
            "kind": "valuecode",
            "code": {"type": "string", "data": ticket_value}
        }
        return self.do_request('/payment_request/%s/ticket/' % pos_tid, json.dumps({'tickets': [ticket]}), 'PUT')

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





