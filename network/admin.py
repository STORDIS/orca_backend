from django.contrib import admin

from django.contrib import admin

class OrcaDeviceAdmin(admin.ModelAdmin):
    list_display = ('img_name', 'mgt_intf', 'mgt_ip','hwsku')

# Register your models here.
