# -*- coding: utf-8 -*-

import os
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect

from models import IncludeFiles
from forms import IncludeFilesFormset, IncludePackagesForm, FwProfileForm

def index(request):
    return render(request, "firmcreator/index.html", {
    })

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


