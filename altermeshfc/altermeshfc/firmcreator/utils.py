# -*- coding: utf-8 -*-
import os
import re
import string

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied

class LoginRequiredMixin(object):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)

class UserRequiredMixin(object):

    def get_object(self, queryset=None):
        object = super(UserRequiredMixin, self).get_object(queryset)
        if object.user == self.request.user:
            return object
        else:
            raise PermissionDenied

class UserOrAdminRequiredMixin(object):

    def get_object(self, queryset=None):
        object = super(UserOrAdminRequiredMixin, self).get_object(queryset)
        if object.user == self.request.user or self.request.user in object.admins.all():
            return object
        else:
            raise PermissionDenied

from django.conf import settings


_default_slug = None
default_profile_slug = getattr(settings, "DEFAULT_PROFILE_SLUG", None)

def get_default_profile():
    global _default_slug

    if not _default_slug and default_profile_slug:
        from models import FwProfile

        _default_slug = FwProfile.objects.get(slug=default_profile_slug)
    return _default_slug


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
