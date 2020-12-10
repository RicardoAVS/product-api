from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Topic, Post

from . import serializers


class BaseTopicAttrViewSet(viewsets.GenericViewSet,
                           mixins.ListModelMixin,
                           mixins.CreateModelMixin):
    """Base viewset for user owned topic attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-title')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TagViewSet(BaseTopicAttrViewSet):
    """Manage tags in database"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class TopicViewSet(BaseTopicAttrViewSet):
    """Manage topics in the database"""
    queryset = Topic.objects.all()
    serializer_class = serializers.TopicSerializer


class PostViewSet(viewsets.ModelViewSet):
    """Manage posts in the database"""
    serializer_class = serializers.PostSerializer
    queryset = Post.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Retrieve the posts for the authenticated user"""
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""

        if self.action == 'retrieve':
            return serializers.PostDetailSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new post"""
        serializer.save(user=self.request.user)
