from django.contrib import admin
from .models import (
    Tag,
    Ingredient,
    Recipe,
    Favorite,
    ShoppingList,
    RecipeIngredient
)


class BaseAdminSettings(admin.ModelAdmin):
    """Базовая кастомизация админ панели."""
    empty_value_display = '-пусто-'
    list_filter = ('author', 'name', 'tags')


class TagAdmin(BaseAdminSettings):
    """
    Управление тегами.
    """
    list_display = ('name', 'slug')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)


class IngredientAdmin(BaseAdminSettings):
    """
    Управление ингредиентами.
    """
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


class RecipeAdmin(BaseAdminSettings):
    """
    Управление рецептами.
    """
    list_display = ('name', 'author', 'added_in_favorites')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags')
    readonly_fields = ('added_in_favorites',)
    filter_horizontal = ('tags',)

    def added_in_favorites(self, obj):
        return obj.favorites.all().count()

    added_in_favorites.short_description = 'Количество добавлений в избранное'


class RecipeIngredientAdmin(admin.ModelAdmin):
    """
    Управление ингридиентами в рецептах.
    """
    list_display = ('ingredient', 'amount',)
    list_filter = ('ingredient',)


class FavoriteAdmin(admin.ModelAdmin):
    """
    Управление избранными рецептами.
    """
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user', 'recipe')


class ShoppingListAdmin(admin.ModelAdmin):
    """
    Управление избранными рецептами.
    """
    list_display = ('recipe', 'user')
    list_filter = ('recipe', 'user')
    search_fields = ('user',)


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
