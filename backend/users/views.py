from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Subscribe, User
from api.pagination import CustomPaginator
from .serializers import (SetPasswordSerializer, AuthorSubscriptionSerializer,
                          SubscriptionsSerializer,
                          UserCreateSerializer, UserReadSerializer,
                          UserAvatarSerializer)


class UserViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = CustomPaginator

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserReadSerializer
        return UserCreateSerializer

    @action(detail=False, methods=['get'],
            pagination_class=None,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = UserReadSerializer(request.user)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = SetPasswordSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({'detail': 'Пароль успешно изменен!'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,),
            pagination_class=CustomPaginator)
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribing__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(page, many=True,
                                             context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,),)
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['pk'])

        if request.method == 'POST':
            if request.user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST)
            if Subscribe.objects.filter(user=request.user,
                                        author=author).exists():
                return Response({'errors': 'Подписка уже существует.'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = AuthorSubscriptionSerializer(
                author, data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=request.user, author=author)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = Subscribe.objects.filter(user=request.user,
                                                    author=author).first()
            if subscription:
                subscription.delete()
                return Response({'detail': 'Успешная отписка'},
                                status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'errors': 'Подписка не найдена.'},
                                status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put', 'delete'],
            permission_classes=(IsAuthenticated,),
            url_path='me/avatar',
            url_name='me-avatar',)
    def avatar(self, request):
        if request.method == 'PUT':
            if 'avatar' not in request.data:
                return Response(
                    {'detail': 'Поле «Аватар» обязательно для заполнения'},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = UserAvatarSerializer(request.user, data=request.data,
                                              partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({'avatar': request.user.avatar.url},
                                status=status.HTTP_200_OK)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            user = request.user
            if user.avatar:
                user.avatar.delete()
                user.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'detail': 'Аватар не найден.'},
                            status=status.HTTP_404_NOT_FOUND)
