from django.db import models


class Logs(models.Model):
    """
    Model to create log data base
    """
    timestamp = models.CharField(max_length=64)
    request_json = models.JSONField()
    status = models.CharField(max_length=32)
    processing_time = models.CharField(max_length=32)
    status_code = models.IntegerField()
    response = models.JSONField()
    http_method = models.CharField(max_length=32, default='')
    http_path = models.CharField(max_length=64)

    objects = models.Manager()
