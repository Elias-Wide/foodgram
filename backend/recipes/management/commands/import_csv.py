import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


DATA_ROOT = os.path.join(settings.BASE_DIR, 'data')
model_class = Ingredient


class Command(BaseCommand):
    help = 'Load data from CSV files into database'

    def add_arguments(self, parser):
        parser.add_argument(
            'filename',
            default='ingredients.csv',
            nargs='?',
            type=str
        )

    def handle(self, *args, **options):
        csv_file_path = os.path.join(DATA_ROOT, 'ingredients.csv')
        row_list = []
        with open(csv_file_path, 'r', encoding='utf8', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                try:
                    name, measurement_unit = row
                    row_list.append(
                        model_class(
                            name=name,
                            measurement_unit=measurement_unit
                        )
                    )
                except Exception as error:
                    self.stdout.write(
                        f'Ошибка в строке {row}. {error}')
            model_class.objects.bulk_create(row_list)
            self.stdout.write(self.style.SUCCESS('Данные УСПЕШНО загружены'))
