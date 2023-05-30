"""
Test for the tags API.
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """Create and return a tag detail url."""
    return reverse('recipe:tag-detail', args=[tag_id])


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


def create_user(email='user@examle.com', password='userexampletest123'):
    """Create and return user"""
    return get_user_model().objects.\
        create_user(email=email, password=password)  # type: ignore


class PublicTagsApiTest(TestCase):
    """Test unauthenticated API request."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving tags."""
        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTest(TestCase):
    """Test authenticated API request."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving a list of tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        response = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)  # type: ignore

    def test_tags_limited_to_user(self):
        """Test list of tags is limited to authenticated user."""
        user2 = create_user(email='user2@example.com')
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #  we only expect to see one tag returned in the response
        self.assertEqual(len(response.data), 1)  # type: ignore
        self.assertEqual(response.data[0]['name'], tag.name)  # type: ignore
        self.assertEqual(response.data[0]['id'], tag.id)  # type: ignore

    def test_update_tag(self):
        """Test updating a tag"""
        tag = Tag.objects.create(user=self.user, name='Before Dinner')
        payload = {'name': 'Ice Cream'}
        url = detail_url(tag_id=tag.id)  # type: ignore
        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test deleting a tag"""
        tag = Tag.objects.create(user=self.user, name='Drink')

        url = detail_url(tag_id=tag.id)  # type: ignore
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_recipes(self):
        """Test listing tags by those assigned to recipe"""
        recipe = create_recipe(user=self.user, title='Salad')
        tag1 = Tag.objects.create(user=self.user, name='Lemon')
        tag2 = Tag.objects.create(user=self.user, name='Oil')

        recipe.tags.add(tag1)

        response = self.client.get(TAGS_URL, {'assigned_only': 1})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)

        self.assertIn(s1.data, response.data)  # type: ignore
        self.assertNotIn(s2.data, response.data)  # type: ignore

    def test_filtered_tags_unique(self):
        """Test filtered tags returns a unique list."""
        recipe = create_recipe(user=self.user, title='Salad')
        recipe2 = create_recipe(user=self.user, title='Beef')
        tag1 = Tag.objects.create(user=self.user, name='Oil')
        Tag.objects.create(user=self.user, name='Lemon')

        recipe.tags.add(tag1)
        recipe2.tags.add(tag1)

        response = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(response.data), 1)  # type: ignore
