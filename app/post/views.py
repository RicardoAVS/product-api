from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
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

    def _params_to_int(self, query_string):
        """Convert a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in query_string.split(',')]

    def get_queryset(self):
        """Retrieve the posts for the authenticated user"""
        tags = self.request.query_params.get('tags')
        topics = self.request.query_params.get('topics')
        queryset = self.queryset

        if tags:
            tag_ids = self._params_to_int(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if topics:
            topic_ids = self._params_to_int(topics)
            queryset = queryset.filter(topics__id__in=topic_ids)

        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""

        if self.action == 'retrieve':
            return serializers.PostDetailSerializer
        elif self.action == 'upload_image':
            return serializers.PostImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new post"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a post"""
        post = self.get_object()
        serializer = self.get_serializer(
            post,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
