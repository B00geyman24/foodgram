from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
    FavoriteViewSet,
    ShoppingListViewSet
)


router = DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'favorites', FavoriteViewSet)
router.register(r'shopping_list', ShoppingListViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
