from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings

from altermeshfc.firmcreator.views import NetworkCreateView, NetworkDetailView, NetworkListView, \
                                           NetworkUpdateView, NetworkDeleteView, FwProfileDetailView, \
                                           FwProfileDeleteView, FwJobDetailView, SSHKeyCreateView, \
                                           SSHKeyListView, SSHKeyDetailView, SSHKeyUpdateView, SSHKeyDeleteView \

admin.autodiscover()
from django.contrib.sites.models import Site
admin.site.unregister(Site)

urlpatterns = patterns('',
    url(r'^$', 'altermeshfc.firmcreator.views.index', name="index"),
    (r'^accounts/', include('registration.backends.default.urls')),

    url(r'^network/create/$', NetworkCreateView.as_view(), name='network-create'),
    url(r'^network/list/$', NetworkListView.as_view(), name='network-list'),
    url(r'^network/(?P<slug>[\w-]+)/$', NetworkDetailView.as_view(), name='network-detail'),
    url(r'^network/(?P<slug>[\w-]+)/edit/$', NetworkUpdateView.as_view(), name='network-edit'),
    url(r'^network/(?P<slug>[\w-]+)/delete/$', NetworkDeleteView.as_view(), name='network-delete'),

    url(r'^sshkey/create/$', SSHKeyCreateView.as_view(), name='sshkey-create'),
    url(r'^sshkey/list/$', SSHKeyListView.as_view(), name='sshkey-list'),
    url(r'^sshkey/(?P<pk>\d+)/$', SSHKeyDetailView.as_view(), name='sshkey-detail'),
    url(r'^sshkey/(?P<pk>\d+)/edit/$', SSHKeyUpdateView.as_view(), name='sshkey-edit'),
    url(r'^sshkey/(?P<pk>\d+)/delete/$', SSHKeyDeleteView.as_view(), name='sshkey-delete'),

    url(r'^fwprofile/create/$', 'altermeshfc.firmcreator.views.create_profile_simple',
        name="fwprofile-create-simple"),
    url(r'^fwprofile/create-advanced/$', 'altermeshfc.firmcreator.views.crud_profile_advanced',
        name="fwprofile-create-advanced"),
    url(r'^fwprofile/(?P<slug>[\w-]+)/edit/$', 'altermeshfc.firmcreator.views.crud_profile_advanced',
        name="fwprofile-edit-advanced"),
    url(r'^fwprofile/(?P<slug>[\w-]+)/$', FwProfileDetailView.as_view(), name='fwprofile-detail'),
    url(r'^fwprofile/(?P<slug>[\w-]+)/delete/$', FwProfileDeleteView.as_view(), name='fwprofile-delete'),

    url(r'^fwjob/list/$', 'altermeshfc.firmcreator.views.view_jobs', name="view-jobs"),
    url(r'^fwjob/(?P<pk>\d+)/$', FwJobDetailView.as_view(), name='fwjob-detail'),

    url(r'^diff/(?P<src_profile>[\w-]+)/(?P<dest_profile>[\w-]+)/$', 'altermeshfc.firmcreator.views.diff', name='fwprofile-diff'),


    url(r'^cook/(?P<slug>[\w-]+)/$', 'altermeshfc.firmcreator.views.cook', name='cook'),

    url(r'^ls/(?P<path>.*)$', 'altermeshfc.list_dir.views.list_dir', name="list-dir"),

    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    )
