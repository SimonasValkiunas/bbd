import json
import math
from django.forms import model_to_dict
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from collections import defaultdict
from django.http import HttpResponse, JsonResponse
import csv
from django.utils import timezone
from .models import ScheduledTask,Request,WebserviceMetrics
from .tasks import collect_data
from django.db.models import Avg
from decimal import Decimal, ROUND_DOWN


class CollectorView(APIView):
    
    def post(self, request, format=None):
        data = request.data
        start_time = timezone.make_aware(datetime.strptime(data.get('startDate'), "%Y-%m-%dT%H:%M"))
        end_time = timezone.make_aware(datetime.strptime(data.get('endDate'), "%Y-%m-%dT%H:%M"))
        url = data.get("endpoint")
        headers = data.get("headers")
        body = data.get("body")
        
        task = collect_data.apply_async(args=[start_time, end_time, url, headers, body], eta=start_time)
        ScheduledTask.objects.create(task_id=task.id, start_time=start_time, end_time=end_time, status='scheduled', url=url, headers=headers, body=body)
        return JsonResponse({'message': 'Task scheduled successfully'})        


class StopTaskView(APIView):
    def post(self, request, format=None):
        data = request.data
        task_id = data.get('task_id', None)
        url = data.get('url', None)
        
        if task_id:
            tasks = ScheduledTask.objects.filter(task_id=task_id)
        elif url:
            tasks = ScheduledTask.objects.filter(url=url)
        else:
            tasks = ScheduledTask.objects.all()

        for task in tasks:
            task.status = 'stopped'
            task.save()

        return JsonResponse({'message': 'Task(s) stopped successfully'})

class TaskListView(APIView):
    def get(self, request):
        tasks = ScheduledTask.objects.all()
        task_list = list(tasks.values())
        return Response(task_list, status=status.HTTP_200_OK)

class MetricsView(APIView):
    def get(self, request, format=None):

        metrics_by_url = defaultdict(list)
        for metrics in WebserviceMetrics.objects.all():
            metrics_dict = model_to_dict(metrics)
            metrics_by_url[metrics.url].append(metrics_dict)

        averages_by_url = {}
        for url, metrics_list in metrics_by_url.items():
            avg_trust = sum([metrics['trust'] for metrics in metrics_list]) / len(metrics_list)
            avg_response_time = sum([metrics['response_time'] for metrics in metrics_list]) / len(metrics_list)
            avg_availability = sum([metrics['availability'] for metrics in metrics_list]) / len(metrics_list)
            avg_throughput = sum([metrics['throughput'] for metrics in metrics_list]) / len(metrics_list)
            avg_reliability = sum([metrics['reliability'] for metrics in metrics_list]) / len(metrics_list)
            avg_successability = sum([metrics['successability'] for metrics in metrics_list]) / len(metrics_list)

            averages_by_url[url] = {
                'trust': math.floor(avg_trust),
                'response_time': round(avg_response_time,1),
                'availability': round(avg_availability,1),
                'throughput': round(avg_throughput,1),
                'reliability': round(avg_reliability,1),
                'successability': round(avg_successability,1),
            }


        return Response(averages_by_url, status=status.HTTP_200_OK)



class GraphView(APIView):
    def get(self, request, format=None):
        url = request.GET.get('url')
        if url:
            metrics = WebserviceMetrics.objects.filter(url=url)
            metrics_dict_list= []
            for metric in metrics:
                metrics_dict = model_to_dict(metric)
                request_id = metrics_dict.get('request_id') 
                request_instance = Request.objects.get(id=request_id)
                metrics_dict['time'] = request_instance.date  
                metrics_dict_list.append(metrics_dict)
            return Response({url: metrics_dict_list}, status=status.HTTP_200_OK)


class ExportView(APIView):
    def post(self, request, format=None):
        data = json.loads(request.body)
        urls = data.get('urls', None)
        columns = data.get('columns', None)

        if urls:
            metrics = WebserviceMetrics.objects.filter(url__in=urls).values('url').annotate(
                    average_trust=Avg('trust'),
                    average_response_time=Avg('response_time'),
                    average_availability=Avg('availability'),
                    average_throughput=Avg('throughput'),
                    average_reliability=Avg('reliability'),
                    average_successability=Avg('successability'),
                )
        else:
            metrics = WebserviceMetrics.objects.all().values('url').annotate(
                    average_trust=Avg('trust'),
                    average_response_time=Avg('response_time'),
                    average_availability=Avg('availability'),
                    average_throughput=Avg('throughput'),
                    average_reliability=Avg('reliability'),
                    average_successability=Avg('successability'),
                )
        rounded_metrics = []
        for metric in metrics:
            rounded_metric = {
                'web_service': metric['url'].split("www.")[1],
                'average_trust': Decimal(metric['average_trust']).quantize(Decimal('0'), rounding=ROUND_DOWN),
                'average_response_time': Decimal(metric['average_response_time']).quantize(Decimal('0.0'), rounding=ROUND_DOWN),
                'average_availability': Decimal(metric['average_availability']).quantize(Decimal('0.0'), rounding=ROUND_DOWN),
                'average_throughput': Decimal(metric['average_throughput']).quantize(Decimal('0.0'), rounding=ROUND_DOWN),
                'average_reliability': Decimal(metric['average_reliability']).quantize(Decimal('0.0'), rounding=ROUND_DOWN),
                'average_successability': Decimal(metric['average_successability']).quantize(Decimal('0.0'), rounding=ROUND_DOWN),
            }
            rounded_metrics.append(rounded_metric)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="metrics.csv"'
        
        if not columns:
            columns = ['web_service', 'average_trust', 'average_response_time', 'average_availability', 'average_throughput', 'average_reliability', 'average_successability' ]
        else:
            columns = ["web_service"] + columns

        writer = csv.writer(response)
        writer.writerow(columns)

        for metric in rounded_metrics:
            row = [metric.get(column) for column in columns]
            writer.writerow(row)

        return response

class URLListView(APIView):
    def get(self, request):
        urls = WebserviceMetrics.objects.values_list('url', flat=True).distinct()
        return Response(list(urls), status=status.HTTP_200_OK)
