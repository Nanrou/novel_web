bind = '127.0.0.1:8000'
workers = 3
worker_class = 'meinheld.gmeinheld.MeinheldWorker'
proc_name = 'gunicorn_novel_project'

x_forwarded_for_header = 'X-Real-IP'

loglevel = 'info'
accesslog = '-'

preload_app = True
reload = True
