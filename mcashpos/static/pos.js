function setFinalResult(text) {
    $('#modal .modal-body').html('<p>' + text + '</p>');
    $('#modal').find('.modal-footer').slideDown();
}
function setIntermediateResult(text) {
    $('#modal').find('.modal-body').html(
            ('<div class="progress progress-striped active">' +
                '<div class="bar" style="width: 100%">{0}</div>' +
                '</div>').format(text)
        ).end()
        .find('.modal-footer').hide().end()
        .modal('show');
}


if (!String.prototype.format) {
    String.prototype.format = function() {
        var args = arguments;
        return this.replace(/{(\d+)}/g, function(match, number) {
            return typeof args[number] != 'undefined' ? args[number] : match ;
        });
    };
}

function Pos(settings, cartId, saleManager, pusher) {
    posUrl = '{0}/merchant/{1}/pos/{2}/'.format(settings.merchantApiUrl, settings.merchantId, settings.posId);
    this.cartId = cartId;
    this.settings = settings;
    this.token = null;
    this.isReady = false;
    this.saleManager = saleManager;
    this.currency = settings.currency;
    this.additionalEdit = false;
    this.pusher = pusher;

    $.ajaxSetup({
        accepts: 'application/json',
        cache: false,
        contentType: 'application/json; charset: UTF-8',
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-Mcash-Secret', settings.mcashSecret);
            this.url = this.url + '?mcash_url=' + encodeURI(settings.merchantApiUrl);
        },
        dataType: 'json'
    });

    this.paymentRequestTries = 0
}
Pos.prototype.getPaymentRequestId = function() {
    return this.cartId + '-' + this.paymentRequestTries;
};
Pos.prototype.setToken = function(token) {
    this.token = token;
    this.checkReadyAndDoSale();
};
Pos.prototype.setSaleReady = function(isReady) {
    this.isReady = isReady === undefined ? true : isReady;
    if (this.isReady) {
        this.saleManager.setLocked();
    }
    this.checkReadyAndDoSale();
};
Pos.prototype.checkReadyAndDoSale = function() {
    if (this.isReady && this.token != null) {
        this.putPaymentRequest(
            this.token,
            this.saleManager.total(),
            this.saleManager.getSaleRequestText(),
            this.currency,
            this.additionalEdit
        )
    }
};
Pos.prototype.putPaymentRequest = function(customer, amount, text, currency, additionalEdit) {
    this.paymentRequestTries += 1;
    var tid = this.getPaymentRequestId()
    var channel = this.pusher.subscribe(this.settings.pusherChannelPrefix + 'pr-' + tid);

    setIntermediateResult('Making a payment request...');
    var pr = window.paymentRequest = new PaymentRequest(tid, {
        'customer': customer,
        'amount': amount,
        'text': text || '',
        'currency': currency,
        'additionalEdit': additionalEdit || false,
        'allowCredit': true
    }, channel);
    pr.createAndWaitForPayment();
};

function ProductListManager(productsUrl, productList, productTemplate, saleManager) {
    this.url = productsUrl;
    this.productList = productList;
    this.productTemplate = productTemplate;
    this.saleManager = saleManager;
    this.products = {};
}

ProductListManager.prototype.populateList = function() {
    var plm = this;
    this.productList.html(this.productTemplate({products: this.products}));
    $(this.productList).find('li').click(function() {
        var index = $(this).find('.thumbnail').attr('data-index');
        var product = plm.products[index];
        plm.saleManager.add(product);
    });
};
ProductListManager.prototype.update = function() {
    var plm = this;
    $.getJSON(this.url, function(data, status, jqXHR) {
        plm.products = $.map(data, function(prod) { prod.price = parseFloat(prod.price); return prod});
        plm.populateList();
    });
};

function SaleManager(display, displayTemplate, saleRequestTemplate, receiptTemplate) {
    this.display = display;
    this.displayTemplate = displayTemplate;
    this.receiptTemplate = receiptTemplate;
    this.saleRequestTemplate = saleRequestTemplate;
    this.products = [];
    this.locked = false;
    this.updateDisplay();
}

SaleManager.prototype.updateDisplay = function() {
    this.display.html(this.displayTemplate(this))
};
SaleManager.prototype.total = function() {
    sum = 0;
    $.each(this.products, function(i, prod) { sum += prod.price });
    return sum.toFixed(2);
};
SaleManager.prototype.add = function(product) {
    if (!this.locked) {
        this.products.push(product);
        this.updateDisplay();
    }
};
SaleManager.prototype.getSaleRequestText = function() {
    return this.saleRequestTemplate(this);
};
SaleManager.prototype.setLocked = function(locked) {
    this.locked = locked === undefined || locked;
};


function PaymentRequest(tid, attrs, channel) {
    this.tid = tid;
    this.channel = channel;
    this._events = {};
    this.state = null;
    this.attrs = attrs;
}

PaymentRequest.prototype.create = function(success, error) {
    var self = this;
    if (success === undefined) success = [];
    else if (success.constructor !== Array) success = [success];
    if (error == undefined) error = [];
    else if (error.constructor !== Array) error = [error];
    success.unshift(function(data, status, jqXHR) {
        self.id = data.id
        self.state = 'pending';
    });

    $.ajax({
        url: '/sale_request/{0}/'.format(self.tid),
        type: 'POST',
        data: JSON.stringify(self.attrs),
        success: success,
        error: error
    });
};

PaymentRequest.prototype.bindEvents = function(events) {
    self = this;
    $.each(events, function(event, callback) {
        self.channel.bind(event, callback);
        self._events[event] = callback;
    });
};

PaymentRequest.prototype.unbindEvents = function(events) {
    self = this;
    $.each(events, function(event, callback) {
        self.channel.unbind(event);
        delete self._events[event];
    });
};

PaymentRequest.prototype.unbindAllEvents = function() {
    if (!$.isEmptyObject(this._events)) this.unbindEvents(this._events);
};


PaymentRequest.prototype.getOutcome = function(callback) {
    var url = '/outcome/{0}/'.format(this.id);
    $.ajax({
        url: url,
        type: 'GET',
        success: callback,
        error: callback
    });
};

PaymentRequest.prototype.checkAndSetState = function(required, new_state) {
    if (this.state == new_state) return false;
    if (required.constructor !== Array) required = [required];
    var ok = false;
    for (var i in required) {
        if (required[i] == this.state) {
            ok = true;
            break;
        }
    }
    if (ok) this.state = new_state;
    return ok;
}

PaymentRequest.prototype.createAndWaitForPayment = function() {
    var self = this;
    this.create(function(data, status, jqXHR) {
        self.unbindAllEvents();
        setIntermediateResult('Waiting for payment...');
        self.bindEvents({
            payment_authorized: function(data) {
                if (!self.checkAndSetState('pending', 'auth')) return;
                setIntermediateResult('Received payment. Capturing...');
                $.ajax({
                    url: '/capture/{0}/'.format(self.id),
                    type: 'POST',
                    success: function(data, status, jqXHR) {
                    }
                });
            },
            payment_captured: function(data) {
                if (!self.checkAndSetState('auth', 'capture')) return;
                setFinalResult('Payment OK');
                self.unbindAllEvents();
                self.channel.unsubscribe();
            },
            payment_aborted_by_customer: function(data) {
                if (!self.checkAndSetState('pending', 'fail')) return;
                setFinalResult('Payment request rejected by customer');
                self.unbindAllEvents();
                self.channel.unsubscribe();
            },
            payment_aborted_by_merchant: function(data) {
                if (!self.checkAndSetState('pending', 'fail')) return;
                setFinalResult('Payment request aborted by merchant');
                self.unbindAllEvents();
                self.channel.unsubscribe();
            },
            payment_request_expired: function(data) {
                if (!self.checkAndSetState('pending', 'fail')) return;
                setFinalResult('Payment request expired');
                self.unbindAllEvents();
                self.channel.unsubscribe();
            }
        });
    });
}
