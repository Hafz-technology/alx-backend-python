from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Conversation, Message, User
from .serializers import ConversationSerializer, MessageSerializer

# Create your views here.

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

    # Optional: Override create to handle adding participants
    def create(self, request, *args, **kwargs):
        # Implementation depends on how you want to pass participant IDs
        return super().create(request, *args, **kwargs)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def perform_create(self, serializer):
        # Automatically set the sender to the current user if logged in
        # For this exercise, we might need to pass sender_id manually in body
        # depending on auth setup. Here is the standard way:
        serializer.save(sender=self.request.user)
        
        
        
    