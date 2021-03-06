from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@example.com', password='pass5555'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTest(TestCase):

    def test_create_user_with_email_successful(self):
        email = "test@example.com"
        password = "Testpassword555"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the mail for a new user is normalized"""
        email = "test@EXAMPLE.COM"
        user = get_user_model().objects.create_user(email, 'test555')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating email with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, '1234')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test555'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            title='TDD with Python and Django'
        )

        self.assertEqual(str(tag), tag.title)

    def test_topic_str(self):
        topic = models.Topic.objects.create(
            user=sample_user(),
            title='Politics'
        )

        self.assertEqual(str(topic), topic.title)

    def test_post_content_not_empty(self):
        """Test the posts string representation"""
        post = models.Post.objects.create(
            user=sample_user(),
            title='AWS:reinvent conference',
            content=''
        )

        self.assertTrue(post.title, '')

    @patch('uuid.uuid4')
    def test_post_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.post_image_file_path(None, 'image.jpg')

        exp_path = f'uploads/post/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)
