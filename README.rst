License
=======

This software is licensed under AGPL.

Install
=======

This app is composed of two different parts, the web frontend made using django and
the firmware builder that are bash scripts that uses OpenWrt ImageBuilder.

Installing & configuring the web app
------------------------------------

To install the web app dependencies run ``pip install -r requeriments.txt``
inside a virtualenv. Then you can follow any howto that explains deploying django.
We recomend using gunicorn, nginx and runit. Here are some links:

http://honza.ca/2011/05/deploying-django-with-nginx-and-gunicorn
http://tech.agilitynerd.com/configuring-runit-for-gunicorn-and-django-ins

The configuration of the webserver must include the downloads url. Nginx example:

    location /downloads {
        # LIST_DIR_ROOT is in settings.py
        alias /home/openwrt/downloads;
        autoindex on;
    }

There are some specific django settings for this app that you must set. Installing
in openwrt's home directory may look like this:

MAKE_SNAPSHOT = "bash /home/openwrt/altermeshfc/bin/make_snapshot"
NETWORK_INCLUDES_PATH = "/home/openwrt/network_includes"
LIST_DIR_ROOT = "/home/openwrt/downloads/"

# set a default profile to use as based_on when creating a new profile
DEFAULT_PROFILE_SLUG = 'altermesh-nodo'


Installing & configuring ImageBuilder
-------------------------------------

TODO
====

* Handle jobs when application crash or stops.

Authors and Contributors
========================

* Santiago Piccinini <spiccinini at altermundi.net> (Main developer)
* Guido Iribarren
* Nico Echaniz
