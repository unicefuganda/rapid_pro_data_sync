from optparse import make_option
from django.core.management import BaseCommand
from contact_sync.models import Sync
from contact_sync.utils import MissingArgumentError

__author__ = 'kenneth'


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("-a", "--app", dest="a"),

    )

    def handle(self, *args, **options):
        if not options['a']:
            raise MissingArgumentError("No --app argument given. Please add --app=app_name")
        s = Sync.objects.get(app_name=options['a'])
        s.sync()