from django.urls import include, path

from .users.urls import router

urlpatterns = [
    path('', include('api.recipes.urls')),
    path('', include(router.urls)),
    path(r'auth/', include('djoser.urls.authtoken')),
]
