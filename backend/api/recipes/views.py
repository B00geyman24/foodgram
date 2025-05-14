from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from foodgram_backend.settings import SHOPPING_CART
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingList, Tag)
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.serializers import RecipeSerializer

from ..filters import RecipeFilter
from ..pagination import RecipePaginator
from ..permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeReadSerializer, TagSerializer)


BASE_URL = 'https://foodgram.example.org'


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter, )
    search_fields = ('^name', )


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    permission_classes = (AllowAny, )
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = RecipePaginator
    permission_classes = (IsAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'create', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def add_to_list(self, request, model, recipe, error_message):
        if not model.objects.filter(user=request.user, recipe=recipe).exists():
            model.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeSerializer(recipe, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': error_message},
                        status=status.HTTP_400_BAD_REQUEST)

    def remove_from_list(self, request, model,
                         recipe, success_message, error_message):
        item = model.objects.filter(user=request.user, recipe=recipe).first()
        if item:
            item.delete()
            return Response({'detail': success_message},
                            status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': error_message},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def add_to_favorites(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        return self.add_to_list(request,
                                Favorite, recipe, 'Рецепт уже в избранном.')

    @action(detail=True, methods=['delete'],
            permission_classes=(IsAuthenticated,))
    def remove_from_favorites(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        return self.remove_from_list(request,
                                     Favorite, recipe,
                                     'Рецепт успешно удален из избранного.',
                                     'Рецепт не найден в избранном.')

    @action(detail=True, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def add_to_shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        return self.add_to_list(request, ShoppingList,
                                recipe, 'Рецепт уже в списке покупок.')

    @action(detail=True, methods=['delete'],
            permission_classes=(IsAuthenticated,))
    def remove_from_shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        return self.remove_from_list(request, ShoppingList,
                                     recipe,
                                     'Рецепт удален из списка покупок.',
                                     'Рецепт не найден в списке покупок.')

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, **kwargs):
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__shoppinglist__user=request.user)
            .values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list('ingredient__name', 'total_amount',
                         'ingredient__measurement_unit')
        )
        file_list = []
        [file_list.append(
            '{} - {} {}.'.format(*ingredient)) for ingredient in ingredients]
        file = HttpResponse('Cписок покупок:\n' + '\n'.join(file_list),
                            content_type='text/plain')
        file['Content-Disposition'] = (f'attachment; filename={SHOPPING_CART}')
        return file

    @action(
        methods=['get'],
        detail=True,
        url_path='get-link',
        url_name='get-link',
        permission_classes=(AllowAny,)
    )
    def get_link(self, request, pk=None):
        """Получение короткой ссылки на рецепт"""
        recipe = self.get_object()
        short_link = f"{BASE_URL}/s/{recipe.id}"
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)
