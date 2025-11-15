from django.urls import path, include
# from rest_framework.routers import DefaultRouter
from rest_framework import routers
from . import views

# Create a router and register our viewsets with it.
router = routers.DefaultRouter()
router.register(r'conversations', views.ConversationViewSet, basename='conversation')
router.register(r'messages', views.MessageViewSet, basename='message')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]

