from django.conf.urls import patterns, include, url
from mcashpos import views
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mcashpos.views.home', name='home'),
    # url(r'^mcashpos/', include('mcashpos.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.main),
    url(r'^qr[_-]scan/$', views.qr_scan),
    url(r'ad_order_scan/$', views.ad_order_scan),
    url(r'^products/$', views.list_products),
    url(r'^sale_request/(?P<tid>[\w_-]+)/$', views.sale_request),
    url(r'^capture/(?P<tid>[\w_-]+)/$', views.capture),
    url(r'^outcome/(?P<tid>[\w_-]+)/$', views.get_outcome),
)


if getattr(settings, 'SERVE_STATIC', False):
    urlpatterns += patterns(
        '',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    )
