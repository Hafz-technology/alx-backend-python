from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet

router = DefaultRouter()

# Add basename='conversation'
router.register(r'conversations', ConversationViewSet, basename='conversation')

# Add basename='message'
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
]


