import os
import multiprocessing

bind = "0.0.0.0:5000"

workers = int(os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
threads = int(os.environ.get("GUNICORN_THREADS", 1))

timeout = int(os.environ.get("GUNICORN_TIMEOUT", 30))
graceful_timeout = 30
keepalive = 5

max_requests = 1000
max_requests_jitter = 100 # randomizes so workers don't restart simultaneously

accesslog = "-" # logs to standard streams and not to files inside a container that would vanish when the container is replaced
errorlog = "-"

forwarded_alloq_ips = "*" # so Gunicorn can trust in X-Forwarded-* headers
