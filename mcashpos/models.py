from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False)
    image_id = models.CharField(max_length=1025, null=True, blank=True)

    def __unicode__(self):
        return u'%s' % (self.name)


class ProductSale(models.Model):
    product = models.ForeignKey(Product)
    sale = models.ForeignKey('Sale')
    quantity = models.IntegerField(default=1)

    class Meta:
        unique_together = ('product', 'sale')

    def __unicode__(self):
        return u'%s|%s' % (self.sale, self.product)


class Sale(models.Model):
    OPEN = 0
    CANCELED = 1
    COMPLETED = 2
    STATES = (
        (OPEN, 'open'),
        (CANCELED, 'canceled'),
        (COMPLETED, 'completed'),
    )

    products = models.ManyToManyField(Product, through=ProductSale)
    status = models.IntegerField(choices=STATES, default=STATES[0][0])

    def __unicode__(self):
        return u'%s: %s' % (super(Sale, self).__unicode__(), self.pk)



