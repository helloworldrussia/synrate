import xlrd
from django.core.management.base import BaseCommand
from synrate_main.models import SearchQuery


class Command(BaseCommand):

    def handle(self, *args, **options):
        file_path = options['file']
        workbook = xlrd.open_workbook(file_path)
        # "/Users/stirlits/Downloads/phrases.xls"
        worksheet = workbook.sheet_by_index(0)

        # for i in range(0, worksheet.nrows + 1):
        for i in range(0, 10):
            phrase = worksheet.cell_value(i, 0)
            slug = worksheet.cell_value(i, 1)
            if phrase and slug:
                search_query, created = SearchQuery.objects.get_or_create(slug=slug)
                if created:
                    search_query.phrase = phrase
                    search_query.save()
                    print(f"created { search_query.phrase } - { search_query.slug }")
                else:
                    print(f"! skipped { search_query.phrase } - { search_query.slug }")

    def add_arguments(self, parser):
        parser.add_argument(
            'file',
            action='store', 
            default=False,
            type=str,
            help='Путь до файла'
        )