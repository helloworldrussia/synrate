from django.core.management.base import BaseCommand

from synrate_main.models import OffersCounter

class Command(BaseCommand):

    def handle(self, *args, **options):
        OffersCounter.reaculculate_all_counts()
