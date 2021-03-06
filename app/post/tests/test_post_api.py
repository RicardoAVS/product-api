import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Post, Tag, Topic

from post.serializers import PostSerializer, PostDetailSerializer


POSTS_URL = reverse('post:post-list')


def image_upload_url(post_id):
    """Return URL for post image uploaded"""
    return reverse('post:post-upload-image', args=[post_id])


def detail_url(post_id):
    """Return post detail URL"""
    return reverse('post:post-detail', args=[post_id])


def sample_tag(user, title='Tech'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, title=title)


def sample_topic(user, title='Facebook'):
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

    def test_create_basic_post(self):
        """Test creating post"""
        payload = {
            'title': "Installation of dependencies fail -Docker wrapper...",
            'content': 'The LTRpred package requires six command-line',
        }

        res = self.client.post(POSTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        post = Post.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(post, key))

    def test_create_post_with_tags(self):
        """Test creating a post with tags"""
        tag1 = sample_tag(user=self.user, title='Tech')
        tag2 = sample_tag(user=self.user, title='History')
        payload = {
            'title': '1990: WorldWideWeb, the first Web browser',
            'tags': [tag1.id, tag2.id],
            'content': 'Of all the technologies that changed our lives,\n'
            'perhaps the most profound of the last 50 years has been the web'
        }
        res = self.client.post(POSTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        posts = Post.objects.get(id=res.data['id'])
        tags = posts.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def tesst_create_post_with_topic(self):
        """Test creating post with topics"""
        topics1 = sample_topic(user=self.user, title='Twitter')
        topics2 = sample_topic(user=self.user, title='Facebook')

        payload = {
            'title': 'Live grows up with two persons broadcasts...',
            'topics': [topics1, topics2],
            'content': 'Today at VidCon Facebook pre-announced three...'
        }
        res = self.client.post(POSTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        post = Post.objects.get(id=res.data.get['id'])
        topics = post.topics.all()
        self.assertEqual(len(topics), 2)
        self.assertIn(topics1, topics)
        self.assertIn(topics2, topics)

    def test_partial_update_post(self):
        """Test updating a post with patch"""
        post = sample_post(user=self.user)
        post.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, title='Movies')

        payload = {
            'title': 'Best movie of the year Interstellar',
            'tags': [new_tag.id]
        }
        url = detail_url(post.id)
        self.client.patch(url, payload)

        post.refresh_from_db()
        self.assertEqual(post.title, payload['title'])
        tags = post.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_post(self):
        """Test updating a post with a PUT"""
        post = sample_post(user=self.user)
        post.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'Spaghetti Carbonara',
            'content': 'Recipe for a delicious spaghetti...'
        }
        url = detail_url(post.id)
        self.client.put(url, payload)

        post.refresh_from_db()
        self.assertEqual(post.title, payload['title'])
        self.assertEqual(post.content, payload['content'])
        tags = post.tags.all()
        self.assertEqual(len(tags), 0)


class PostImageUploadTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@example.com',
            'pass5555'
        )
        self.client.force_authenticate(self.user)
        self.post = sample_post(user=self.user)

    def tearDown(self):
        self.post.image.delete()

    def test_upload_image_to_post(self):
        """TEst uploading an image to post"""
        url = image_upload_url(self.post.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.post.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.post.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.post.id)
        res = self.client.post(
            url, {'image': 'invalidimg'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
