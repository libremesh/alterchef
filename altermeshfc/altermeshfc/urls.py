from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.views.static import serve

from altermeshfc.firmcreator import views
from altermeshfc.list_dir.views import list_dir

admin.autodiscover()
from django.contrib.sites.models import Site
admin.site.unregister(Site)

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^accounts/', include('registration.backends.default.urls')),

    url(r'^network/create/$', views.NetworkCreateView.as_view(), name='network-create'),
    url(r'^network/list/$', views.NetworkListView.as_view(), name='network-list'),
    url(r'^network/(?P<slug>[\w-]+)/$', views.NetworkDetailView.as_view(), name='network-detail'),
    url(r'^network/(?P<slug>[\w-]+)/edit/$', views.NetworkUpdateView.as_view(), name='network-edit'),
    url(r'^network/(?P<slug>[\w-]+)/delete/$', views.NetworkDeleteView.as_view(), name='network-delete'),

    url(r'^sshkey/create/$', views.SSHKeyCreateView.as_view(), name='sshkey-create'),
    url(r'^sshkey/list/$', views.SSHKeyListView.as_view(), name='sshkey-list'),
    url(r'^sshkey/(?P<pk>\d+)/$', views.SSHKeyDetailView.as_view(), name='sshkey-detail'),
    url(r'^sshkey/(?P<pk>\d+)/edit/$', views.SSHKeyUpdateView.as_view(), name='sshkey-edit'),
    url(r'^sshkey/(?P<pk>\d+)/delete/$', views.SSHKeyDeleteView.as_view(), name='sshkey-delete'),

    url(r'^fwprofile/create/$', views.create_profile_simple, name="fwprofile-create-simple"),
    url(r'^fwprofile/create-advanced/$', views.crud_profile_advanced, name="fwprofile-create-advanced"),
    url(r'^fwprofile/(?P<slug>[\w-]+)/edit/$', views.crud_profile_advanced,
        name="fwprofile-edit-advanced"),
    url(r'^fwprofile/(?P<slug>[\w-]+)/$', views.FwProfileDetailView.as_view(), name='fwprofile-detail'),
    url(r'^fwprofile/(?P<slug>[\w-]+)/delete/$', views.FwProfileDeleteView.as_view(), name='fwprofile-delete'),

    url(r'^fwjob/list/$', views.view_jobs, name="view-jobs"),
    url(r'^fwjob/(?P<pk>\d+)/$', views.FwJobDetailView.as_view(), name='fwjob-detail'),

    url(r'^diff/(?P<src_profile>[\w-]+)/(?P<dest_profile>[\w-]+)/$', views.diff, name='fwprofile-diff'),

    url(r'^cook/(?P<slug>[\w-]+)/$', views.cook, name='cook'),

    url(r'^ls/(?P<path>.*)$', list_dir, name="list-dir"),

    url(r'^admin/', include(admin.site.urls)),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]
