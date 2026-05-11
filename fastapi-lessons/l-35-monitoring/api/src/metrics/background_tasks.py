from prometheus_client import Histogram

from src.metrics.container.collector_container import RegistryContainer

background_task_duration_seconds = Histogram(
    'background_task_duration_seconds',
    'Background task execution time',
    ['task_type'],
    registry=RegistryContainer.registry()
)

# also you can use background_task_duration_seconds
# background_task_duration_seconds.labels(task_type=task_type).observe(duration)
