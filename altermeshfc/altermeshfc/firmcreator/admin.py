from django.contrib import admin
from models import Network, FwProfile

class NetworkAdmin(admin.ModelAdmin):
    list_display = ('name', 'web')

class FwProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'network', 'based_on', 'creation_date')
    list_filter = ('based_on',)

admin.site.register(Network, NetworkAdmin)
admin.site.register(FwProfile, FwProfileAdmin)
