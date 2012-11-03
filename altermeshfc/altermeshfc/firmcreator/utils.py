# -*- coding: utf-8 -*-
import os
import re
import string

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class LoginRequiredMixin(object):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)

import atexit
import Queue
import threading
from django.utils.functional import wraps

def worker_thread():
    while True:
        func, args, kwargs = queue.get()
        try:
            func(*args, **kwargs)
        except:
            raise
        finally:
            queue.task_done()

def to_thread(func):
    @wraps(func)
    def inner(*args, **kwargs):
        queue.put((func, args, kwargs))
    return inner

queue = Queue.Queue()

job_thread = threading.Thread(target=worker_thread)
job_thread.daemon = True
job_thread.start()

def cleanup():
    queue.join()

atexit.register(cleanup)
