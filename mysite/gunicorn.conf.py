import multiprocessing
from gevent import monkey

monkey.patch_all()

preload_app = True

bind = '127.0.0.1:8080'
workers = 3
worker_class = 'gevent'
max_requests = 1000


proc_name = 'gunicorn_blog_project'


# worker_tmp_dir = '/dev'


loglevel = 'debug'
# logfile = '/home/log/gunicorn.debug.log'
errorlog = '/home/log/gunicorn.error.log'


# accesslog = '/home/log/gunicorn.access.log'
# access_logformat = ''
