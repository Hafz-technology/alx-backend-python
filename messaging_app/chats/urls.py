

from django.urls import path, include
from rest_framework import routers
from rest_framework_nested.routers import NestedDefaultRouter
from . import views

# Main router for conversations
router = routers.DefaultRouter()
router.register(r'conversations', views.ConversationViewSet, basename='conversation')

# Nested router for messages within conversations
# This creates URLs like: /conversations/{conversation_pk}/messages/
conversations_router = NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', views.MessageViewSet, basename='conversation-messages')

# The API URLs are now determined automatically by the routers
urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversations_router.urls)),
]
