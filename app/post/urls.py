from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('topic', views.TopicViewSet)
router.register('posts', views.PostViewSet)

app_name = 'post'

urlpatterns = [
    path('', include(router.urls))
]
