from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet
from . import views


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(
    r'ingredients', views.IngredientViewSet, basename='ingredients')
router.register(r'tags', views.TagViewSet, basename='tags')
router.register(r'recipes', views.RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path(r'auth/', include('djoser.urls.authtoken')),
]
