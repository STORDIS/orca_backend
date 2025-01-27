import os
from celery import Celery, signals

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orca_backend.settings')

app = Celery('orca_backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object(f'django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


def cancel_task(task_id):
    """ 
    This function is used to cancel a task in Celery.
    
    Args:
        task_id: The ID of the task to be cancelled.
    """
    app.control.revoke(task_id, terminate=True, signal="SIGKILL")


@signals.worker_init.connect
def on_worker_init(sender, **kwargs):
    from orca_nw_lib.gnmi_util import close_all_stubs
    close_all_stubs()


@signals.worker_ready.connect
def on_worker_ready(sender, **kwargs):
    """
    This function is called when a worker is ready to process tasks.
    It revokes all tasks with status "started" and sets their status to "interrupted" when server is restarted.
    
    Args:
        sender: The sender of the signal.
        **kwargs: Additional keyword arguments.
    """
    from django_celery_results.models import TaskResult, states
    results = TaskResult.objects.filter(status=str(states.STARTED))
    for i in results:
        cancel_task(i.task_id)
        i.status = "INTERRUPTED"
        i.save()
