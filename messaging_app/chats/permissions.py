from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to allow only participants of a conversation to access it.
    """

    def has_permission(self, request, view):
        # Allow access only if the user is authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # 1. Check if the object is a Conversation
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        
        # 2. Check if the object is a Message
        # We trace the message back to its conversation to check participation
        if hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()

        return False
    
    
    
    