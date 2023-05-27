""""  test for models ."""
from unittest.mock import patch
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email='test@example.com', password='testuser123'):
    """Create and return new user"""
    return get_user_model().objects.\
        create_user(email=email, password=password)  # type: ignore


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        email = 'test@example.com'
        password = 'testpass123'

        user = get_user_model().objects.create_user(  # type: ignore
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model()\
                .objects.create_user(email, 'sample123')  # type: ignore
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """test that creating a user without an email raises a ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'pass123')  # type: ignore

    def test_create_superuser(self):
        """test that creating a superuser"""
        user = get_user_model().objects.create_superuser(  # type: ignore
            'test@test.com',
            'pass123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating a recipe is successful"""
        user = get_user_model().objects.create_user(  # type: ignore
            email='test@example.com',
            password='testpass1234',
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample Recipe name',
            time_minutes=5,
            price=Decimal('5.60'),
            description='Sample recipe description',
        )
        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test creating a tag is successful"""
        user = create_user()

        tag = models.Tag.objects.create(user=user, name='Tag1')

        self.assertEqual(str(tag), tag.name)

    def test_ingredient(self):
        """Test creating a ingredient is successful"""
        user = create_user()
        ingredient = models.Ingredient.objects.create(
            user=user,
            name='ingredient1'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    # ensure we that we don't have or create any duplicate file name in system.
    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating image path."""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(  # type: ignore
            None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
