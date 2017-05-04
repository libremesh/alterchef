# License

This software is licensed under AGPL.

# Installation and configuration

This app is composed of two different parts, the web frontend (made using [Django](https://www.djangoproject.com/)) and the binary firmware images builder (bash scripts that use [OpenWrt](https://openwrt.org/)'s [Image Builder](https://wiki.openwrt.org/doc/howto/obtain.firmware.generate)).

## Local installation for development

Clone or download the source code (i.e. to the _alterchef_ folder):

```
git clone https://github.com/libremesh/alterchef.git
```

If you want to run Chef using the Django development server first install Chef's dependencies in a virtual environment:

```
mkvirtualenv alterchef
cd alterchef
pip install -r requirements.txt
```

Initialize the database and create the _chef_ administrative user:

```
cd altermeshfc
./manage.py migrate --settings=altermeshfc.dev_settings
./manage.py createsuperuser --settings=altermeshfc.dev_settings
```

Then run Django's web server:

```
./manage.py runserver --settings=altermeshfc.dev_settings
```

If everything went good, you can now visit your Chef instance at http://127.0.0.1:8000/

Next time you don't need to create the virtual environment again, just activate it by typing `workon alterchef` and run the web server again.

## Installing & configuring the web app

To install the web app dependencies run `pip install -r requeriments.txt` inside a virtualenv. Then you can follow any howto that explains deploying Django. We recomend using gunicorn, nginx and runit. Here are some links:

- http://honza.ca/2011/05/deploying-django-with-nginx-and-gunicorn
- http://tech.agilitynerd.com/configuring-runit-for-gunicorn-and-django-ins

The configuration of the webserver must include the downloads url. Nginx example:

```
location /downloads {
    # LIST_DIR_ROOT is in settings.py
    alias /home/openwrt/downloads;
    autoindex on;
}
```

There are some specific Django settings for this app that you must set. Installing in openwrt's home directory may look like this:

```
MAKE_SNAPSHOT = "bash /home/openwrt/altermeshfc/bin/make_snapshot" NETWORK_INCLUDES_PATH = "/home/openwrt/network_includes" LIST_DIR_ROOT = "/home/openwrt/downloads/"
```

## set a default profile to use as based_on when creating a new profile

```
DEFAULT_PROFILE_SLUG = 'altermesh-nodo'
```

## Installing & configuring ImageBuilder

# TODO

- Handle jobs when application crash or stops.

# Authors and Contributors

- Santiago Piccinini \<spiccinini at altermundi.net\> (Main developer)
- Guido Iribarren
- Nico Echaniz
- [Pablo Castellano](https://github.com/PabloCastellano)
