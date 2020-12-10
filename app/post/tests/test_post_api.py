from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Post, Tag, Topic

from post.serializers import PostSerializer, PostDetailSerializer


POSTS_URL = reverse('post:post-list')


def detail_url(post_id):
    """Return post detail URL"""
    return reverse('post:post-detail', args=[post_id])


def sample_tag(user, title='Tech'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, title=title)


def sample_topic(user, title='Random Topic'):
    """Create and return a sample topic"""
    return Topic.objects.create(user=user, title=title)


def sample_post(user, **params):
    """Create and return a sample post"""
    defaults = {
        'title': 'Sample post title',
        'content': 'Type what would you like to say'
    }
    defaults.update(params)

    return Post.objects.create(user=user, **defaults)


class PublicPostApiTest(TestCase):
    """Test unauthenticated post API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(POSTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePostApiTest(TestCase):
    """Test unauthorized post API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@example.com',
            'pass5555'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_post(self):
        """Test retrieving a list of posts"""
        sample_post(user=self.user)
        sample_post(user=self.user)

        res = self.client.get(POSTS_URL)

        posts = Post.objects.all().order_by('id')
        serializer = PostSerializer(posts, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_post_limited_to_user(self):
        """Test retrieving post for user"""
        user2 = get_user_model().objects.create_user(
            'other@example.com',
            'pass4555'
        )
        sample_post(user=user2)
        sample_post(user=self.user)

        res = self.client.get(POSTS_URL)

        posts = Post.objects.filter(user=self.user)
        serializer = PostSerializer(posts, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_viewing_post_detail(self):
        """Test viewing post detail"""
        post = sample_post(user=self.user)
        post.tags.add(sample_tag(user=self.user))
        post.topics.add(sample_topic(user=self.user))

        url = detail_url(post.id)
        res = self.client.get(url)

        serializer = PostDetailSerializer(post)
        self.assertEqual(res.data, serializer.data)
