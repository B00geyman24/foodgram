from rest_framework import viewsets, permissions, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from users.models import User
from recipes.models import Tag, Recipe, ShoppingList, Favorite
from django.http import HttpResponse
from rest_framework.response import Response
from django.template.loader import render_to_string
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    TagSerializer,
    RecipeSerializer,
    RecipeCreateSerializer,
    SetAvatarSerializer
)


@api_view(['GET'])
def get_short_link(request, id):
    try:
        recipe = Recipe.objects.get(id=id)
        short_link = f"http://yourdomain.com/recipes/{recipe.id}/"
        return Response({'short_link': short_link}, status=status.HTTP_200_OK)
    except Recipe.DoesNotExist:
        return Response(
            {'detail': 'Recipe not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@permission_classes([IsAuthenticated])
def download_shopping_list(request):
    user = request.user
    shopping_list = ShoppingList.objects.filter(user=user)
    context = {
        'shopping_list': shopping_list,
    }
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = (
        'attachment; filename="shopping_list.txt"')
    response.write(render_to_string('shopping_list.txt', context))
    return response


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @action(detail=True,
            methods=['get'],
            permission_classes=[permissions.AllowAny])
    def profile(self, request, pk=None):
        user = self.get_object()
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @action(detail=False,
            methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False,
            methods=['put'],
            permission_classes=[permissions.IsAuthenticated])
    def avatar(self, request):
        user = request.user
        serializer = SetAvatarSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['delete'],
            permission_classes=[permissions.IsAuthenticated])
    def remove_avatar(self, request):
        user = request.user
        user.avatar.delete()
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['author', 'tags__slug']
    search_fields = ['name']

    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited == '1':
            queryset = queryset.filter(favorited_by__user=user)

        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        if is_in_shopping_cart == '1':
            queryset = queryset.filter(shopping_lists__user=user)

        return queryset

    def perform_update(self, serializer):
        if self.request.user != serializer.instance.author:
            raise permissions.PermissionDenied(
                "У вас нет прав на редактирование этого рецепта."
            )
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance.author:
            raise permissions.PermissionDenied(
                "У вас нет разрешения на удаление этого рецепта."
            )
        instance.delete()

    @action(detail=True, methods=['post'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
            return Response(
                {'detail': 'Recipe already in favorites'},
                status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.create(user=request.user, recipe=recipe)
        return Response(
            {'id': recipe.id,
             'name': recipe.name,
             'image': recipe.image.url,
             'cooking_time': recipe.cooking_time},
            status=status.HTTP_201_CREATED)

    @action(detail=True,
            methods=['delete'],
            permission_classes=[permissions.IsAuthenticated])
    def unfavorite(self, request, pk=None):
        recipe = self.get_object()
        favorite = Favorite.objects.filter(user=request.user, recipe=recipe)
        if favorite.exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'detail': 'Recipe not in favorites'},
            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        if ShoppingList.objects.filter(user=request.user,
                                       recipe=recipe).exists():
            return Response({'detail': 'Recipe already in shopping cart'},
                            status=status.HTTP_400_BAD_REQUEST)
        ShoppingList.objects.create(user=request.user, recipe=recipe)
        return Response(
            {'id': recipe.id,
             'name': recipe.name,
             'image': recipe.image.url,
             'cooking_time': recipe.cooking_time},
            status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'],
            permission_classes=[permissions.IsAuthenticated])
    def remove_from_shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        shopping_list_item = ShoppingList.objects.filter(user=request.user,
                                                         recipe=recipe)
        if shopping_list_item.exists():
            shopping_list_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Recipe not in shopping cart'},
                        status=status.HTTP_400_BAD_REQUEST)
