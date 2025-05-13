import json
import os

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из data/ingredients.json'

    def handle(self, *args, **kwargs):
        file_path = os.path.join('data', 'ingredients.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                Ingredient.objects.get_or_create(name=item['name'])
        self.stdout.write(self.style.SUCCESS('Ингредиенты успешно загружены!'))
