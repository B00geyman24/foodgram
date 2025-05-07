from django.core.management.base import BaseCommand
from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Load initial data for ingredients and tags'

    def handle(self, *args, **kwargs):
        # Создаем ингредиенты
        ingredients = [
            {'name': 'Соль', 'measurement_unit': 'г'},
            {'name': 'Сахар', 'measurement_unit': 'г'},
        ]
        for ingredient_data in ingredients:
            Ingredient.objects.get_or_create(**ingredient_data)

        # Создаем теги
        tags = [
            {'name': 'Завтрак', 'slug': 'breakfast'},
            {'name': 'Обед', 'slug': 'lunch'},
            {'name': 'Ужин', 'slug': 'dinner'},
        ]
        for tag_data in tags:
            Tag.objects.get_or_create(**tag_data)

        self.stdout.write(
            self.style.SUCCESS('Initial data loaded successfully'))
