if (!String.prototype.format) {
    String.prototype.format = function() {
        var args = arguments;
        return this.replace(/{(\d+)}/g, function(match, number) {
            return typeof args[number] != 'undefined' ? args[number] : match ;
        });
    };
}

function Pos(settings, cartId) {
    posUrl = '{0}/merchant/{1}/pos/{2}/'.format(settings.merchantApiUrl, settings.merchantId, settings.posId);
    this.cartId = cartId;
    this.settings = settings;
    this.pusher = new Pusher(posSettings.pusherAppKey);
    this.pusher.subscribe(cartId);

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
    this.getPaymentRequestId = function() {
        return this.cartId + '-' + this.paymentRequestTries;
    }
    this.putPaymentRequest = function(customer, amount, text, additionalEdit) {
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
                $('#waitmodal').modal('show');
                function callback(data, status, jqXHR) {
                    if (status == 'success') {
                        if (data.status != 'pending') {
                            $('#waitmodal').modal('hide');
                            return;
                        }
                    }
                    setTimeout(function () {paymentRequest.getOutcome(callback)}, 500);
                }
                paymentRequest.getOutcome(callback);
            }
        });
    }
    var putPaymentRequest = this.putPaymentRequest;
    this.pusher.bind('qr-scan', function(data) {
        var img = $('#qr-image');
        var innerContainer = $('#qr-container-inner');
        innerContainer.height(img.height()).width(img.width());
        img.parent().slideUp(200, function() {
            $('#qr-status').html('QR scanned: ' + data.token).fadeIn('fast');
        });
        putPaymentRequest(data.token, '10.00', 'Hello world');
    });
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