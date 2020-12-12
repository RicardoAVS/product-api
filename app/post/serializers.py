from rest_framework import serializers

from core.models import Tag, Topic, Post


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'title')
        read_only_fields = ('id',)


class TopicSerializer(serializers.ModelSerializer):
    """Serializer for topic objects"""

    class Meta:
        model = Topic
        fields = ('id', 'title')
        read_only_fields = ('id',)


class PostSerializer(serializers.ModelSerializer):
    """Serialize a post"""
    topics = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Topic.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'date', 'topics', 'tags')
        read_only_fields = ('id',)


class PostDetailSerializer(PostSerializer):
    """Serializer a post detail"""
    topics = TopicSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)


class PostImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to post"""

    class Meta:
        model = Post
        fields = ('id', 'image')
        read_only_fields = ('id',)
