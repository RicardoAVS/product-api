from rest_framework import serializers

from core.models import Tag, Topic


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
