import os
import codecs
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from autoslug.fields import AutoSlugField

class IncludePackages(object):

    def __init__(self, include=None, exclude=None):
        self.include = include or []
        self.exclude = exclude or []

    @classmethod
    def load(cls, file_obj):
        ip = IncludePackages()
        packages = file_obj.read().split()
        for package in packages:
            if package.startswith("-"):
                ip.exclude.append(package[1:])
            else:
                ip.include.append(package)
        return ip

    def to_string(self):
        return " ".join(self.include) + " -" + " -".join(self.exclude)

    def dump(self, file_obj):
        file_obj.write(self.to_string())

class IncludeFiles(object):

    def __init__(self, files=None):
        self.files = files or {}

    @classmethod
    def load(cls, path):
        inc_files = IncludeFiles()
        for root, dirs, files in os.walk(os.path.abspath(path)):
            dirname = root.split("include_files")[1]
            for filename in files:
                with codecs.open(os.path.join(root, filename), "r", "utf-8") as f:
                    inc_files.files[os.path.join(dirname, filename)] = f.read()
        return inc_files

    def dump(self, to_path):
        for abspath, filecontent in self.files.iteritems():
            to_dir = os.path.join(to_path, os.path.dirname(abspath[1:]))
            filename = os.path.basename(abspath)
            if not os.path.exists(to_dir):
                os.makedirs(to_dir)
            with codecs.open(os.path.join(to_dir, filename), "w", "utf-8") as f:
                f.write(filecontent)

class FwProfile(object):

    def read_profile(self):
        raise NotImplemented

    def write_profile(self):
        raise NotImplemented


class Network(models.Model):
    user = models.ForeignKey(User, editable=False)
    name = models.CharField(_('name'), max_length=100, unique=True,
                            help_text=_("also acts as the default public ESSID. Eg: quintanalibre.org.ar"))
    slug = AutoSlugField(populate_from='name', always_update=False,
                         editable=False, blank=True)
    description = models.TextField(_('description'))

    def get_absolute_url(self):
        return reverse('network-detail', kwargs={'slug': self.slug})

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('network')
        verbose_name_plural = _('networks')


class FwProfile(models.Model):
    network = models.ForeignKey(Network, verbose_name=_('network'))
    name = models.SlugField(_("name"), default="default", max_length=15)
    description = models.TextField(_('description'))
    creation_date = models.DateTimeField(_("creation date"), auto_now=True,
                                         editable=False)
    path = models.CharField(editable=False, max_length=255)

    class Meta:
        verbose_name = _("firmware profile")
        verbose_name_plural = _("firmware profiles")
