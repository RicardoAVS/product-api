from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Topic

from . import serializers


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    """Manage tags in database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    def get_queryset(self):
        """Return object for the authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-title')

    def perform_create(self, serializer):
        """Create a new tag"""
        serializer.save(user=self.request.user)


class TopicViewSet(viewsets.GenericViewSet,
                   mixins.ListModelMixin,
                   mixins.CreateModelMixin):
    """Manage topics in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Topic.objects.all()
    serializer_class = serializers.TopicSerializer

    def get_queryset(self):
        """Return objects for the current authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-title')

    def perform_create(self, serializer):
        """Create a new topic"""
        serializer.save(user=self.request.user)
