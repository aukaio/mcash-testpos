if (!String.prototype.format) {
    String.prototype.format = function() {
        var args = arguments;
        return this.replace(/{(\d+)}/g, function(match, number) {
            return typeof args[number] != 'undefined' ? args[number] : match ;
        });
    };
}

function Pos(settings, cartId, saleManager) {
    posUrl = '{0}/merchant/{1}/pos/{2}/'.format(settings.merchantApiUrl, settings.merchantId, settings.posId);
    this.cartId = cartId;
    this.settings = settings;
    this.token = null;
    this.saleReady = false;
    this.saleManager = saleManager;
    this.additionalEdit = false;

    $.ajaxSetup({
        accepts: 'application/json',
        cache: false,
        contentType: 'application/json; charset: UTF-8',
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-Mcash-Secret', settings.mcashSecret);
        },
        dataType: 'json'
    });

    this.paymentRequestTries = 0
}
Pos.prototype.getPaymentRequestId = function() {
    return this.cartId + '-' + this.paymentRequestTries;
}
Pos.prototype.setToken = function(token) {
    this.token = token;
    this.checkReadyAndDoSale();
}
Pos.prototype.setSaleReady = function(isReady) {
    this.isReady = isReady === undefined ? true : isReady;
    this.checkReadyAndDoSale();
}
Pos.prototype.checkReadyAndDoSale = function() {
    if (this.isReady && this.token != null) {
        this.putPaymentRequest(
            this.token,
            this.saleManager.total(),
            this.saleManager.getSaleRequestText(),
            this.additionalEdit
        )
    }
}
Pos.prototype.putPaymentRequest = function(customer, amount, text, additionalEdit) {
       this.paymentRequestTries += 1
       var pr = {
            'customer': customer,
            'amount': amount,
            'text': text || '',
            'currency': 'NOK',
            'additionalEdit': additionalEdit || false,
            'allowCredit': true,
            'posTimestamp': new Date().toUTCString('yyyy-MM-dd HH:mm:ss')
       }
        $.ajax({
            url: '/sale_request/{0}/'.format(this.getPaymentRequestId()),
            type: 'POST',
            data: JSON.stringify(pr),
            success: function(data, status, jqXHR) {
                window.paymentRequest = new PaymentRequest(data);
                $('#modal').find('.modal-body').html(
                    '<div class="progress progress-striped active"><div class="bar" style="width: 100%">Waiting for payment</div></div>'
                ).end()
                    .find('.modal-footer').hide().end()
                    .modal('show');
                function callback(data, status, jqXHR) {
                    if (status == 'success') {
                        if (data.status != 'pending') {
                            if (data.status == 'ok') text = 'Payment OK';
                            else text = 'Payment request rejected';
                            $('#modal .modal-body').html('<p>' + text + '</p>');
                            $('#modal').find('.modal-footer').slideDown();
                            return;
                        }
                    }
                    setTimeout(function () {paymentRequest.getOutcome(callback)}, 500);
                }
                paymentRequest.getOutcome(callback);
            }
        });
    }

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
}
ProductListManager.prototype.update = function() {
    var plm = this;
    $.getJSON(this.url, function(data, status, jqXHR) {
        plm.products = $.map(data, function(prod) { prod.price = parseFloat(prod.price); return prod});
        plm.populateList();
    });
}

function SaleManager(display, displayTemplate, saleRequestTemplate, receiptTemplate) {
    this.display = display;
    this.displayTemplate = displayTemplate;
    this.receiptTemplate = receiptTemplate;
    this.saleRequestTemplate = saleRequestTemplate;
    this.products = [];
    this.updateDisplay();
}

SaleManager.prototype.updateDisplay = function() {
    this.display.html(this.displayTemplate(this))
}
SaleManager.prototype.total = function() {
    sum = 0;
    $.each(this.products, function(i, prod) { sum += prod.price });
    return sum.toFixed(2);
}
SaleManager.prototype.add = function(product) {
    this.products.push(product);
    this.updateDisplay();
}
SaleManager.prototype.getSaleRequestText = function() {
    return this.saleRequestTemplate(this);
}

function PaymentRequest(attrs) {
    attrs.getOutcome = function(callback) {
        url = '/outcome/{0}/'.format(this.id)
        $.ajax({
            url: url,
            type: 'GET',
            success: callback,
            error: callback
        })
    }
    return attrs;
}