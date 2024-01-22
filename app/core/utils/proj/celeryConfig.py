broker_url='redis://localhost:6379/0',
result_backend = 'sqlite:///celery_results.db',
include=['proj.tasks']
result_expires=3600