from django.conf.urls import patterns, include, url

from altermeshfc.firmcreator.views import NetworkCreateView, NetworkDetailView, NetworkListView, \
                                           NetworkUpdateView, NetworkDeleteView, FwProfileDetailView

urlpatterns = patterns('',
    url(r'^$', 'altermeshfc.firmcreator.views.index', name="index"),
    (r'^accounts/', include('registration.backends.default.urls')),

    url(r'^network/create/$', NetworkCreateView.as_view(), name= 'network-create'),
    url(r'^network/list/$', NetworkListView.as_view(), name= 'network-list'),
    url(r'^network/(?P<slug>[\w-]+)/$', NetworkDetailView.as_view(), name= 'network-detail'),
    url(r'^network/(?P<slug>[\w-]+)/edit/$', NetworkUpdateView.as_view(), name= 'network-edit'),
    url(r'^network/(?P<slug>[\w-]+)/delete/$', NetworkDeleteView.as_view(), name= 'network-delete'),

    url(r'^fwprofile/create/$', 'altermeshfc.firmcreator.views.create_profile_simple',
        name="fwprofile-create-simple"),
    url(r'^fwprofile/create-advanced/$', 'altermeshfc.firmcreator.views.create_profile_advanced',
        name="fwprofile-create-advanced"),
    #url(r'^fwprofile/(?P<slug>[\w-]+)/edit/$', ProfileUpdateView.as_view(), name= 'fwprofile-edit'),
    url(r'^fwprofile/(?P<slug>[\w-]+)/$', FwProfileDetailView.as_view(), name= 'fwprofile-detail'),


    # url(r'^admin/', include(admin.site.urls)),
)
