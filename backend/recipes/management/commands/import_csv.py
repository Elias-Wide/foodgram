import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


DATA_ROOT = os.path.join(settings.BASE_DIR, 'data')
TABLES_DICT = {
    Ingredient: 'ingredients.csv',
    Tag: 'tags.csv',
}


class Command(BaseCommand):
    """Команда импорта данных из csv-файла.
    Создаются соответствующие модели в бд.
    """
    help = 'загрузка данных их CSV файла в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            'filename',
            default='ingredients.csv',
            nargs='?',
            type=str
        )

    def handle(self, *args, **options):
        for model_class, filename in TABLES_DICT.items():
            csv_file_path = os.path.join(DATA_ROOT, filename)
            row_list = []
            with open(
                csv_file_path, 'r', encoding='utf8', newline=''
            ) as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        row_list.append(model_class(**row))
                    except Exception as error:
                        self.stdout.write(f'Ошибка в строке {row}. {error}')
            model_class.objects.bulk_create(row_list)
            self.stdout.write(
                self.style.SUCCESS(f'Данные {filename} УСПЕШНО загружены')
            )
