from django.conf.urls import patterns, include, url
from mcashpos import views

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
    url(r'qr_scan/$', views.qr_scan),
)
