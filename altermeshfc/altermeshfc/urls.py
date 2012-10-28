from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'altermeshfc.firmcreator.views.index', name="index"),
    url(r'^profile/create/$', 'altermeshfc.firmcreator.views.crud_profile',
        name="crud_profile"),

    # url(r'^admin/', include(admin.site.urls)),
)
