from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to view it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        # BUT only if the user is a participant.
        
        # Check if the object is a Conversation
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        
        # Check if the object is a Message
        if hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()

        return False
    
    
    
    