"""Test for the ingredients"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    """Create and return an ingredient detail url."""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email='test@example.com', password='testpass123'):
    """Create and return user"""
    return get_user_model().objects.\
        create_user(email=email, password=password)  # type: ignore


def create_recipe(user, **params):  # helper function
    """Create and return a sample recipe"""

    defaults = {
        'title': 'sample for recipe title',
        'time_minutes': 32,
        'price': Decimal('43.2'),
        'description': 'good food test',
        'link': 'http://recipetest.com/recipe.pdf',
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


class PublicIngredientApiTest(TestCase):
    """Test unauthenticated API request"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth required for retrieving ingredients"""

        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTest(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving a list of ingredients"""
        Ingredient.objects.create(user=self.user, name='kale')
        Ingredient.objects.create(user=self.user, name='Vanilla')

        response = self.client.get(INGREDIENTS_URL)

        ingredient = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredient, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)  # type: ignore

    def test_ingredients_limited_to_user(self):
        """Test list of ingredients is limited to authenticated user."""
        user_new = create_user(email='newuser@example.com')
        Ingredient.objects.create(user=user_new, name='Salt')
        ingredient = Ingredient.objects.create(user=self.user, name='Pepper')

        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # type: ignore
        self.assertEqual(response.data[0]['name'],  # type: ignore
                         ingredient.name)
        self.assertEqual(response.data[0]['id'], ingredient.id)  # type: ignore

    def test_update_ingredient(self):
        """Test updating an ingredient"""
        ingredient = Ingredient.objects.create(user=self.user, name='Cilantro')
        payload = {'name': 'Coriander'}
        url = detail_url(ingredient_id=ingredient.id)  # type: ignore
        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test deleting an ingredient"""
        ingredient = Ingredient.objects.create(user=self.user, name='Lettuce')

        url = detail_url(ingredient_id=ingredient.id)  # type: ignore
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        ingredient = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredient.exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        """Test listing ingredient by those assigned to recipe"""
        recipe = create_recipe(user=self.user, title='Salad')
        ingredient1 = Ingredient.objects.create(user=self.user, name='Lemon')
        ingredient2 = Ingredient.objects.create(user=self.user, name='Oil')

        recipe.ingredients.add(ingredient1)

        response = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        s1 = IngredientSerializer(ingredient1)
        s2 = IngredientSerializer(ingredient2)

        self.assertIn(s1.data, response.data)  # type: ignore
        self.assertNotIn(s2.data, response.data)  # type: ignore

    def test_filtered_ingredients_unique(self):
        """Test filtered ingredients returns a unique list."""
        recipe = create_recipe(user=self.user, title='Salad')
        recipe2 = create_recipe(user=self.user, title='Beef')
        ing1 = Ingredient.objects.create(user=self.user, name='Oil')
        Ingredient.objects.create(user=self.user, name='Lemon')

        recipe.ingredients.add(ing1)
        recipe2.ingredients.add(ing1)

        response = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(response.data), 1)  # type: ignore
