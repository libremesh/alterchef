# -*- coding: utf-8 -*-

import os
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView, UpdateView, DetailView, CreateView, DeleteView
from django.utils.decorators import method_decorator

from models import IncludeFiles, Network
from forms import IncludeFilesFormset, IncludePackagesForm, FwProfileForm, NetworkForm

class LoginRequiredMixin(object):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(NetworkEdit, self).dispatch(*args, **kwargs)

class NetworkCreateView(CreateView, LoginRequiredMixin):
    model = Network

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(NetworkCreateView, self).form_valid(form)

class NetworkUpdateView(UpdateView, LoginRequiredMixin):
    model = Network
    def get_object(self, queryset=None):
        object = super(NetworkUpdateView, self).get_object(queryset)
        if object.user == self.request.user:
            return object
        else:
            raise Http404

class NetworkDeleteView(DeleteView, LoginRequiredMixin):
    model = Network
    success_url = reverse_lazy('network-list')

    def get_object(self, queryset=None):
        object = super(NetworkDeleteView, self).get_object(queryset)
        if object.user == self.request.user:
            return object
        else:
            raise Http404

class NetworkDetailView(DetailView):
    model = Network

class NetworkListView(ListView):
    model = Network


def index(request):
    return render(request, "firmcreator/index.html", {
    })



@login_required
def crud_profile(request):
    based_on = request.GET.get("based_on", None)
    if based_on:
        # buscar perfil
        # cargar perfil
        # FIXME
        inc_files = IncludeFiles.load(os.path.join(based_on, "include_files"))
        initial = [{"name":name, "content": content} for name, content in inc_files.files.iteritems()]
        include_files_formset = IncludeFilesFormset(initial=initial, prefix="include-files")
    else:
        include_files_formset = IncludeFilesFormset(prefix="include-files")
    return render(request, "firmcreator/crud_profile.html", {
        'include_files_formset': include_files_formset,
        'include_packages_form': IncludePackagesForm(),
        'profile_form': FwProfileForm(),
    })


