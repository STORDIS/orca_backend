from django.db import models


class ReDiscoveryConfig(models.Model):

    device_ip = models.CharField(max_length=64, primary_key=True)
    interval = models.IntegerField()
    last_discovered = models.DateTimeField(null=True)

    objects = models.Manager()


class IPRange(models.Model):
    
    range = models.CharField(max_length=64, primary_key=True)
    
    objects = models.Manager
    

class IPAvailability(models.Model):
    
    ip = models.CharField(max_length=64, primary_key=True)
    used_in = models.CharField(max_length=64, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = models.Manager
    
    
    @staticmethod
    def create_if_not_exist(ip):
        if not IPAvailability.objects.filter(ip=ip).exists():
            IPAvailability.objects.create(ip=ip)
            
    @staticmethod
    def delete_if_not_used(ip):
        data = IPAvailability.objects.filter(ip=ip).first()
        if not data.used_in:
            data.delete()