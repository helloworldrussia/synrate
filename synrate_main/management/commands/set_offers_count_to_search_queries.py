import datetime
from tqdm import tqdm
from django.core.management.base import BaseCommand

from synrate_main.models import SearchQuery, Offer


class Command(BaseCommand):

    def handle(self, *args, **options):
        for search_query in tqdm(SearchQuery.objects.all()):
            phrase = search_query.phrase
            year_ago_date = datetime.datetime.now() - datetime.timedelta(days=365)
            queryset = Offer.objects.filter(offer_start_date__gte=year_ago_date).order_by('-offer_start_date')
            words = phrase.replace('.', '').replace(',', '').split(' ')

            additional_data_queryset = queryset
            words = [word  for word in words if word!='']
            for word in words:
                additional_data_queryset = additional_data_queryset.filter(additional_data__icontains=word)
            name_queryset = queryset
            for word in words:
                name_queryset = name_queryset.filter(name__icontains=word)

            queryset = name_queryset | additional_data_queryset
            search_query.offers_count = queryset.count()
            if search_query.offers_count > 0:
                search_query.is_active = True
            search_query.save()

