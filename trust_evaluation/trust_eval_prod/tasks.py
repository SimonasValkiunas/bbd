from celery import shared_task
import time
from django.forms import model_to_dict
import requests
from .models import Request, ScheduledTask, WebserviceMetrics
from asgiref.sync import async_to_sync
from django.utils import timezone
from channels.layers import get_channel_layer
import asyncio
from trust_eval_prod.lib.bpnn_model import calculate_metrics

@shared_task
def collect_data(start_date, end_date, url, headers, body, task_id=None):

    print(f"Sending request to {url}")
    start_time = time.time()
    error_request = 0
    successful_request = 0
    successful_invocation = 0
    failed_invocation = 0
    duration = 0
    try:
        response = requests.get(url, headers=headers, data=body)
        duration = time.time() - start_time
        if response.status_code >= 200 and response.status_code < 500:
            successful_request += 1
        else:
            error_request += 1
        successful_invocation += 1
    except Exception as e:
        print(f"Error occured: {e}")
        failed_invocation += 1
    
    request = Request(date=timezone.now(), duration=duration, url = url, successful_request=successful_request, error_request=error_request, successful_invocation=successful_invocation, failed_invocation=failed_invocation)    
    request.save()

    metric = calculate_metrics(request)
    wbmetric = WebserviceMetrics( url=request.url, trust=metric["trust"], response_time=metric["response_time"], availability=metric["availability"], throughput=metric["throughput"], reliability=metric["reliability"], successability=metric["successability"], request_id=request)
    wbmetric.save()

    request_dict = model_to_dict(request)
    request_dict['date'] = request.date.isoformat()
    ws_data = f"Request sent to {request.url} at {request.date}\nHeaders:{headers}\nData:{body}\nResponse time: {request.duration}\n----------------------\n"

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'task_{task_id}',
        {
            'type': 'send_log',
            'text': ws_data,
        }
    )
 
    return f"Task Completed. ID: {task_id}"

@shared_task
def check_scheduled_tasks():
    now = timezone.now()
    tasks_to_stop = ScheduledTask.objects.filter(end_time__lte=now)
    for t in tasks_to_stop:
        t.status = 'stopped'
        t.save()

    tasks = ScheduledTask.objects.filter(start_time__lte=now, end_time__gte=now).exclude(status='stopped')
    for task in tasks:
        collect_data.delay(
            task.start_time,
            task.end_time,
            task.url,
            task.headers,
            task.body,
            task.task_id
        )
        task.status = 'running'
        task.save()