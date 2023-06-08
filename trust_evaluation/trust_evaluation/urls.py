from django.urls import path
from trust_eval_prod.views import CollectorView
from trust_eval_prod.views import MetricsView
from trust_eval_prod.views import GraphView
from trust_eval_prod.views import ExportView
from trust_eval_prod.views import URLListView
from trust_eval_prod.views import StopTaskView
from trust_eval_prod.views import TaskListView

urlpatterns = [
    path('schedule/', CollectorView.as_view(), name='collector'),
    path('metrics/', MetricsView.as_view(), name='metrics'),
    path('graph/', GraphView.as_view(), name='graph'),
    path('export/csv/', ExportView.as_view(), name='export_requests_csv'),
    path('urls/', URLListView.as_view(), name='url_list'),
    path('stop_task/', StopTaskView.as_view(), name='stop_task'),
    path('tasks/', TaskListView.as_view(), name='tasks')

]