from rest_framework import viewsets, permissions
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    # Enforce that only authenticated participants can access
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        # Filter queryset so users only see their own conversations
        return Conversation.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        # Automatically add the creator to the participants list
        conversation = serializer.save()
        conversation.participants.add(self.request.user)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    # Enforce that only authenticated participants can access
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        # Filter messages to only those belonging to conversations the user is in
        return Message.objects.filter(conversation__participants=self.request.user)

    def perform_create(self, serializer):
        # Set the sender to the current user
        serializer.save(sender=self.request.user)
        
        
        
        
        