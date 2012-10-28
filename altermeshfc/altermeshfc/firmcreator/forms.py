# -*- coding: utf-8 -*-
import os
import datetime

from django import forms
from django.forms.widgets import TextInput, Textarea, FileInput, DateInput
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms.formsets import formset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Fieldset
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions

from models import IncludePackages, IncludeFiles, FwProfile

# We may add a description of each package, in the form ("pkgname", "description")
SUGESTED_PACKAGES = ["iperf", "uhttpd", "mini-snmpd"]

class BaseForm(forms.Form):
    helper = FormHelper()
    helper.form_tag = False
    helper.form_class = 'form-horizontal'

class IncludePackagesForm(BaseForm):

    optional_packages = forms.MultipleChoiceField(
        label = _("Optional packages"),
        choices = [(p, p) for p in SUGESTED_PACKAGES],
        widget = forms.CheckboxSelectMultiple,
        help_text = _("This packages are not needed but you may enjoy from them."),
        required = False,
    )

    include_exclude = forms.CharField(
        label = _("Extra include/exclude packages"),
        help_text = _("list of packages to include and exclude in the following form to include foo and baz and exclude bar: <tt>foo -bar baz</tt>"),
        required = False,
    )

    @classmethod
    def from_instance(self, instance):
        return IncludePackagesForm({"include_exclude":instance.to_string()})


class IncludeFileForm(BaseForm):

    name = forms.CharField(
        help_text="eg: /etc/conf/batmesh"
    )

    content = forms.CharField(
        widget = forms.Textarea(),
    )

    helper = FormHelper()
    helper.form_tag = False
    helper.form_style = 'inline'
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
            Fieldset(_("File"),
                Field('name', css_class="input-xxlarge"),
                Field('content', css_class="input-xxlarge pre-scrollable"),
            )
        )

    @classmethod
    def from_instance(self, instance):
        return IncludePackagesForm({"include_exclude":instance.to_string()})

class FwProfileForm(forms.ModelForm):

    base_profile = forms.CharField(
        help_text = _("Create fw profile based on this profile. Leave it on default if you are not sure.")
    )

    helper = FormHelper()
    helper.form_tag = False
    helper.form_class = 'form-horizontal'

    class Meta:
        model = FwProfile
        exclude = (
            'cretion_date', 'path',
        )

IncludeFilesFormset = formset_factory(IncludeFileForm, extra=0)
