import os
from os import path
import shutil
import StringIO
import tempfile
import subprocess

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from models import IncludePackages, IncludeFiles, FwJob, FwProfile, Network
from forms import IncludePackagesForm, CookFirmwareForm

TEST_DATA_PATH = path.join(path.dirname(__file__), "test_data")
PROFILES_PATH =  path.abspath(path.join(TEST_DATA_PATH, "profiles"))
TEST_PROFILE_PATH = path.join(PROFILES_PATH, "test.org.ar")

class ViewsTest(TestCase):
    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

class IncludePackagesTest(TestCase):
    def test_read_from_disk(self):
        ip = IncludePackages.load(open(path.join(TEST_PROFILE_PATH, "include_packages")))
        self.assertEqual(ip.include, ["kmod-batman-adv", "kmod-ipv6", "dnsmasq-dhcpv6",
                                      "ip6tables", "kmod-ath9k-htc", "safe-reboot", "iperf"])
        self.assertEqual(ip.exclude, ["dnsmasq", "qos-scripts"])

    def test_write_to_disk(self):
        ip = IncludePackages(include=["iperf", "safe-reboot"],
                             exclude=["dnsmasq", "qos-scripts"])
        output = StringIO.StringIO()
        ip.dump(output)
        self.assertEqual(output.getvalue(), "iperf safe-reboot -dnsmasq -qos-scripts")

    def test_form(self):
        ip = IncludePackages(include=["iperf", "safe-reboot"],
                             exclude=["dnsmasq", "qos-scripts"])
        form = IncludePackagesForm.from_instance(ip)
        self.assertTrue(form.is_valid())

    def test_string(self):
        ip = IncludePackages.from_str("")
        self.assertEqual(ip.to_str(), "")


class IncludeFilesTest(TestCase):

    def read_file(self, filename):
        return open(path.join(TEST_PROFILE_PATH, "include_files", filename)).read()

    def read_test_files(self):
        files = {}
        for filename in ["/etc/profile", "/etc/config/batman-adv", "/etc/config/batmesh",
                         "/etc/uci-defaults/add-opkg-repo-altermundi",
                         "/etc/uci-defaults/set-timezone-art3"]:
            files[filename] = self.read_file(filename[1:])
        return files

    def test_read_from_disk(self):
        inc_files = IncludeFiles.load(path.join(TEST_PROFILE_PATH, "include_files"))

        self.assertEqual(inc_files.files, self.read_test_files())

    def test_write_to_disk(self):
        inc_files = IncludeFiles(files=self.read_test_files())
        dest_dir = tempfile.mkdtemp()
        inc_files.dump(dest_dir)
        diff = subprocess.check_output(["diff", "-r", dest_dir, path.join(TEST_PROFILE_PATH, "include_files")], stderr=subprocess.STDOUT)
        self.assertEqual(diff, "")
        shutil.rmtree(dest_dir) # cleaning up

class NetworkTest(TestCase):
    def test_create_network_anonymous(self):
         response = self.client.get(reverse('network-create'))
         self.assertEqual(response.status_code, 302)

class JobsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("ninja", "e@a.com", "password")
        self.network = Network.objects.create(name="quintanalibre.org.ar", user=self.user)
        self.profile = FwProfile.objects.create(network=self.network)
        self.client.login(username="ninja", password="password")
        self.cook_url = reverse('cook', kwargs={'slug': self.profile.slug})

    def _test_process_some_jobs(self):
        fwjob = FwJob.objects.create(profile=self.profile, user=self.user)
        fwjob = FwJob.objects.create(profile=self.profile, user=self.user)

        import time
        self.assertEqual(len(FwJob.started.all()), 0)
        self.assertEqual(len(FwJob.waiting.all()), 2)
        FwJob.process_jobs()
        time.sleep(0.5)
        self.assertEqual(len(FwJob.started.all()), 1)
        self.assertEqual(len(FwJob.waiting.all()), 1)
        FwJob.process_jobs()
        time.sleep(0.5)

        self.assertEqual(len(FwJob.started.all()), 1)
        self.assertEqual(len(FwJob.waiting.all()), 0)
        FwJob.process_jobs()
        time.sleep(0.5)
        self.assertEqual(len(FwJob.started.all()), 0)
        self.assertEqual(len(FwJob.waiting.all()), 0)

    def _test_cook(self):
        response = self.client.get(self.cook_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.cook_url, {"other_devices":"TLMR3020", "openwrt_revision": "stable"})
        self.assertEqual(response.status_code, 302)

        self.assertEqual(len(FwJob.started.all()), 0)
        self.assertEqual(len(FwJob.waiting.all()), 1)
        FwJob.process_jobs()
        self.assertEqual(len(FwJob.started.all()), 1)
        self.assertEqual(len(FwJob.waiting.all()), 0)

    def test_empty_cook(self):
        response = self.client.post(self.cook_url, {})
        self.assertContains(response, "You must select at least one device.")

    def test_inyect_cook(self):
        response = self.client.post(self.cook_url, {"other_devices": "MR320;comando"})
        self.assertContains(response, "Devices must contains only alphanumeric characters.")

    def test_make_commands(self):
        from models import make_commands
        commands = make_commands("quintanalibre.org.ar", "profile1", ["TLMR3220", "NONEatherosDefault"], "33333")
        self.assertTrue("33333 ar71xx quintanalibre.org.ar profile1 TLMR3220" in commands[0])
        self.assertTrue("33333 atheros quintanalibre.org.ar profile1 Default" in commands[1])
