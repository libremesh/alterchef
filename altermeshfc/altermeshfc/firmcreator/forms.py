# -*- coding: utf-8 -*-
import os
import datetime

from django import forms
from django.conf import settings
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

from models import IncludePackages, IncludeFiles, FwProfile, Network

# We may add a description of each package, in the form ("pkgname", "description")
SUGESTED_PACKAGES = ["iperf", "mini-snmpd"]

class BaseForm(forms.Form):
    helper = FormHelper()
    helper.form_tag = False
    helper.form_class = 'form-horizontal'

class IncludePackagesForm(BaseForm):

    optional_packages = forms.MultipleChoiceField(
        label = _("Optional packages"),
        choices = [(p, p) for p in SUGESTED_PACKAGES],
        widget = forms.CheckboxSelectMultiple,
        help_text = _("These packages are not essential, but pretty useful."),
        required = False,
    )

    include_exclude = forms.CharField(
        label = _("Extra include/exclude packages"),
        help_text = _("list of packages to include or exclude. i.e. to include foo and baz, and exclude bar: <tt>foo -bar baz</tt>"),
        widget=forms.Textarea,
        required = False,
    )

    @classmethod
    def from_instance(self, instance):
        return IncludePackagesForm({"include_exclude":instance.to_str()})

    @classmethod
    def from_str(self, string):
        ip = IncludePackages.from_str(string)
        optional_packages = []
        for package in ip.include[:]:
            if package in SUGESTED_PACKAGES:
                optional_packages.append(package)
                ip.include.remove(package)
        return IncludePackagesForm({"include_exclude":ip.to_str(), "optional_packages": optional_packages})

    def to_str(self):
        optional_packages = self.cleaned_data.get("optional_packages")
        include_exclude = self.cleaned_data.get("include_exclude")
        ip = IncludePackages.from_str(include_exclude)
        ip.include = set(ip.include + optional_packages)
        return ip.to_str()

class IncludeFileForm(BaseForm):

    name = forms.CharField(
        help_text="eg: /etc/config/batmesh"
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
        return IncludePackagesForm({"include_exclude":instance.to_str()})

class NetworkForm(forms.ModelForm):

    class Meta:
        model = Network
        exclude = (
            'slug', 'user',
        )

class FwProfileSimpleForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(FwProfileSimpleForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        self.fields['network'] = forms.ModelChoiceField(queryset=Network.objects.filter(user=user))

    helper = FormHelper()
    helper.form_tag = False
    helper.form_class = 'form-horizontal'

    class Meta:
        model = FwProfile
        exclude = (
            'creation_date', 'path', 'include_packages', 'include_files',
        )

class FwProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(FwProfileForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        self.fields['network'] = forms.ModelChoiceField(queryset=Network.objects.filter(user=user))


    def save(self, user, *args, **kwargs):
        kwargs['commit'] = False
        obj = super(FwProfileForm, self).save(*args, **kwargs)
        obj.user = user
        obj.save()
        self.save_m2m()
        return obj

    helper = FormHelper()
    helper.form_tag = False
    helper.form_class = 'form-horizontal'

    class Meta:
        model = FwProfile
        exclude = (
            'creation_date', 'path', 'include_files', 'include_packages'
        )

IncludeFilesFormset = formset_factory(IncludeFileForm, extra=0)

COMMON_DEVICES = (
    ('TLMR3020', 'TP-LINK TL-MR3020'),
    ('TLMR3220', 'TP-LINK TL-MR3220'),
    ('TLMR3420', 'TP-LINK TL-MR3420'),
    ('TLWR842', 'TP-LINK TL-WR842N/ND'),
    ('UBNT', 'Ubiquiti M series: M2, M5 (ar71xx_UBNT)'),
    ('NONEatherosDefault', 'Ubiquiti legacy: Bullet 2, Nano 2/5 (atheros)'),
)


class CookFirmwareForm(forms.Form):
    common_devices = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                               required=False,
                                               choices=COMMON_DEVICES,
                                               label=_("Common devices"))
    other_devices = forms.CharField(required=False, label=_("Other devices"),
                                    help_text=_("List of PROFILE devices separated by a space or EOL. Eg: <code>TLMR3420 UBNT TLWA701</code>"),
                                    )
    openwrt_revision = forms.SlugField(required=True, initial="stable")

    def get_devices(self):
        return self.cleaned_data["common_devices"] + self.cleaned_data["other_devices"].split()

    def clean(self):
        cleaned_data = super(CookFirmwareForm, self).clean()
        common_devices = cleaned_data.get("common_devices")
        other_devices = cleaned_data.get("other_devices")

        if not (common_devices or other_devices):
            raise forms.ValidationError(self.ERROR_ONE_DEVICE)

        devices = self.get_devices()
        if not all(map(lambda x: x.isalnum(), devices)):
            raise forms.ValidationError(self.ERROR_ALPHANUMERIC)

        return cleaned_data

    ERROR_ONE_DEVICE = _("You must select at least one device.")
    ERROR_ALPHANUMERIC = _("PROFILE devices must contain only alphanumeric characters.")
