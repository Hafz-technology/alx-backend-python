from django.shortcuts import render


from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

User = get_user_model()


class ConversationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows conversations to be viewed or created.
    
    - list: Returns a list of conversations for the authenticated user.
    - create: Creates a new conversation, adding the authenticated user
              and the users specified in 'participant_ids'.
    - retrieve: Gets the details of a specific conversation, including
                all messages and participants.
    """
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all conversations
        for the currently authenticated user.
        """
        user = self.request.user
        # We use .distinct() to avoid duplicate conversations in the list
        return Conversation.objects.filter(participants=user).distinct()

    # Note: We don't need to override perform_create here.
    # The ConversationSerializer is designed to get the request.user
    # from the context, which ModelViewSet provides automatically,
    # and handles adding the creator to the participants list.


class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows messages to be viewed or sent.
    
    - list: Returns messages from conversations the user is part of.
    - create: Sends a new message to a specific conversation.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all messages in
        conversations the user is part of.
        
        The ordering (e.g., oldest or newest first) is
        controlled by the 'ordering' Meta option in the Message model.
        """
        user = self.request.user
        # Filter messages based on conversations the user is a participant in
        return Message.objects.filter(conversation__participants=user)

    def perform_create(self, serializer):
        """
        Set the sender of the message to the currently authenticated user
        and validate that the user is part of the conversation.
        """
        # The serializer validation ensures 'conversation' is a valid object
        conversation = serializer.validated_data['conversation']
        user = self.request.user

        # Security check: Ensure the user is a participant
        if user not in conversation.participants.all():
            raise PermissionDenied(
                {"detail": "You are not a participant in this conversation."}
            )
        
        # Set the sender and save the message
        serializer.save(sender=user)
