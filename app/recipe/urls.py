"""URL mappings for the recipe app"""


from django.urls import path, include

from rest_framework.routers import DefaultRouter

from recipe import views

router = DefaultRouter()

router.register('recipes', views.RecipeViewSet)

app_name = 'recipe'  # for testing url in reverse in test file

urlpatterns = [
    path('', include(router.urls))
]