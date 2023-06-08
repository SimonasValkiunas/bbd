from django.db import models
from django.db.models import JSONField

class Request(models.Model):
    successful_request = models.IntegerField(null=True)
    error_request = models.IntegerField(null=True)
    successful_invocation = models.IntegerField(null=True)
    failed_invocation = models.IntegerField(null=True)
    date = models.DateTimeField()
    duration = models.FloatField(null=True)
    url = models.URLField()

class ScheduledTask(models.Model):
    task_id = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=50)
    url = models.CharField(max_length=255)
    headers = JSONField(null=True)
    body = models.TextField(null=True)

class WebserviceMetrics(models.Model):
    url = models.URLField()
    trust = models.IntegerField()
    response_time = models.FloatField()
    availability = models.FloatField()
    successability = models.FloatField()
    throughput = models.FloatField()
    reliability = models.FloatField()
    request_id = models.ForeignKey(Request, on_delete=models.CASCADE)
