import sys
from django.core.management.base import BaseCommand
from altermeshfc.firmcreator.models import FwProfile


class Command(BaseCommand):
    args = 'profile_slug path'
    help = 'Load profile from disk'

    def handle(self, *args, **options):
        if len(args) != 2:
            print("invalid arguments, see help with --help")
            sys.exit(1)
        slug, path = args
        profile = FwProfile.objects.get(slug=slug)
        profile.load_includes_from_disk(path)
        profile.save()
