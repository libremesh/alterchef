import os
from os import path
import shutil
import StringIO
import tempfile
import subprocess

from django.test import TestCase
from models import IncludePackages, IncludeFiles
from forms import IncludePackagesForm

TEST_DATA_PATH = path.join(path.dirname(__file__), "test_data")
PROFILES_PATH =  path.abspath(path.join(TEST_DATA_PATH, "profiles"))
TEST_PROFILE_PATH = path.join(PROFILES_PATH, "test.org.ar")

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

