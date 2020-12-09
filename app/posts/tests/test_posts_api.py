from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Topic

from posts.serializers import TopicSerializer


TOPICS_URL = reverse('posts:topic-list')


class PublicTopicsApiTests(TestCase):
    """Test the publicly available topics API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access"""
        res = self.client.get(TOPICS_URL)

        self.assertEquals(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTopicApiTests(TestCase):
    """Test that topics can be retrieve be authorized user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@example.com',
            'passtest'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_topic_list(self):
        """Test a list of topics"""
        Topic.objects.create(user=self.user, title='James')
        Topic.objects.create(user=self.user, title='Animals')

        res = self.client.get(TOPICS_URL)

        topics = Topic.objects.all().order_by('-title')
        serializer = TopicSerializer(topics, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_topics_limited_to_user(self):
        """Test that topics for the authenticated user are returned"""
        user2 = get_user_model().objects.create_user(
            'another@examplemail.com',
            'anotherpass'
        )
        Topic.objects.create(user=user2, title='Games')
        topic = Topic.objects.create(user=self.user, title='Sports')

        res = self.client.get(TOPICS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['title'], topic.title)

    def test_create_topic_successful(self):
        """Test creating a new topic"""
        payload = {'title': 'Tech'}
        self.client.post(TOPICS_URL, payload)
        
        exists = Topic.objects.filter().filter(
            user = self.user,
            title = payload['title']
        ).exists()
        self.assertTrue(exists)

    def test_create_topic_invalid(self):
        """Test creating invalid topic fails"""
        payload = {'title': ''}
        res = self.client.post(TOPICS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
