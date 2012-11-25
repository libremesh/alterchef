import os
import codecs
import datetime
import subprocess
from collections import defaultdict

from django.db import models, DatabaseError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from autoslug.fields import AutoSlugField
from django.utils.text import normalize_newlines
from django.template import Context, Template
from django.core.mail import mail_managers
from django.contrib.sites.models import Site

from fields import JSONField
from utils import to_thread

from django.conf import settings

class IncludePackages(object):

    def __init__(self, include=None, exclude=None):
        self.include = include or []
        self.exclude = exclude or []

    @classmethod
    def from_str(cls, string):
        ip = IncludePackages()
        packages = string.split()
        for package in packages:
            if package.startswith("-"):
                ip.exclude.append(package[1:])
            else:
                ip.include.append(package)
        return ip

    @classmethod
    def load(cls, file_obj):
        return IncludePackages.from_str(file_obj.read())


    def to_str(self):
        out = ""
        if self.include:
            out += " ".join(self.include)
        if self.exclude:
            out += " -" + " -".join(self.exclude)
        return "\n".join(out.split())

    def dump(self, file_obj):
        file_obj.write(self.to_str())


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
                f.write(normalize_newlines(filecontent))


class Network(models.Model):
    user = models.ForeignKey(User, editable=False)
    name = models.CharField(_('name'), max_length=100, unique=True,
                            help_text=_("also acts as the default public ESSID. Eg: quintanalibre.org.ar"))
    slug = AutoSlugField(populate_from='name', always_update=False,
                         editable=False, blank=True, unique=True)
    description = models.TextField(_('description'))

    def get_absolute_url(self):
        return reverse('network-detail', kwargs={'slug': self.slug})

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('network')
        verbose_name_plural = _('networks')
        ordering = ['name']


class FwProfile(models.Model):
    network = models.ForeignKey(Network, verbose_name=_('network'))
    name = models.SlugField(_("name"), default="node", max_length=15)
    slug = AutoSlugField(_("slug"), always_update=False, unique=True,
                         populate_from=lambda instance: instance._get_slug())
    description = models.TextField(_('description'))
    creation_date = models.DateTimeField(_("creation date"), default=datetime.datetime.now,
                                         editable=False)
    path = models.CharField(editable=False, max_length=255)
    based_on = models.ForeignKey("self", verbose_name=_('based on'), blank=True,
                                 null=True, on_delete=models.SET_NULL,
                                 help_text=_("Create fw profile based on this profile. Leave it on default if you are not sure."))
    include_packages = models.TextField(_('include packages'), blank=True)
    include_files = JSONField(_('include files'), default="{}")


    def _get_slug(self):
        return "%s-%s" % (self.network.slug, self.name)

    def __unicode__(self):
        return "%s-%s" % (unicode(self.network), self.name)

    def load_includes_from_disk(self, from_path):
        inc_files = IncludeFiles.load(os.path.join(from_path, "include_files"))
        inc_packages = IncludePackages.load(open(os.path.join(from_path, "include_packages")))
        self.include_packages = inc_packages.to_str()
        self.include_files = inc_files.files

    def write_to_disk(self):
        to_path = os.path.join(settings.NETWORK_INCLUDES_PATH, self.network.name, self.name)
        if not os.path.exists(to_path):
            os.makedirs(to_path)

        inc_packages = IncludePackages.from_str(self.include_packages)
        inc_packages.dump(open(os.path.join(to_path, "include_packages"), "w"))
        files = {}
        for fname, content in self.include_files.iteritems():
            t = Template(content)
            c = Context({"NETWORK_NAME": self.network.name}, autoescape=False)
            files[fname] = normalize_newlines(t.render(c))

        inc_files = IncludeFiles(files)
        inc_files.dump(os.path.join(to_path, "include_files"))

    @models.permalink
    def get_absolute_url(self):
        return ('fwprofile-detail', [self.slug])

    class Meta:
        verbose_name = _("firmware profile")
        verbose_name_plural = _("firmware profiles")
        unique_together = ("network", "name")
        ordering = ['name', 'network__name']


STATUSES = (
    ("WAITING", _("waiting")),
    ("STARTED", _("started")),
    ("FINISHED", _("finished")),
    ("FAILED", _("failed")),
)

class StatusManager(models.Manager):
    _status = None
    def get_query_set(self):
        return super(StatusManager, self).get_query_set().filter(status=self._status)

class StartedManager(StatusManager):
    _status = 'STARTED'

class WaitingManager(StatusManager):
    _status = 'WAITING'

class FinishedManager(StatusManager):
    _status = 'FINISHED'

class FailedManager(StatusManager):
    _status = 'FAILED'

class FwJob(models.Model):
    status = models.CharField(verbose_name=_('satus'), choices=STATUSES, default="WAITING",
                              max_length=10)
    profile = models.ForeignKey(FwProfile, verbose_name=_('profile'))
    user = models.ForeignKey(User, editable=False, verbose_name=_('user'))
    job_data = JSONField(_('job data'), default="{}")
    build_log = models.TextField(_('build log'), blank=True)
    creation_date = models.DateTimeField(_("creation date"), default=datetime.datetime.now,
                                         editable=False)
    started = StartedManager()
    waiting = WaitingManager()
    finished = FinishedManager()
    failed = FailedManager()
    objects = models.Manager()

    class Meta:
        ordering = ['-pk']

    def __unicode__(self):
        return u"%s (%s)" % (self.profile, self.status)

    @classmethod
    def process_jobs(cls, sync=False):
        try:
            started = FwJob.objects.filter(status="STARTED")
            waiting = FwJob.objects.filter(status="WAITING")
        except DatabaseError:
            return
        if not started and waiting:
            job = waiting[0]
            job.status = "STARTED"
            job.profile.write_to_disk()
            commands = make_commands(job.profile.network.name,
                                     job.profile.name,
                                     job.job_data["devices"],
                                     job.job_data["revision"])
            job.job_data["commands"] = commands
            job.save()
            job.process(sync)  # runs in another thread


    def process(self, sync=False):
        if sync:
            self._process()
        else:
            to_thread(self._process)()

    def _process(self, *args, **kwargs):
        output = u"%s\n" % self.job_data
        for command in self.job_data["commands"]:
            output += command + "\n"
            p = subprocess.Popen(command.split(), stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
            output += p.communicate()[0].decode("utf-8")

            if p.returncode != 0:
                job_url = reverse('fwjob-detail', kwargs={'pk': self.pk})
                domain = Site.objects.all()[0].domain
                email_msg = "Cook failed for job http://%s%s" % (domain, job_url)
                mail_managers("[Chef] Cook failed", email_msg, fail_silently=True)
                self.status = "FAILED"
                self.build_log = output
                self.save()
                return
        self.status = "FINISHED"
        self.save()



def _make_commands(networkname, profilename, devices, revision):
    archs = defaultdict(list)
    for device in devices:
        arch = get_arch(device)
        if arch:
            if device.startswith("NONE%s" % arch):
                device = device.split("NONE%s" % arch)[1]
            archs[arch].append(device)

    return ["%s %s %s %s %s %s" % (settings.MAKE_SNAPSHOT, revision, arch, networkname, \
                                   profilename, " ".join(devices)) for (arch, devices) in archs.iteritems()]

def make_commands(networkname, profilename, devices, revision):
    return _make_commands(networkname, profilename, devices, revision)

def get_arch(device):
    for arch, devices in ARCHS.iteritems():
        if device in devices:
            return arch

ARCHS = {
    "ar71xx": set([
            "ath5k","ALFAAP96","HORNETUB","ALFANX","ALL0305","ALL0258N","ALL0315N","AP113","AP121","AP121MINI","AP136","AP81","AP83","AP96","DB120","PB42",
            "PB44","PB92","A02RBW300N","WZRHPG300NH","WZRHPG300NH2","WZRHPAG300H","WZRHPG450H","WHRG301N","WHRHPG300N","WHRHPGN",
            "WLAEAG300N","WP543","WPE72","DIR600A1","DIR601A1","DIR615C1","DIR615E4","DIR825B1","EWDORIN","JA76PF","JA76PF2",
            "JWAP003","WRT160NL","WRT400N","WNDR3700","OM2P","MZKW04NU","MZKW300NH","RW2458N","TLMR11U","TLMR3020","TLMR3040",
            "TLMR3220","TLMR3420","TLWR703","TLWA701","TLWA901","TLWDR4300","TLWR740","TLWR741","TLWR743","TLWR841","TLWR842",
            "TLWR941","TLWR1041","TLWR1043","TLWR2543","TEW632BRP","TEW652BRP","TEW673GRU","TEW712BR","UBNTRS","UBNTRSPRO",
            "UBNTUNIFI","UBNT","ZCN1523H28","ZCN1523H516","NBG_460N_550N_550NH"]),
    "atheros": set(["NONEatherosDefault"]),
}

import threading

def thread_process_jobs():
    import time, random
    sleep = random.randint(5, 15)
    while True:
        FwJob.process_jobs()
        time.sleep(sleep)

process_jobs_thread = threading.Thread(target=thread_process_jobs)
process_jobs_thread.daemon = True
process_jobs_thread.start()

