from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    TagViewSet,
    RecipeViewSet,
    download_shopping_list,
    get_short_link
)


router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'tags', TagViewSet)
router.register(r'recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('recipes/download_shopping_cart/',
         download_shopping_list,
         name='download_shopping_list'),
    path('recipes/<int:id>/get-link/', get_short_link, name='get_short_link'),
]
