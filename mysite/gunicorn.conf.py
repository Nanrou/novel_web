import multiprocessing
from gevent import monkey

monkey.patch_all()

preload_app = True

bind = '127.0.0.1:8080'
workers = 3
worker_class = 'gevent'
max_requests = 1000
x_forwarded_for_header = "X-Real-IP"

proc_name = 'gunicorn_blog_project'


# worker_tmp_dir = '/dev'


loglevel = 'debug'
# logfile = '/home/log/gunicorn.debug.log'
errorlog = '/home/log/gunicorn.error.log'


accesslog = '/home/log/gunicorn.access.log'
access_log_format = '%({X-Real-IP}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" '
