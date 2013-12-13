# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.formsets import formset_factory, BaseFormSet
from django.utils.text import normalize_newlines
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Fieldset

from models import IncludePackages, FwProfile, Network, Device, SSHKey, OpenwrtImageBuilder
from utils import get_default_profile

class BaseForm(forms.Form):
    helper = FormHelper()
    helper.form_tag = False
    helper.form_class = 'form-horizontal'

class IncludePackagesForm(BaseForm):

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
        return IncludePackagesForm({"include_exclude":ip.to_str()})

    def to_str(self):
        include_exclude = self.cleaned_data.get("include_exclude")
        ip = IncludePackages.from_str(include_exclude)
        return ip.to_str()

class IncludeFileForm(BaseForm):

    path = forms.CharField(
        help_text="eg: /etc/config/batmesh"
    )

    content = forms.CharField(
        widget = forms.Textarea(),
        required = False,
    )

    helper = FormHelper()
    helper.form_tag = False
    helper.form_style = 'inline'
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
            Fieldset(_("File"),
                Field('path', css_class="input-xxlarge"),
                Field('content', css_class="input-xxlarge pre-scrollable"),
                Field('DELETE'),
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


def make_choices(queryset, title=""):
    base = "--   " if title else ""
    default = title if title else '------'
    choices = map(lambda item: (item.pk, base + unicode(item)), queryset)
    choices.insert(0, ('' or title, default))
    return choices

def make_base_on_choices(user):

    default_profile = get_default_profile()
    own_profiles = FwProfile.objects.filter(network__user=user)
    other_profiles = FwProfile.objects.exclude(network__user=user)
    if default_profile:
        default_nps = FwProfile.objects.filter(network=default_profile.network)
        other_profiles = other_profiles.exclude(pk__in=[p.pk for p in default_nps])

    own_choices = make_choices(own_profiles, _("Own profiles")) if own_profiles else []
    other_choices = make_choices(other_profiles, _("Other profiles (unsupported!)")) if other_profiles else []

    choices = own_choices + other_choices

    if default_profile:
        def_choices = make_choices(default_nps, title=_("Default profiles (supported)"))
        choices = def_choices + choices
    choices = [("", _("OpenWrt Vanilla"))] + choices
    return choices


def _create_ssh_keys_field(data, kwargs, user):
    HT = _(u"<span class='text-warning'>Select at least one ssh key if you"
           u" want to access using ssh</span>")
    kwds = {"auto_add": True}
    instance = kwargs.get('instance', None)
    if instance:
        network = instance.network
    elif data:
        network = data.get("network")
    else:
        network = kwargs.get("initial").get("network") if "initial" in kwargs else None
    if network and not hasattr(network, "pk"):
        network = Network.objects.get(id=int(network))

    if network:
        kwds["user__in"] = network.users
    else:
        kwds["user"] = user
    ssh_keys = SSHKey.objects.filter(**kwds)
    return forms.ModelMultipleChoiceField(
                queryset=ssh_keys, widget=forms.CheckboxSelectMultiple,
                help_text=HT, required=False,
                initial=[s.pk for s in ssh_keys.filter(auto_add=True)])

COMMON_DEVICES = (
    ('TLWDR4300', 'TP-LINK TL-WDR3500/3600/4300/4310'),
    ('TLWR842', 'TP-LINK TL-WR842N/ND'),
    ('TLMR3020', 'TP-LINK TL-MR3020'),
    ('TLMR3220', 'TP-LINK TL-MR3220'),
    ('TLMR3420', 'TP-LINK TL-MR3420'),
    ('UBNT', 'Ubiquiti M series: M2, M5 (ar71xx_UBNT)'),
)

ALL_DEVICES = COMMON_DEVICES + tuple(((device, device) for device in \
                                       Device.list_devices() if device not in 
                                      [common_dev[0] for common_dev in COMMON_DEVICES] ))

def build_revision_choices():

    stable_revision = OpenwrtImageBuilder.get_stable_version()
    def transform_revision(rev):
        if rev == stable_revision:
            return "%d (stable)" % rev
        else:
            return "%d" % rev
    choices = [("r%d" % r, transform_revision(r)) for r in \
               OpenwrtImageBuilder.get_available_openwrt_revisions()]
    return choices

class FwProfileCommon(forms.ModelForm):

    openwrt_revision = forms.ChoiceField(choices=(("stable", "stable"),))

    def __init__(self, data=None, *args, **kwargs):
        user = kwargs.pop('user')
        super(FwProfileCommon, self).__init__(data, *args, **kwargs)
        self.fields['network'] = forms.ModelChoiceField(queryset=Network.objects.with_user_perms(user))
        self.fields['based_on'].choices = make_base_on_choices(user)
        self.fields['ssh_keys'] = _create_ssh_keys_field(data, kwargs, user)
        instance = kwargs.get("instance")
        revision_choices = build_revision_choices()
        if revision_choices:
            initial = instance.openwrt_revision if instance else \
                      filter(lambda x: "stable" in x[1], revision_choices)[0][0]
            self.fields["openwrt_revision"] = forms.ChoiceField(choices=revision_choices,
                                                                initial=initial)

    def clean(self):
        cleaned_data = super(FwProfileCommon, self).clean()

        devices = cleaned_data.get("devices")

        if not all(map(lambda x: x.isalnum(), devices)):
            raise forms.ValidationError(self.ERROR_ALPHANUMERIC)

        for device in devices:
            if not Device.exists(device):
                raise forms.ValidationError(self.ERROR_NONEXISTENT_DEVICE % device)
        cleaned_data["devices"] = " ".join(devices)
        return cleaned_data


    ERROR_ONE_DEVICE = _("You must select at least one device.")
    ERROR_ALPHANUMERIC = _("PROFILE devices must contain only alphanumeric characters.")
    ERROR_NONEXISTENT_DEVICE = _("Nonexistent device %s")


    class Meta:
        model = FwProfile

class FwProfileSimpleForm(FwProfileCommon):

    helper = FormHelper()
    helper.form_tag = False
    helper.form_class = 'form-horizontal'

    devices = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                        required=False,
                                        choices=COMMON_DEVICES,
                                        label=_("devices"))
    class Meta:
        model = FwProfile
        exclude = (
            'creation_date', 'path', 'include_packages', 'include_files',
        )

class FwProfileForm(FwProfileCommon):
    UPLOAD_HELP_TEXT = _(u'Upload a tar/tar.gz with files to include.' \
                          ' Files <b>MUST</b> be UTF-8 encoded!')
    upload_files = forms.FileField(required=False, help_text=UPLOAD_HELP_TEXT)

    helper = FormHelper()
    helper.form_tag = False
    helper.form_class = 'form-horizontal'

    devices = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                        required=False,
                                        choices=ALL_DEVICES,
                                        label=_("devices"))

    class Meta:
        model = FwProfile
        exclude = (
            'creation_date', 'include_files', 'include_packages'
        )


class IncludeFilesBaseFormSet(BaseFormSet):
    def include_files(self):
        files = {}
        for form in self.cleaned_data:
            if form.get("DELETE"):
                continue
            files[form["path"]] = normalize_newlines(form["content"])
        return files

IncludeFilesFormset = formset_factory(IncludeFileForm, extra=0, can_delete=True,
                                      formset=IncludeFilesBaseFormSet)



